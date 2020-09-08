from . import models
from django.contrib import admin
from django.contrib import messages
from django.db.transaction import atomic
from jalali_date.admin import ModelAdminJalaliMixin
from .forms import get_activity_assessment_inline_form
from django.utils.translation import ugettext_lazy as _
from IRIB_FollowUpProject.utils import get_jalali_filter, BaseModelAdmin


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
        fields = ['member', 'score', 'scores', 'description', 'date_jalali', ]
        readonly_fields = ['member', 'date_jalali', 'score']
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
                       'description',)}),
    )
    list_display = ['row', 'activity', 'date', 'status']
    list_display_links = ['row', 'activity', 'date', 'status']
    search_fields = ['row', 'activity', 'description']
    readonly_fields = ['row', 'max_score', 'score', 'limit', 'quantity', 'date', 'status', 'user']
    list_filter = [get_jalali_filter('_date', _('Creation Date')), '_status', 'activity']

    def get_queryset(self, request):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_committee_member(user):
            return models.PersonalCardtable.objects.all()
        else:
            return models.PersonalCardtable.objects.filter(user=user)

    def get_fieldsets(self, request, obj=None):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_committee_member(user):
            return (
                (_('Main info'), {
                    'fields': (
                        ('row', 'date', 'status'), ('activity', 'max_score', 'score', 'limit', 'quantity'),
                        'description',)}),)
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        if obj and obj.user != user:
            return self.readonly_fields + ['activity', 'description']

        return self.readonly_fields

    def get_list_display(self, request):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_committee_member(user):
            list_display = self.list_display.copy()
            list_display.insert(1, 'user')
            return list_display
        return self.list_display

    def get_list_display_links(self, request, list_display):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_committee_member(user):
            return self.list_display_links + ['user']
        return self.list_display_links

    def get_list_filter(self, request):
        user = request.user
        if user.is_superuser or models.CommitteeMember.is_committee_member(user):
            return self.list_filter + ['user']
        return self.list_filter

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
        except Exception as e:
            self.message_user(request, e, messages.ERROR)

    def save_formset(self, request, form, formset, change):
        try:
            super(PersonalCardtableAdmin, self).save_formset(request, form, formset, change)
        except Exception as e:
            self.message_user(request, e, messages.ERROR)

    def get_inline_instances(self, request, obj=None):
        return [
            AttachmentInline(self.model, self.admin_site),
            ActivitySubCategoryInline(self.model, self.admin_site),
            get_activity_assessment_inline(request)(self.model, self.admin_site),
        ]


@admin.register(models.AssessmentCardtable)
class AssessmentCardtableAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = models.AssessmentCardtable
    fieldsets = (
        (_('Main info'), {
            'fields': (('row', 'date', 'user', 'status'), ('activity', 'max_score', 'score'), 'description',)}),
    )
    list_display = ['row', 'user', 'activity', 'date', 'status']
    list_display_links = ['row', 'user', 'activity', 'date', 'status']
    search_fields = ['row', 'activity', 'description']
    readonly_fields = ['row', 'max_score', 'score', 'user', 'date', 'status']
    list_filter = ['_status', 'activity']

    def save_model(self, request, obj, form, change):
        return super(AssessmentCardtableAdmin, self).save_model(request, obj, form, change)

    def get_inline_instances(self, request, obj=None):
        return [
            AttachmentInline(self.model, self.admin_site),
            get_activity_assessment_inline(request)(self.model, self.admin_site),
        ]
