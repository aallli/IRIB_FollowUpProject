from . import models
from django.urls import path
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone, translation
from IRIB_Shared_Lib.admin import BaseModelAdmin
from django.contrib.auth.models import Permission
from jalali_date.admin import ModelAdminJalaliMixin
from .forms import get_activity_assessment_inline_form
from django.utils.translation import ugettext_lazy as _
from IRIB_Shared_Lib.utils import get_jalali_filter, get_admin_url, to_jalali, format_date, get_model_fullname


class SubCategoryInline(admin.TabularInline):
    model = models.SubCategory


class AttachmentInline(admin.TabularInline):
    model = models.Attachment
    extra = 1


class ActivityIndicatorInline(admin.TabularInline):
    model = models.ActivityIndicator


class ActivitySubCategoryInline(admin.TabularInline):
    model = models.ActivitySubCategory


def get_activity_assessment_inline(request):
    class ActivityAssessmentInline(ModelAdminJalaliMixin, admin.TabularInline):
        fields = ['member', 'score', 'description', 'date', ]
        readonly_fields = ['member', 'date', 'score']
        model = models.ActivityAssessment
        max_num = models.CommitteeMember.objects.count()
        extra = 0
        form = get_activity_assessment_inline_form(request)
        template = 'admin/custom/edit_inline/tabular.html'

        def has_add_permission(self, request, obj):
            return False

        def has_delete_permission(self, request, obj=None):
            return False

    return ActivityAssessmentInline


@admin.register(models.SubCategory)
class SubCategoryAdmin(BaseModelAdmin):
    model = models.SubCategory
    list_display = ['category', 'name']
    list_display_links = ['category', 'name']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


@admin.register(models.Category)
class CategoryAdmin(BaseModelAdmin):
    model = models.Category
    search_fields = ['name', ]
    inlines = [SubCategoryInline]


