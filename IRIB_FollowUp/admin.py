import datetime
from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from jalali_date import datetime2jalali
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.admin import SimpleListFilter
from jalali_date.admin import ModelAdminJalaliMixin
from IRIB_FollowUpProject.utils import get_admin_url
from django.contrib.auth.models import Group as _Group
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from .forms import EnactmentAdminForm, get_followup_inline_form
from IRIB_FollowUp.models import User, Enactment, Session, Subject, Supervisor, \
    Attachment, Attendant, FollowUp, Group, GroupUser, GroupFollowUp


class JalaliDateFilter(SimpleListFilter):
    title = _('Assignment Date')
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return [('today', _('Today')), ('this_week', _('This week')), ('10days', _('Last 10 days')),
                ('this_month', _('This month')), ('30days', _('Last 30 days')), ('90days', _('Last 3 months')),
                ('180days', _('Last 6 months'))]

    def queryset(self, request, queryset):
        startdate = timezone.now()
        enddate = None
        if self.value() == 'today':
            enddate = startdate

        if self.value() == 'this_week':
            enddate = startdate - datetime.timedelta(days=(startdate.weekday() + 2) % 7)

        if self.value() == '10days':
            enddate = startdate - datetime.timedelta(days=9)

        if self.value() == 'this_month':
            enddate = startdate - datetime.timedelta(days=datetime2jalali(startdate).day - 1)

        if self.value() == '30days':
            enddate = startdate - datetime.timedelta(days=29)

        if self.value() == '90days':
            enddate = startdate - datetime.timedelta(days=89)

        if self.value() == '180days':
            enddate = startdate - datetime.timedelta(days=179)

        return queryset.filter(date__range=[enddate, startdate]) if enddate else queryset


class ReviewJalaliDateFilter(SimpleListFilter):
    title = _('Review Date')
    parameter_name = 'review_date'

    def lookups(self, request, model_admin):
        return [('today', _('Today')), ('this_week', _('This week')), ('10days', _('Last 10 days')),
                ('this_month', _('This month')), ('30days', _('Last 30 days')), ('90days', _('Last 3 months')),
                ('180days', _('Last 6 months'))]

    def queryset(self, request, queryset):
        startdate = timezone.now()
        enddate = None
        if self.value() == 'today':
            enddate = startdate

        if self.value() == 'this_week':
            enddate = startdate - datetime.timedelta(days=(startdate.weekday() + 2) % 7)

        if self.value() == '10days':
            enddate = startdate - datetime.timedelta(days=9)

        if self.value() == 'this_month':
            enddate = startdate - datetime.timedelta(days=datetime2jalali(startdate).day - 1)

        if self.value() == '30days':
            enddate = startdate - datetime.timedelta(days=29)

        if self.value() == '90days':
            enddate = startdate - datetime.timedelta(days=89)

        if self.value() == '180days':
            enddate = startdate - datetime.timedelta(days=179)

        return queryset.filter(review_date__range=[enddate, startdate]) if enddate else queryset


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


class GroupUserInline(admin.TabularInline):
    model = GroupUser
    insert_after_fieldset = _('Important dates')


class GroupFollowUpInline(admin.TabularInline):
    model = GroupFollowUp
    max_num = 1
    extra = 1
    template = 'admin/custom/edit_inline/tabular.html'


