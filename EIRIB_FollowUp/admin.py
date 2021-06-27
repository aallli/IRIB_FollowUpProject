from .models import User as _User
from .forms import EnactmentAdminForm
from django.db.transaction import atomic
from django.contrib import admin, messages
from django.shortcuts import get_object_or_404
from django.utils import timezone, translation
from IRIB_Shared_Lib.admin import BaseModelAdmin
from django.contrib.admin import SimpleListFilter
from jalali_date.admin import ModelAdminJalaliMixin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
#from EIRIB_FollowUp.utils import save_user, delete_user, execute_query
from IRIB_Shared_Lib.utils import to_jalali, get_jalali_filter, get_model_fullname, format_date
from EIRIB_FollowUp.models import Enactment, Session, Assigner, Subject, Actor, Supervisor, Attachment


class ActorFilter(SimpleListFilter):
    title = _('Supervisor')
    parameter_name = 'actor'

    def lookups(self, request, model_admin):
        return [(-1, _('No actor'))] + [(actor.pk, actor) for actor in Actor.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(first_actor__pk=self.value()) | queryset.filter(
                second_actor__pk=self.value()) if int(self.value()) > 0 else queryset.filter(
                first_actor__isnull=True).filter(second_actor__isnull=True)
        else:
            return queryset


class SupervisorFilter(SimpleListFilter):
    title = _('Supervisor Unit')
    parameter_name = 'supervisor'

    def lookups(self, request, model_admin):
        return [(-1, _('No supervisor'))] + [(supervisor.pk, supervisor.name) for supervisor in Supervisor.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(first_actor__supervisor__pk=self.value()) | queryset.filter(
                second_actor__supervisor__pk=self.value()) if int(self.value()) > 0 else queryset.filter(
                first_actor__supervisor__isnull=True).filter(second_actor__supervisor__isnull=True)
        else:
            return queryset


@admin.register(Session)
class SessionAdmin(BaseModelAdmin):
    model = Session
    search_fields = ['name', ]


@admin.register(Assigner)
class AssignerAdmin(BaseModelAdmin):
    model = Assigner
    search_fields = ['name', ]


@admin.register(Subject)
class SubjectAdmin(BaseModelAdmin):
    model = Subject
    search_fields = ['name', ]


@admin.register(Actor)
class ActortAdmin(BaseModelAdmin):
    model = Actor
    list_display = ['fname', 'lname', 'supervisor']
    list_display_links = ['fname', 'lname', 'supervisor']
    search_fields = ['fname', 'lname', 'supervisor__name']


@admin.register(Supervisor)
class SupervisorAdmin(BaseModelAdmin):
    model = Supervisor
    search_fields = ['name', ]


class AttachmentInline(admin.TabularInline):
    model = Attachment


@admin.register(Attachment)
class AttachmentAdmin(BaseModelAdmin):
    model = Attachment
    fields = ['description', 'file', 'enactment']
    search_fields = ['description', 'file',
                     'enactment__session__name', 'enactment__code', 'enactment__subject__name',
                     'enactment__assigner__name', 'enactment__description', 'enactment__result',
                     'enactment__first_actor__fname', 'enactment__first_actor__lname', 'enactment__second_actor__fname',
                     'enactment__second_actor__lname', 'enactment__first_supervisor__name',
                     'enactment__second_supervisor__name', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "enactment" and not (request.user.is_superuser or request.user.is_secretary):
            _user = _User.objects.get(user=request.user)
            kwargs["queryset"] = Enactment.objects.filter(
                row__in=_user.query) if _user and not _user.query is None else Enactment.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(_User)
class UserAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = _User
    fields = ['user', ('query_name', 'secretary_query_name')]
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__supervisor__name', 'query_name',
                     'secretary_query_name']
    list_display = ['first_name', 'last_name', 'username', 'access_level', 'supervisor', 'last_login_jalali']
    list_display_links = ['first_name', 'last_name', 'username', 'access_level', 'supervisor', 'last_login_jalali']
    list_filter = ('user__supervisor', 'user__access_level', 'user__is_active', 'user__is_superuser', 'user__groups')
    readonly_fields = ['last_login_jalali', ]

    @atomic
    def save_model(self, request, obj, form, change):
        super(UserAdmin, self).save_model(request, obj, form, change)
        try:
            pass
            # save_user(obj.user)
        except Exception as e:
            messages.set_level(request, messages.WARNING)
            messages.error(request, _('Error in creating/updating user in MS Acceess Database'))

    @atomic
    def delete_model(self, request, obj):
        try:
            pass
            # delete_user(obj.user)
        except Exception as e:
            messages.set_level(request, messages.WARNING)
            messages.error(request, _('Error in deleting user from MS Acceess Database'))

        super(UserAdmin, self).delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            try:
                try:
                    pass
                    # delete_user(obj.user)
                except Exception as e:
                    self.message_user(request, _('Error in deleting user from MS Acceess Database'), messages.WARNING)
                obj.delete()
            except Exception as e:
                messages.set_level(request, messages.ERROR)
                messages.error(request, e)


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fields = (('row', 'session', '_date', '_review_date'),
              ('assigner', 'subject', 'code'),
              'description', 'result',
              ('first_actor', 'first_supervisor'),
              ('second_actor', 'second_supervisor'),
              )
    list_display = ['row', 'session', 'date', 'review_date', 'subject', 'status_colored', 'description_short',
                    'result_short']
    list_display_links = ['row', 'session', 'date', 'review_date', 'subject', 'status_colored', 'description_short',
                          'result_short']
    list_filter = [get_jalali_filter('_review_date', _('Review Date')),
                   get_jalali_filter('_date', _('Assignment Date')), 'session', 'subject',
                   'assigner', ActorFilter, SupervisorFilter]
    search_fields = ['session__name', 'subject__name', 'assigner__name', 'description', 'result', 'first_actor__fname',
                     'first_actor__lname', 'second_actor__fname', 'second_actor__lname', 'row']
    inlines = [AttachmentInline, ]
    readonly_fields = ['row', 'description_short', 'result_short', 'review_date', 'status_colored',
                       'first_supervisor', 'second_supervisor']
    form = EnactmentAdminForm

    def get_queryset(self, request):
        queryset = super(EnactmentAdmin, self).get_queryset(request).filter(follow_grade=1)
        user = request.user
        if user.is_superuser or user.is_secretary:
            return queryset

        _user = _User.objects.get(user=user)
        return queryset.filter(row__in=_user.query) | queryset.filter(first_actor__fname=user.first_name).filter(
            first_actor__lname=user.last_name) | queryset.filter(second_actor__fname=user.first_name).filter(
            second_actor__lname=user.last_name) if _user.query else Enactment.objects.none()

    def get_readonly_fields(self, request, obj=None):
        if not (request.user.is_superuser or request.user.is_secretary or request.user.is_scoped_secretary):
            return self.readonly_fields + ['code', 'session', '_review_date', 'assigner', 'subject',
                                           'description', 'first_actor', 'second_actor', 'follow_grade']
        elif obj:
            return self.readonly_fields + ['_review_date']

        return self.readonly_fields

    @atomic
    def save_model(self, request, obj, form, change):
        new_obj = False
        user = request.user
        _user = _User.objects.get(user=user)
        if obj.session and _user.secretary_query and not obj.session.name in _user.secretary_query:
            messages.set_level(request, messages.ERROR)
            messages.error(request, _('Unauthorized session, Access denied'))
            return

        obj._review_date = timezone.now()
        if obj.pk:
            # query = '''
            #         UPDATE tblmosavabat
            #         SET tblmosavabat.natije = ?
            #        '''
            # params = [obj.result]
            #
            # if user.is_superuser or user.is_secretary or user.is_scoped_secretary:
            #     query += ", tblmosavabat.sharh=?, tblmosavabat.peygiri1=?, tblmosavabat.peygiri2=?" \
            #              ", tblmosavabat.tarikh=?, tblmosavabat.jalaseh=?, tblmosavabat.muzoo=?" \
            #              ", tblmosavabat.gooyandeh=?, tblmosavabat.vahed=?, tblmosavabat.vahed2=?" \
            #              ", tblmosavabat.mosavabatcode=?, tblmosavabat.TarikhBaznegari=?, tblmosavabat.[date]=?" \
            #              ", tblmosavabat.review_date=?"
            #     params.extend((obj.description,
            #                    obj.first_actor.lname if obj.first_actor else '-',
            #                    obj.second_actor.lname if obj.second_actor else '-',
            #                    int(to_jalali(obj._date, no_time=True).replace('/', '')) - 13000000,
            #                    obj.session.name,
            #                    obj.subject.name,
            #                    obj.assigner.name,
            #                    obj.first_actor.supervisor.name if obj.first_actor and obj.first_actor.supervisor else '-',
            #                    obj.second_actor.supervisor.name if obj.second_actor and obj.second_actor.supervisor else '-',
            #                    obj.code,
            #                    obj.review_date(),
            #                    obj._date,
            #                    obj._review_date))
            # query += '''
            #         WHERE ID = ?
            #        '''
            # params.append(obj.row)
            # execute_query(query, params, update=True)
            pass
        else:
            # query = '''
            #         INSERT INTO tblmosavabat (sharh, peygiri1, peygiri2, tarikh, lozoomepeygiri, natije, jalaseh,
            #         muzoo, gooyandeh, vahed, vahed2, mosavabatcode, TarikhBaznegari, [date], review_date)
            #         VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            #         '''
            obj.follow_grade = 1
            # params = (obj.description,
            #           obj.first_actor.lname if obj.first_actor else '-',
            #           obj.second_actor.lname if obj.second_actor else '-',
            #           int(to_jalali(obj._date, True).replace('/', '')) - 13000000,
            #           obj.follow_grade,
            #           obj.result,
            #           obj.session.name,
            #           obj.subject.name,
            #           obj.assigner.name,
            #           obj.first_actor.supervisor.name if obj.first_actor and obj.first_actor.supervisor else '-',
            #           obj.second_actor.supervisor.name if obj.second_actor and obj.second_actor.supervisor else '-',
            #           obj.code,
            #           obj.review_date(),
            #           obj._date,
            #           obj._review_date)
            # obj.row = execute_query(query, params, insert=True)
            obj.row = Enactment.objects.latest('row').row + 1
            new_obj = True

        super(EnactmentAdmin, self).save_model(request, obj, form, change)
        if new_obj:
            model_full_name = get_model_fullname(self)
            queryset_name = '%s_query_set' % model_full_name
            try:
                enactment_query_set = request.session[queryset_name]
                enactment_query_set.append({'pk': obj.pk})
                request.session[queryset_name] = list(enactment_query_set)
            except:
                pass

    @atomic
    def delete_model(self, request, obj):
        # query = '''
        #         DELETE FROM tblmosavabat
        #         WHERE tblmosavabat.ID = ?
        #         '''
        # params = (obj.row)
        # execute_query(query, params, delete=True)
        super(EnactmentAdmin, self).delete_model(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        super(EnactmentAdmin, self).response_delete(request, obj_display, obj_id)
        return self.next(request, obj_id)

    @atomic
    def save_formset(self, request, form, formset, change):
        super(EnactmentAdmin, self).save_formset(request, form, formset, change)
        # if formset.prefix == 'attachment_set' and change:
        #     obj = form.instance
        #     query = '''
        #         UPDATE tblmosavabat
        #         SET tblmosavabat.[attachments] = ?
        #        '''
        #
        #     attachments = ' '.join(
        #         '%s%s' % (request.META['HTTP_ORIGIN'], attachment.file.url) for attachment in obj.attachment_set.all())
        #
        #     params = (attachments, obj.row)
        #     query += '''
        #             WHERE ID = ?
        #            '''
        #     execute_query(query, params, update=True)

    def get_urls(self):
        urls = super(EnactmentAdmin, self).get_urls()
        from django.urls import path
        return [path('close/', self.close, name="eirib-enactment-close"),
                path('report/', self.report, name="eirib-enactment-report"),
                path('report-excel/', self.report_excel, name="eirib-enactment-report-excel"),
                path('report-todo/', self.report_todo, name="eirib-enactment-todo-report"),
                path('<int:pk>/print/', self.print, name="eirib-enactment-print"),
                ] + urls

    def report(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = Enactment.objects.filter(
            pk__in=[item['pk'] for item in request.session['%s_query_set' % model_full_name]])
        minutes = []
        for minute in Session.objects.filter(pk__in=queryset.values('session')):
            minutes.append({'minute': dict(session=dict(name=minute)),
                            'enactments': queryset.filter(session=minute)})

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
            pk__in=[item['pk'] for item in request.session['%s_query_set' % model_full_name]])
        followups = []
        for item in queryset:
            enactment = dict(
                id=item.id,
                row=item.row,
                review_date=item.review_date()
            )
            followup = dict(
                enactment=enactment
            )

            if item.first_actor:
                followup['actor'] = dict(last_name=item.first_actor.lname)
                followups.append(followup)

            if item.second_actor:
                followup['actor'] = dict(last_name=item.second_actor.lname)
                followups.append(followup)

        context = dict(
            followups=followups,
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now()),
            full_model_name=model_full_name
        )
        return TemplateResponse(request, 'admin/custom/enactments-list-report-excel.html', context)

    def report_todo(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = Enactment.objects.filter(
            pk__in=[item['pk'] for item in request.session['%s_query_set' % model_full_name]])
        queryset = queryset.filter(result__isnull=True) | queryset.filter(result='')
        followups = []
        for item in queryset.distinct():
            enactment = dict(
                id=item.id,
                row=item.row,
                review_date=item.review_date()
            )
            followup = dict(
                enactment=enactment
            )

            followup['actor'] = dict(last_name=item.followups)

            followups.append(followup)

        context = dict(
            followups=followups,
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now()),
            full_model_name=model_full_name
        )
        return TemplateResponse(request, 'admin/custom/enactments-list-report-excel.html', context)

    def print(self, request, pk):
        enactment = get_object_or_404(Enactment, pk=pk)
        context = dict(
            enactment=enactment,
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now()),
            app_name=self.opts.app_config.verbose_name
        )
        return TemplateResponse(request, 'admin/custom/eirib-enactment.html', context)

    @atomic
    def close(self, request):
        pk = int(request.GET['pk'])
        result = self.next(request, pk)
        enactment = get_object_or_404(Enactment, pk=pk)
        enactment.follow_grade = 0
        enactment.save()

        # query = '''
        #         UPDATE tblmosavabat
        #         SET tblmosavabat.lozoomepeygiri = ?
        #         WHERE ID = ?
        #        '''
        # params = [enactment.follow_grade, enactment.row]
        # execute_query(query, params, update=True)
        return result
