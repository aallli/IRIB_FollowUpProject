import datetime
from django.contrib import admin
from django.utils import timezone
from .forms import EnactmentAdminForm
from jalali_date import datetime2jalali
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.admin import SimpleListFilter
from jalali_date.admin import ModelAdminJalaliMixin
from IRIB_FollowUpProject.utils import get_admin_url
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from IRIB_FollowUp.models import User, Enactment, Session, Subject, Supervisor, \
    Attachment, Attendant


class JalaliDateFilter(SimpleListFilter):
    title = _('Review Date')
    parameter_name = 'review_date'

    def lookups(self, request, model_admin):
        return [('today', _('Today')), ('this_week', _('This week')), ('10days', _('Last 10 days')),
                ('this_month', _('This month')), ('30days', _('Last 30 days'))]

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

        return queryset.filter(review_date__range=[enddate, startdate]) if enddate else queryset


class ActorFilter(SimpleListFilter):
    title = _('Supervisor')
    parameter_name = 'actor'

    def lookups(self, request, model_admin):
        return [(actor.pk, actor) for actor in User.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(first_actor__pk=self.value()) | queryset.filter(
            second_actor__pk=self.value()) if self.value() else queryset


class AttendantInline(admin.TabularInline):
    model = Attendant


class SupervisorFilter(SimpleListFilter):
    title = _('Supervisor Unit')
    parameter_name = 'supervisor'

    def lookups(self, request, model_admin):
        return [(supervisor.pk, supervisor.name) for supervisor in Supervisor.objects.all()]

    def queryset(self, request, queryset):
        return queryset.filter(first_supervisor__pk=self.value()) | queryset.filter(
            second_supervisor__pk=self.value()) if self.value() else queryset


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(Session)
class SessionAdmin(BaseModelAdmin):
    model = Session
    search_fields = ['name', ]
    inlines = [AttendantInline]


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
            queryset = Enactment.objects.filter(follow_grade=1)
            kwargs["queryset"] = \
                queryset.filter(first_actor=request.user) | queryset.filter(second_actor=request.user) | \
                queryset.filter(session__pk__in=Attendant.objects.filter(user=request.user).values('session'))
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
    inlines = [AttendantInline]

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_secretary and not request.user.is_superuser:
            return self.readonly_fields + ['is_staff', 'is_superuser', 'groups', 'user_permissions']
        return self.readonly_fields


@admin.register(Enactment)
class EnactmentAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Enactment
    fields = (('id', 'session', 'date', 'review_date'),
              ('assigner', 'subject', 'code'),
              'description', 'result',
              ('first_actor', 'first_supervisor'),
              ('second_actor', 'second_supervisor'),
              )
    list_display = ['id', 'session', 'review_date_jalali', 'subject', 'description_short',
                    'result_short']
    list_display_links = ['id', 'session', 'review_date_jalali', 'subject', 'description_short',
                          'result_short']
    list_filter = [JalaliDateFilter, 'session', 'subject', 'assigner', ActorFilter, SupervisorFilter]
    search_fields = ['session__name', 'subject__name', 'assigner__name', 'description', 'result',
                     'first_actor__fname', 'first_actor__lname', 'second_actor__fname', 'second_actor__lname',
                     'first_supervisor__name', 'second_supervisor__name', ]
    inlines = [AttachmentInline]
    readonly_fields = ['description_short', 'result_short', 'review_date_jalali', 'first_supervisor',
                       'second_supervisor', ]
    form = EnactmentAdminForm

    def get_queryset(self, request):
        queryset = Enactment.objects.filter(follow_grade=1)
        if request.user.is_superuser or request.user.is_secretary:
            return queryset

        return queryset.filter(first_actor=request.user) | queryset.filter(second_actor=request.user) | \
               queryset.filter(session__pk__in=Attendant.objects.filter(user=request.user).values('session'))

    def get_readonly_fields(self, request, obj=None):
        if not (request.user.is_superuser or request.user.is_secretary):
            return self.readonly_fields + ['code', 'session', 'date', 'review_date', 'assigner', 'subject',
                                           'description', 'first_actor', 'second_actor', 'follow_grade']
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