class SupervisorFilter(SimpleListFilter):
    title = _('Supervisor Unit')
    parameter_name = 'supervisor'

    def lookups(self, request, model_admin):
        return [(supervisor.pk, supervisor.name) for supervisor in Supervisor.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(pk__in=FollowUp.objects.filter(actor__supervisor__pk=self.value()).values(
            'enactment__pk')) if self.value() else queryset


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(Session)
class SessionAdmin(BaseModelAdmin):
    model = Session
    search_fields = ['name', ]
    inlines = [AttendantInline]

    @atomic()
    def save_model(self, request, obj, form, change):
        if obj.pk:
            if 'name' in form.initial:
                group = get_object_or_404(Group, name=form.initial['name'])
                group.name = obj.name
                group.save()
        else:
            Group.objects.get_or_create(name=obj.name)
        super(SessionAdmin, self).save_model(request, obj, form, change)

    @atomic()
    def save_formset(self, request, form, formset, change):
        if formset.model._meta.model_name == 'attendant':
            group = Group.objects.get_or_create(name=formset.instance.name)[0]
            for item in formset.cleaned_data:
                if 'user' in item:
                    GroupUser.objects.get_or_create(group=group, user=item['user'])
        super(SessionAdmin, self).save_formset(request, form, formset, change)


@admin.register(Subject)
class SubjectAdmin(BaseModelAdmin):
    model = Subject
    search_fields = ['name', ]


@admin.register(Supervisor)
class SupervisorAdmin(BaseModelAdmin):
    model = Supervisor
    search_fields = ['name', ]


class AttachmentInline(admin.TabularInline):
    model = Attachment


def get_followup_inline(request):
    class FollowUpInline(ModelAdminJalaliMixin, admin.TabularInline):
        model = FollowUp
        form = get_followup_inline_form(request)
        fields = ['actor', 'supervisor', 'result', 'date_jalali']
        readonly_fields = ['supervisor', 'date_jalali']

        def has_add_permission(self, request, obj):
            user = request.user
            return user.is_superuser or user.is_secretary

        def has_delete_permission(self, request, obj):
            user = request.user
            return user.is_superuser or user.is_secretary

        def get_readonly_fields(self, request, obj=None):
            user = request.user
            if user.is_superuser or user.is_secretary:
                return self.readonly_fields
            else:
                return self.readonly_fields + ['actor']

        def get_formset(self, request, obj=None, **kwargs):
            user = request.user
            if user.is_superuser or user.is_secretary:
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
                     'enactment__session__name', 'enactment__subject__name',
                     'enactment__assigner__name', 'enactment__description', 'enactment__result',
                     'enactment__second_supervisor__name', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enactment" and not (request.user.is_superuser or request.user.is_secretary):
            queryset = Enactment.objects.filter(follow_grade=1)
            kwargs["queryset"] = queryset.filter(
                session__pk__in=Attendant.objects.filter(user=request.user).values('session'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(User)
class UserAdmin(ModelAdminJalaliMixin, _UserAdmin, BaseModelAdmin):
    fieldsets = (
        (_('Personal info'), {
            'fields': (('username', 'first_name', 'last_name', '_title'),
                       ('access_level', 'is_active'),)}),
        (_('Address Info'), {
            'fields': (('supervisor', 'email'))}),
        (_('Important dates'), {
            'fields': (('last_login_jalali', 'date_joined_jalali'),)}),
        (_('Permissions'), {
            'fields': (('is_staff', 'is_superuser'), 'groups', 'user_permissions'), }),
        (_('Sensitive Info'), {'fields': ('password',)}),
    )
    list_display = ['username', 'first_name', 'last_name', 'access_level', 'supervisor', 'last_login_jalali']
    list_display_links = ['username', 'first_name', 'last_name', 'access_level', 'supervisor', 'last_login_jalali']
    list_filter = ('supervisor', 'access_level', 'is_active', 'is_superuser', 'groups')
    readonly_fields = ['last_login_jalali', 'date_joined_jalali']
    inlines = [AttendantInline, GroupUserInline]
    change_form_template = 'admin/custom/change_form.html'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_secretary and not request.user.is_superuser:
            return self.readonly_fields + ['is_staff', 'is_superuser', 'groups', 'user_permissions']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.is_staff = True
        super(UserAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        user = form.instance
        super(UserAdmin, self).save_related(request, form, formsets, change)
        self.set_groups(user)

    def set_groups(self, user):
        if user.is_secretary:
            user.groups.add(get_object_or_404(_Group, name='Operators'))
            user.groups.remove(get_object_or_404(_Group, name='Users'))
        else:
            user.groups.add(get_object_or_404(_Group, name='Users'))
            user.groups.remove(get_object_or_404(_Group, name='Operators'))

    def delete_model(self, request, obj):
        try:
            return super(UserAdmin, self).delete_model(request, obj)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            try:
                obj.delete()
            except Exception as e:
                messages.set_level(request, messages.ERROR)
                messages.error(request, e)


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fields = (('row', 'session', 'date', 'review_date'),
              ('assigner', 'subject', '_type'), 'description',
              )
    list_display = ['row', 'type', 'session', 'date_jalali', 'review_date_jalali', 'subject', 'description_short']
    list_display_links = ['row', 'type', 'session', 'date_jalali', 'review_date_jalali', 'subject', 'description_short']
    list_filter = ['_type', ReviewJalaliDateFilter, JalaliDateFilter, ActorFilter, SupervisorFilter, 'session',
                   'subject',
                   'assigner']
    search_fields = ['session__name', 'subject__name', 'description', 'assigner__first_name', 'assigner__last_name', 'id' ]
    readonly_fields = ['row', 'type', 'description_short', 'date_jalali', 'review_date_jalali', ]
    form = EnactmentAdminForm

    def get_inline_instances(self, request, obj=None):
        return [
            GroupFollowUpInline(self.model, self.admin_site),
            get_followup_inline(request)(self.model, self.admin_site),
            AttachmentInline(self.model, self.admin_site),
        ]

    def get_queryset(self, request):
        queryset = Enactment.objects.filter(follow_grade=1)
        if request.user.is_superuser or request.user.is_secretary:
            return queryset

        return queryset.filter(pk__in=FollowUp.objects.filter(actor=request.user).values('enactment')) | \
               queryset.filter(session__in=Attendant.objects.filter(user=request.user).values('session'))

    def get_readonly_fields(self, request, obj=None):
        if not (request.user.is_superuser or request.user.is_secretary):
            return self.readonly_fields + ['session', 'date', 'review_date', 'assigner', 'subject',
                                           'description', 'follow_grade']
        elif obj:
            return self.readonly_fields + ['date', 'review_date']

        return self.readonly_fields

    def get_urls(self):
        urls = super(EnactmentAdmin, self).get_urls()
        from django.urls import path
        return [path('first/', self.first, name="first"),
                path('previous/', self.previous, name="previous"),
                path('next/', self.next, name="next"),
                path('last/', self.last, name="last"),
                path('close/', self.close, name="close"),
                ] + urls

    def first(self, request):
        queryset = self.get_queryset(request)
        return HttpResponseRedirect(get_admin_url(queryset.first()))

    def previous(self, request):
        pk = int(request.GET['pk'])
        queryset = self.get_queryset(request)
        index = list(queryset.values_list('pk', flat=True)).index(pk)
        if index == 0:
            obj = queryset[index]
        else:
            obj = queryset[index - 1]
        return HttpResponseRedirect(get_admin_url(obj))

    def next(self, request):
        pk = int(request.GET['pk'])
        queryset = self.get_queryset(request)
        index = list(queryset.values_list('pk', flat=True)).index(pk)
        if index == queryset.count() - 1:
            obj = queryset[index]
        else:
            obj = queryset[index + 1]
        return HttpResponseRedirect(get_admin_url(obj))

    def last(self, request):
        queryset = self.get_queryset(request)
        return HttpResponseRedirect(get_admin_url(queryset.last()))

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
                self.message_user(request, _("Followup added for all %(group)s users." % {'group': group.name}))
            return HttpResponseRedirect('.')
        return super(EnactmentAdmin, self).response_change(request, obj)


@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    model = Group
    inlines = [GroupUserInline]
