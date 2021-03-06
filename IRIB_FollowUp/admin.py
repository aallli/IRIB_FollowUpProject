from django.urls import path
from django.conf import settings
from django.db.models import Count
from IRIB_Auth.models import Supervisor
from django.db.transaction import atomic
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils import timezone, translation
from django.shortcuts import get_object_or_404
from IRIB_Shared_Lib.admin import BaseModelAdmin
from django.contrib.admin import SimpleListFilter
from jalali_date.admin import ModelAdminJalaliMixin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from .forms import EnactmentAdminForm, get_followup_inline_form
from IRIB_Shared_Lib.utils import get_jalali_filter, to_jalali, format_date, get_model_fullname
from .models import User, Enactment, Session, Subject, Attachment, Member, FollowUp, Group, GroupUser, GroupFollowUp, \
    SessionBase, Attendant


class SupervisorFilter(SimpleListFilter):
    title = _('Supervisor Unit')
    parameter_name = 'supervisor'

    def lookups(self, request, model_admin):
        return [(supervisor.pk, supervisor.name) for supervisor in Supervisor.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(pk__in=FollowUp.objects.filter(actor__supervisor__pk=self.value()).values(
            'enactment__pk')) if self.value() else queryset


class ActorFilter(SimpleListFilter):
    title = _('Supervisor')
    parameter_name = 'actor'

    def lookups(self, request, model_admin):
        return [(actor.pk, actor) for actor in User.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(pk__in=FollowUp.objects.filter(actor__pk=self.value()).values(
            'enactment__pk')) if self.value() else queryset


class AttendantInline(admin.TabularInline):
    model = Attendant
    insert_after_fieldset = _('Important dates')


class MemberInline(admin.TabularInline):
    model = Member
    insert_after_fieldset = _('Important dates')


class SessionInline(ModelAdminJalaliMixin, admin.TabularInline):
    model = Session
    fields = ['_date', 'absents']
    readonly_fields = ['date', 'absents']
    extra = 0

    def get_max_num(self, request, obj=None, **kwargs):
        return Session.objects.filter(session=obj).count()


class GroupUserInline(admin.TabularInline):
    model = GroupUser
    insert_after_fieldset = _('Important dates')


class GroupFollowUpInline(admin.TabularInline):
    model = GroupFollowUp
    max_num = 1
    extra = 1
    template = 'admin/custom/edit_inline/tabular.html'


class AttachmentInline(admin.TabularInline):
    model = Attachment

    def get_readonly_fields(self, request, obj=None):
        if FollowUp.objects.filter(actor=request.user, enactment=obj).count() == 0:
            self.extra = 0
            self.max_num = 0
            return ['description', 'file']
        return self.readonly_fields


@admin.register(Session)
class SessionAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Session
    search_fields = ['session__name', ]
    fields = [('session', '_date'), 'absents']
    list_display = ['session', 'date']
    readonly_fields = ['date', 'absents']
    list_filter = ['session', get_jalali_filter('_date', _('Attended Date'))]
    ordering = ['session__name', '-_date']
    inlines = [AttendantInline]

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_queryset(self, request):
        queryset = super(SessionAdmin, self).get_queryset(request)
        user = request.user

        if user.is_superuser:
            return queryset

        groups = user.get_groups(settings.IRIB_FU_)
        return queryset.filter(session__group__name__in=groups)

    def get_field_queryset(self, db, db_field, request):
        user = request.user
        if not user.is_superuser and db_field.name == 'session':
            groups = user.get_groups(settings.IRIB_FU_)
            queryset = super(SessionAdmin, self).get_field_queryset(db, db_field, request)
            if queryset:
                queryset = queryset.filter(group__name__in=groups)
            return queryset
        return super(SessionAdmin, self).get_field_queryset(db, db_field, request)

    def save_model(self, request, obj, form, change):
        new_session = not obj.pk
        result = super(SessionAdmin, self).save_model(request, obj, form, change)
        if new_session:
            for member in Member.objects.filter(session=obj.session):
                Attendant.objects.get_or_create(user=member.user, session=obj)
        return result

    def report(self, request, pk=None):
        minute = Session.objects.get(pk=pk)
        enactments = Enactment.objects.filter(session=minute)
        context = dict(
            minutes=[{'minute': minute, 'enactments': enactments}],
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now())
        )
        return TemplateResponse(request, 'admin/custom/enactments-list-report.html', context)

    def get_urls(self):
        urls = super(SessionAdmin, self).get_urls()
        return [path('<int:pk>/report/', self.report, name="session-report"), ] + urls


@admin.register(SessionBase)
class SessionBaseAdmin(BaseModelAdmin):
    model = Session
    fields = ['name', 'group', ]
    list_display = ['name', 'group', ]
    search_fields = ['name', ]
    inlines = [MemberInline, SessionInline]
    ordering = ['name']

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_field_queryset(self, db, db_field, request):
        user = request.user
        if not user.is_superuser and db_field.name == 'group':
            groups = user.get_groups(settings.IRIB_FU_)
            return super(SessionBaseAdmin, self).get_field_queryset(db, db_field, request).filter(name__in=groups)
        return super(SessionBaseAdmin, self).get_field_queryset(db, db_field, request)

    def get_queryset(self, request):
        queryset = super(SessionBaseAdmin, self).get_queryset(request)
        user = request.user

        if user.is_superuser:
            return queryset

        groups = user.get_groups(settings.IRIB_FU_)
        return queryset.filter(group__name__in=groups)

    @atomic()
    def save_model(self, request, obj, form, change):
        if obj.pk:
            # Change the correspondent group name
            if 'name' in form.initial:
                try:
                    group = Group.objects.get(name=form.initial['name'])[0]
                    group.name = obj.name
                    group.save()
                except:
                    pass
        else:
            Group.objects.get_or_create(name=obj.name)
        return super(SessionBaseAdmin, self).save_model(request, obj, form, change)

    @atomic()
    def save_formset(self, request, form, formset, change):
        if formset.model._meta.model_name == 'member':
            group = Group.objects.get_or_create(name=formset.instance.name)[0]
            for item in formset.cleaned_data:
                if 'user' in item:
                    GroupUser.objects.get_or_create(group=group, user=item['user'])
        if formset.model._meta.model_name == 'session':
            pass
        return super(SessionBaseAdmin, self).save_formset(request, form, formset, change)


@admin.register(Subject)
class SubjectAdmin(BaseModelAdmin):
    model = Subject
    search_fields = ['name', ]


def get_followup_inline(request):
    class FollowUpInline(ModelAdminJalaliMixin, admin.TabularInline):
        model = FollowUp
        form = get_followup_inline_form(request)
        fields = ['actor', 'supervisor', 'result', 'date']
        readonly_fields = ['supervisor', 'date']

        def get_queryset(self, request):
            queryset = super(FollowUpInline, self).get_queryset(request)
            if request.user.is_superuser or request.user.is_secretary:
                return queryset
            else:
                return queryset.filter(actor=request.user)

        def has_add_permission(self, request, obj):
            user = request.user
            return user.is_superuser or user.is_secretary or user.is_scoped_secretary

        def has_delete_permission(self, request, obj):
            user = request.user
            return user.is_superuser or user.is_secretary or user.is_scoped_secretary

        def get_readonly_fields(self, request, obj=None):
            user = request.user
            if user.is_superuser or user.is_secretary or user.is_scoped_secretary:
                return self.readonly_fields
            else:
                return self.readonly_fields + ['actor']

        def get_formset(self, request, obj=None, **kwargs):
            user = request.user
            if user.is_superuser or user.is_secretary or user.is_scoped_secretary:
                self.extra = 1
                self.max_num = 20
            else:
                self.extra = 0
                self.max_num = 0

            return super(FollowUpInline, self).get_formset(request, obj, **kwargs)

    return FollowUpInline


@admin.register(Attachment)
class AttachmentAdmin(BaseModelAdmin):
    model = Attachment
    fields = ['description', 'file', 'enactment']
    search_fields = ['description', 'file',
                     'enactment__session__session__name', 'enactment__subject__name',
                     'enactment__assigner__name', 'enactment__description', 'enactment__result',
                     'enactment__second_supervisor__name', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enactment" and not (request.user.is_superuser or request.user.is_secretary):
            queryset = Enactment.objects.filter(follow_grade=1)
            kwargs["queryset"] = queryset.filter(
                session__session__pk__in=Member.objects.filter(user=request.user).values('session'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fieldsets = (
        (_('Session info'), {
            'fields': (('session', 'session_date', 'session_absents'), 'session_presents',)}),
        (_('Enactment Info'), {
            'fields': (('row', 'review_date', 'assigner', 'subject'), ('_type', 'description'))}),
    )

    list_display = ['row', 'type', 'session', 'session_date', 'review_date', 'status', 'subject',
                    'description_short']
    list_filter = ['_type',
                   get_jalali_filter('_review_date', _('Review Date')),
                   get_jalali_filter('session___date', _('Assignment Date')),
                   ActorFilter, SupervisorFilter, 'session__session', 'subject', 'assigner']
    search_fields = ['session__session__name', 'subject__name', 'description', 'assigner__first_name',
                     'assigner__last_name', 'id']
    readonly_fields = ['row', 'type', 'description_short', 'review_date', 'session_presents', 'session_absents',
                       'status', 'session_date']
    form = EnactmentAdminForm

    def status(self, obj):
        return obj.status_colored()

    status.admin_order_field = 'status'
    status.short_description = _('Status')

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_field_queryset(self, db, db_field, request):
        user = request.user
        if not user.is_superuser and db_field.name == 'session':
            groups = user.get_groups(settings.IRIB_FU_)
            queryset = super(EnactmentAdmin, self).get_field_queryset(db, db_field, request)
            return queryset.filter(session__group__name__in=groups) | queryset.filter(
                session_id__in=Member.objects.filter(user=user).values('session_id'))
        return super(EnactmentAdmin, self).get_field_queryset(db, db_field, request)

    def get_inline_instances(self, request, obj=None):
        if request.user.is_superuser or request.user.is_secretary or request.user.is_scoped_secretary:
            return [
                GroupFollowUpInline(self.model, self.admin_site),
                get_followup_inline(request)(self.model, self.admin_site),
                AttachmentInline(self.model, self.admin_site),
            ]
        elif FollowUp.objects.filter(actor=request.user).count() > 0:
            return [
                get_followup_inline(request)(self.model, self.admin_site),
                AttachmentInline(self.model, self.admin_site),
            ]
        else:
            return [
                AttachmentInline(self.model, self.admin_site),
            ]

    def get_queryset(self, request):
        queryset = super(EnactmentAdmin, self).get_queryset(request).filter(follow_grade=1).annotate(
            status=Count('followup'))

        if request.user.is_superuser or request.user.is_secretary:
            return queryset

        user = request.user
        groups = user.get_groups(settings.IRIB_FU_)
        return queryset.filter(session__session__group__name__in=groups) | \
               queryset.filter(pk__in=FollowUp.objects.filter(actor=user).values('enactment')) | \
               queryset.filter(session__session__in=Member.objects.filter(user=user).values('session'))

    def get_readonly_fields(self, request, obj=None):
        extra_readonly = ['_review_date']
        if not (request.user.is_superuser or request.user.is_secretary or request.user.is_scoped_secretary):
            return self.readonly_fields + extra_readonly + ['session', 'assigner', 'subject',
                                                            'description', 'follow_grade', '_type']
        elif obj:
            return self.readonly_fields + extra_readonly

        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        user = request.user
        try:
            if not user.is_superuser:
                groups = user.get_groups(settings.IRIB_FU_)
                if not obj.session.session.group.name in groups:
                    raise Exception(_('Session not allowed.'))

            super(EnactmentAdmin, self).save_model(request, obj, form, change)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    def delete_model(self, request, obj):
        user = request.user
        try:
            if not user.is_superuser:
                groups = user.get_groups(settings.IRIB_FU_)
                if not obj.session.session.group.name in groups:
                    raise Exception(_('Session not allowed.'))

            super(EnactmentAdmin, self).delete_model(request, obj)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    def report(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = Enactment.objects.filter(
            pk__in=[item[0] for item in request.session['%s_query_set' % model_full_name]])
        minutes = []
        for minute in Session.objects.filter(pk__in=queryset.values('session')):
            minutes.append({'minute': minute, 'enactments': queryset.filter(session=minute)})

        context = dict(
            minutes=minutes,
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now()),
            full_model_name=model_full_name
        )
        return TemplateResponse(request, 'admin/custom/enactments-list-report.html', context)

    def report_excel(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = Enactment.objects.filter(
            pk__in=[item[0] for item in request.session['%s_query_set' % model_full_name]])
        context = dict(
            followups=FollowUp.objects.filter(enactment__in=queryset),
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now()),
            full_model_name=model_full_name
        )
        return TemplateResponse(request, 'admin/custom/enactments-list-report-excel.html', context)

    def report_todo(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = Enactment.objects.filter(
            pk__in=[item[0] for item in request.session['%s_query_set' % model_full_name]])
        followups = FollowUp.objects.filter(enactment__in=queryset.distinct())
        followups = followups.filter(result__isnull=True) | followups.filter(result='')
        context = dict(
            followups=followups.distinct(),
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now()),
            full_model_name=model_full_name
        )
        return TemplateResponse(request, 'admin/custom/enactments-list-report-excel.html', context)

    def get_urls(self):
        urls = super(EnactmentAdmin, self).get_urls()
        return [
                   path('close/', self.close, name="irib-enactment-close"),
                   path('report/', self.report, name="irib-enactment-report"),
                   path('report-excel/', self.report_excel, name="irib-enactment-report-excel"),
                   path('report-todo/', self.report_todo, name="irib-enactment-todo-report"),
               ] + urls

    @atomic
    def close(self, request):
        result = self.next(request)
        pk = int(request.GET['pk'])
        enactment = get_object_or_404(Enactment, pk=pk)
        enactment.follow_grade = 0
        enactment.save()
        return result

    def response_change(self, request, obj):
        if 'add-group-followup' in request.POST:
            if request.POST['groupfollowup_set-0-group']:
                group = Group.objects.get(pk=request.POST['groupfollowup_set-0-group'])
                for group_user in GroupUser.objects.filter(group=group):
                    FollowUp.objects.get_or_create(enactment=obj, actor=group_user.user)
                messages.set_level(request, messages.INFO)
                messages.error(request, _("Followup added for all %(group)s users." % {'group': group.name}))
            return HttpResponseRedirect('.')
        return super(EnactmentAdmin, self).response_change(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        super(EnactmentAdmin, self).response_delete(request, obj_display, obj_id)
        return self.next(request, obj_id)


@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    model = Group
    inlines = [GroupUserInline]