@admin.register(models.Attachment)
class AttachmentAdmin(BaseModelAdmin):
    model = models.Attachment
    fields = ['description', 'file', 'cardtable']
    search_fields = ['description', 'file',
                     'cardtable__activity__name', 'cardtable__description',
                     'cardtable__user__first_name', 'cardtable__user__last_name', 'cardtable__user__username', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cardtable" and not (request.user.is_superuser or request.user.is_km_operator):
            kwargs["queryset"] = models.CardtableBase.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser or request.user.is_km_operator:
            return super(AttachmentAdmin, self).get_queryset()
        return models.Attachment.objects.filter(cardtable__in=models.CardtableBase.objects.filter(user=request.user))


@admin.register(models.Activity)
class ActivityAdmin(BaseModelAdmin):
    model = models.Activity
    search_fields = ['name', ]
    inlines = [ActivityIndicatorInline]


@admin.register(models.CommitteeMember)
class CommitteeMemberAdmin(BaseModelAdmin):
    model = models.CommitteeMember
    list_display = ['user', 'chairman', 'secretary']
    list_display_links = ['user', 'chairman', 'secretary']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']

    def save_model(self, request, obj, form, change):
        super(CommitteeMemberAdmin, self).save_model(request, obj, form, change)
        try:
            obj.user.user_permissions.add(Permission.objects.get(codename='change_assessmentcardtable'))
        except:
            pass

    def delete_model(self, request, obj):
        super(CommitteeMemberAdmin, self).delete_model(request, obj)
        try:
            obj.user.user_permissions.remove(Permission.objects.get(codename='change_assessmentcardtable'))
        except:
            pass


@admin.register(models.Indicator)
class IndicatorAdmin(BaseModelAdmin):
    model = models.Indicator
    search_fields = ['name', ]


@admin.register(models.PersonalCardtable)
class PersonalCardtableAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = models.PersonalCardtable
    fieldsets = (
        (_('Main info'), {
            'fields': (('row', 'date', 'status'), ('activity', 'max_score', 'score', 'limit', 'quantity'),
                       'description', 'secretary_description')}),
    )
    list_display = ['row', 'activity', 'date', 'status']
    list_display_links = ['row', 'activity', 'date', 'status']
    search_fields = ['id', 'activity__name', 'description', ]
    readonly_fields = ['row', 'max_score', 'score', 'limit', 'quantity', 'date', 'status', 'secretary_description']
    list_filter = [get_jalali_filter('_date', _('Creation Date')), '_status', 'activity']

    def get_queryset(self, request):
        return super(PersonalCardtableAdmin, self).get_queryset(request).filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        return obj and obj._status in [models.ActivityStatus.DR, models.ActivityStatus.EN]

    def has_delete_permission(self, request, obj=None):
        return obj and obj._status == models.ActivityStatus.DR

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        if obj and obj.user != user:
            return self.readonly_fields + ['activity', 'description']

        return self.readonly_fields

    @atomic
    def save_model(self, request, obj, form, change):
        new_model = not obj.pk
        try:
            if new_model:
                obj.user = request.user
                if obj.quantity() == obj.limit():
                    raise Exception(_('Maximum exceeded, Invalid operations.'))
            super(PersonalCardtableAdmin, self).save_model(request, obj, form, change)
            if new_model:
                for member in models.CommitteeMember.objects.all():
                    models.ActivityAssessment.objects.get_or_create(cardtable=obj, member=member)

                model_full_name = get_model_fullname(self)
                queryset_name = '%s_query_set' % model_full_name

                try:
                    enactment_query_set = request.session[queryset_name]
                    enactment_query_set.append({'pk': obj.pk})
                    request.session[queryset_name] = list(enactment_query_set)
                except:
                    pass
        except Exception as e:
            self.message_user(request, e, messages.ERROR)

    def save_formset(self, request, form, formset, change):
        try:
            super(PersonalCardtableAdmin, self).save_formset(request, form, formset, change)
        except Exception as e:
            self.message_user(request, e, messages.ERROR)

    def get_inline_instances(self, request, obj=None):
        if obj and obj._status in [models.ActivityStatus.DR, models.ActivityStatus.EN, models.ActivityStatus.NW]:
            return [
                AttachmentInline(self.model, self.admin_site),
                ActivitySubCategoryInline(self.model, self.admin_site),
            ]
        else:
            return [
                AttachmentInline(self.model, self.admin_site),
                ActivitySubCategoryInline(self.model, self.admin_site),
                get_activity_assessment_inline(request)(self.model, self.admin_site),
            ]

    def get_urls(self):
        urls = super(PersonalCardtableAdmin, self).get_urls()
        return [path('send/', self.send, name="send"), ] + urls

    @atomic
    def send(self, request):
        pk = int(request.GET['pk'])
        personalcardtable = get_object_or_404(models.CardtableBase, pk=pk)
        personalcardtable._status = models.ActivityStatus.NW
        personalcardtable.save()
        return HttpResponseRedirect(get_admin_url(self.model, pk))


@admin.register(models.AssessmentCardtable)
class AssessmentCardtableAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = models.AssessmentCardtable
    fieldsets = (
        (_('Main info'), {
            'fields': (('row', 'user', 'date', 'status'), ('activity', 'max_score', 'score', 'limit', 'quantity'),
                       'description', 'secretary_description')}),
    )
    list_display = ['row', 'user', 'activity', 'date', 'status']
    list_display_links = ['row', 'user', 'activity', 'date', 'status']
    search_fields = ['id', 'activity__name', 'description', 'user__first_name', 'user__last_name', 'user__username']
    readonly_fields = ['row', 'user', 'max_score', 'score', 'limit', 'quantity', 'date', 'status', 'activity',
                       'description']
    list_filter = ['user', get_jalali_filter('_date', _('Creation Date')), '_status', 'activity']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        # @todo: set to False
        return True

    def get_queryset(self, request):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_km_committee_secretary(user):
            return models.AssessmentCardtable.objects.exclude(
                _status__in=[models.ActivityStatus.DR, models.ActivityStatus.EN])
        elif models.CommitteeMember.is_km_committee_member(user):
            return models.AssessmentCardtable.objects.exclude(
                _status__in=[models.ActivityStatus.DR, models.ActivityStatus.EN, models.ActivityStatus.NW])
        else:
            return models.AssessmentCardtable.objects.none()

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_km_committee_secretary(user):
            return self.readonly_fields

        return self.readonly_fields + ['secretary_description']

    def save_model(self, request, obj, form, change):
        return super(AssessmentCardtableAdmin, self).save_model(request, obj, form, change)

    def get_inline_instances(self, request, obj=None):
        if obj and obj._status in [models.ActivityStatus.DR, models.ActivityStatus.EN, models.ActivityStatus.NW]:
            return [
                AttachmentInline(self.model, self.admin_site),
                ActivitySubCategoryInline(self.model, self.admin_site),
            ]
        else:
            return [
                AttachmentInline(self.model, self.admin_site),
                ActivitySubCategoryInline(self.model, self.admin_site),
                get_activity_assessment_inline(request)(self.model, self.admin_site),
            ]

    def get_urls(self):
        urls = super(AssessmentCardtableAdmin, self).get_urls()
        return [path('accept/', self.accept, name="accept"),
                path('todo/', self.todo, name="todo"),
                path('approve/', self.approve, name="approve"),
                path('capprove/', self.conditional_approve, name="conditional-approve"),
                path('reject/', self.reject, name="reject"),
                path('<int:pk>/assess/', self.assess, name="assess"),
                path('<int:pk>/assess-save/', self.assess_save, name="assess-save"),
                ] + urls

    @atomic
    def accept(self, request):
        pk = int(request.GET['pk'])
        assessmentcardtable = get_object_or_404(models.CardtableBase, pk=pk)
        assessmentcardtable._status = models.ActivityStatus.AC
        assessmentcardtable.save()
        return self.next(request, pk)

    @atomic
    def todo(self, request):
        pk = int(request.GET['pk'])
        assessmentcardtable = get_object_or_404(models.CardtableBase, pk=pk)
        if assessmentcardtable.secretary_description:
            assessmentcardtable._status = models.ActivityStatus.EN
            assessmentcardtable.save()
            return self.next(request, pk)
        else:
            self.message_user(request, _('Type some note for knowledge user and save before clicking Accept button...'),
                              messages.WARNING)
        return HttpResponseRedirect(get_admin_url(models.AssessmentCardtable, pk))

    @atomic
    def approve(self, request):
        pk = int(request.GET['pk'])
        assessmentcardtable = get_object_or_404(models.CardtableBase, pk=pk)
        assessmentcardtable._status = models.ActivityStatus.AP
        assessmentcardtable.save()
        return HttpResponseRedirect(get_admin_url(models.AssessmentCardtable, pk))

    @atomic
    def conditional_approve(self, request):
        pk = int(request.GET['pk'])
        assessmentcardtable = get_object_or_404(models.CardtableBase, pk=pk)
        assessmentcardtable._status = models.ActivityStatus.CN
        assessmentcardtable.save()
        return HttpResponseRedirect(get_admin_url(models.AssessmentCardtable, pk))

    @atomic
    def reject(self, request):
        pk = int(request.GET['pk'])
        assessmentcardtable = get_object_or_404(models.CardtableBase, pk=pk)
        assessmentcardtable._status = models.ActivityStatus.RJ
        assessmentcardtable.save()
        return HttpResponseRedirect(get_admin_url(models.AssessmentCardtable, pk))

    @atomic
    def assess(self, request, pk):
        activityassessment = models.ActivityAssessment.objects.get(pk=pk)
        indicatorscores = [[int(item.value), item.label] for item in models.IndicatorScore]
        context = dict(
            pk=pk,
            closed=activityassessment.cardtable.closed,
            assessor=activityassessment.member.user,
            scores=activityassessment._scores,
            indicatorscores=indicatorscores,
            indicators=activityassessment.cardtable.activity.activityindicator_set.all(),
            assessmentdate=activityassessment.date())

        return render(request, 'admin/custom/activity_assessment_details.html', context)

    @atomic
    def assess_save(self, request, pk):
        activityassessment = models.ActivityAssessment.objects.get(pk=pk)
        activityassessment._scores = []
        for indicator_pk in models.ActivityIndicator.objects.filter(
                activity=activityassessment.cardtable.activity).values_list(
            'indicator'):
            activityassessment._scores.append(request.POST['indicator-%s' % indicator_pk])
        activityassessment.save()
        return HttpResponseRedirect(get_admin_url(models.AssessmentCardtable, activityassessment.cardtable.pk))
