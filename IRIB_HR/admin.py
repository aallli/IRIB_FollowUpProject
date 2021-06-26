import locale
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from IRIB_Shared_Lib.models import Month
from django.utils import timezone, translation
from IRIB_Shared_Lib.admin import BaseModelAdmin
from jalali_date.admin import ModelAdminJalaliMixin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from IRIB_Shared_Lib.utils import to_jalali, format_date, get_jalali_filter
from .models import PaySlip, BonusType, Bonus, BonusSubType, PersonalInquiry, Attachment

# Used for thousands separator for numbers... usage: f'{value:n}'
locale.setlocale(locale.LC_ALL, '')


class AttachmentInline(admin.TabularInline):
    model = Attachment

    def get_readonly_fields(self, request, obj=None):
        if PersonalInquiry.objects.filter(pk=obj.pk).count() == 0:
            self.extra = 0
            self.max_num = 0
            return ['description', 'file']
        return self.readonly_fields


@admin.register(PaySlip)
class PaySlipAdmin(BaseModelAdmin):
    model = PaySlip
    fields = [('first_name', 'last_name', 'personnel_id'),
              ('department', 'working_place', 'contract_type', 'job_title'),
              ('basic_salary', 'overtime_working', 'insurance', 'tax'),
              ('gross_salary', 'deductions_sum', 'salary_net')]
    readonly_fields = ['gross_salary', 'deductions_sum', 'salary_net']
    list_display = ['year', 'month']
    list_display_links = ['year', 'month']
    list_filter = ['year', 'month']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return PaySlip.objects.all() if request.user.is_superuser else PaySlip.objects.filter(
            personnel_id=request.user.username)

    def get_list_display(self, request):
        return self.list_display + ['last_name', 'first_name', ] if request.user.is_superuser else self.list_display

    def get_list_display_links(self, request, list_display):
        return self.list_display_links + ['last_name',
                                          'first_name', ] if request.user.is_superuser else self.list_display_links

    def get_list_filter(self, request):
        return self.list_filter + ['last_name', 'first_name', ] if request.user.is_superuser else self.list_filter

    def get_search_fields(self, request):
        return ['last_name', 'first_name', ] if request.user.is_superuser else []

    def report(self, request, pk=None):
        payslip = PaySlip.objects.get(pk=pk)
        payslip.month = Month(payslip.month).label
        incomes_sum = payslip.gross_salary(),
        deductions_sum = payslip.deductions_sum(),
        net_salary = payslip.salary_net(),
        payslip.tax = payslip.tax
        payslip.insurance = locale.format("%d", payslip.insurance, grouping=True)
        incomes = []
        for item in [
            [PaySlip._meta.get_field('basic_salary').verbose_name, payslip.basic_salary],
            [PaySlip._meta.get_field('supplementary_allowance').verbose_name, payslip.supplementary_allowance],
            [PaySlip._meta.get_field('overtime').verbose_name, payslip.overtime],
            [PaySlip._meta.get_field('special_allowance').verbose_name, payslip.special_allowance],
            [PaySlip._meta.get_field('post_allowance').verbose_name, payslip.post_allowance],
            [PaySlip._meta.get_field('children_allowance').verbose_name, payslip.children_allowance],
            [PaySlip._meta.get_field('grocery_salary').verbose_name, payslip.grocery_salary],
            [PaySlip._meta.get_field('housing_salary').verbose_name, payslip.housing_salary],
            [PaySlip._meta.get_field('spouse_salary').verbose_name, payslip.spouse_salary],
            [PaySlip._meta.get_field('mobile_salary').verbose_name, payslip.mobile_salary],
            [PaySlip._meta.get_field('etc').verbose_name, payslip.etc],
            [PaySlip._meta.get_field('difference').verbose_name, payslip.difference],
            [PaySlip._meta.get_field('food_cost').verbose_name, payslip.food_cost], ]:
            if item[1] > 0:
                incomes.append([item[0], item[1]])

        context = dict(
            payslip=payslip,
            incomes=incomes,
            incomes_sum=incomes_sum,
            deductions_sum=deductions_sum,
            net_salary=net_salary,
            date=to_jalali(timezone.now()) if translation.get_language() == 'fa' else format_date(timezone.now())
        )
        return TemplateResponse(request, 'admin/custom/pay-slip.html', context)

    def get_urls(self):
        urls = super(PaySlipAdmin, self).get_urls()
        return [path('<int:pk>/report/', self.report, name="payslip-report"), ] + urls


@admin.register(BonusType)
class BonusTypeAdmin(BaseModelAdmin):
    model = BonusType
    fields = ['title', ]
    list_display = ['title', ]
    ordering = ['title', ]

    def get_fields(self, request, obj=None):
        user = request.user
        return self.fields + ['group', ] if user.is_superuser else self.fields

    def get_list_display(self, request):
        user = request.user
        return self.list_display + ['group', ] if user.is_superuser else self.list_display

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_queryset(self, request):
        queryset = super(BonusTypeAdmin, self).get_queryset(request)
        user = request.user

        if user.is_superuser:
            return queryset

        groups = user.get_groups(settings.HR_)
        return queryset.filter(group__name__in=groups)


@admin.register(BonusSubType)
class BonusSubTypeAdmin(BaseModelAdmin):
    model = BonusSubType
    fields = ['type', 'title']
    list_display = ['type', 'title', ]
    list_filter = ['type', ]
    ordering = ['type', 'title']

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_queryset(self, request):
        queryset = super(BonusSubTypeAdmin, self).get_queryset(request)
        user = request.user

        if user.is_superuser:
            return queryset

        groups = user.get_groups(settings.HR_)
        return queryset.filter(type__group__name__in=groups)

    def save_model(self, request, obj, form, change):
        user = request.user
        try:
            if not user.is_superuser:
                groups = user.get_groups(settings.HR_)
                if not obj.type.group.name in groups:
                    raise Exception(_('Bonus type not allowed.'))

            super(BonusSubTypeAdmin, self).save_model(request, obj, form, change)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    def get_field_queryset(self, db, db_field, request):
        user = request.user
        if not user.is_superuser and db_field.name == 'type':
            groups = user.get_groups(settings.HR_)
            queryset = super(BonusSubTypeAdmin, self).get_field_queryset(db, db_field, request)
            return queryset.filter(group__name__in=groups)
        return super(BonusSubTypeAdmin, self).get_field_queryset(db, db_field, request)


@admin.register(Bonus)
class BonusAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Bonus
    list_display = ['type', 'date', 'amount']
    list_filter = ['type', ]
    search_fields = ['type__title', 'description', 'user__username', 'user__first_name', 'user__last_name']

    def get_list_display(self, request):
        return self.list_display + ['user', ] if request.user.is_superuser else self.list_display

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)

    def get_list_filter(self, request):
        return self.list_filter + ['user', ] if request.user.is_superuser else self.list_filter

    def get_queryset(self, request):
        queryset = super(BonusAdmin, self).get_queryset(request)
        user = request.user

        if user.is_superuser:
            return queryset

        if user.is_group_member(settings.HR_OPERATOR_GROUP_NAME):
            groups = user.get_groups(settings.HR_)
            return queryset.filter(type__type__group__name__in=groups)
        else:
            return queryset.filter(user_id=user.pk)

    def save_model(self, request, obj, form, change):
        user = request.user
        try:
            if not user.is_superuser:
                groups = user.get_groups(settings.HR_)
                if not obj.type.type.group.name in groups:
                    raise Exception(_('Bonus type not allowed.'))

            super(BonusAdmin, self).save_model(request, obj, form, change)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            messages.error(request, e)

    def get_field_queryset(self, db, db_field, request):
        user = request.user
        if not user.is_superuser and db_field.name == 'type':
            groups = user.get_groups(settings.HR_)
            queryset = super(BonusAdmin, self).get_field_queryset(db, db_field, request)
            return queryset.filter(type__group__name__in=groups)
        return super(BonusAdmin, self).get_field_queryset(db, db_field, request)


@admin.register(PersonalInquiry)
class PersonalInquiryAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = PersonalInquiry
    queryset = PersonalInquiry.objects.all()
    fields = (('image', 'image_tag'),
              ('last_name', 'first_name', 'alias', 'national_code',),
              ('father_name', 'id_number', 'issue_place', 'marital_status',),
              ('_birthdate', 'birth_place', 'religion', 'personal_no',),
              ('educational_stage', 'email', 'postal_code', 'tel',),
              ('mobile', 'operator_name', 'cooperation_reason',),
              ('address', 'description', 'background',),
              )
    list_display = ['last_name', 'first_name', 'national_code', 'date', 'operator_name']
    list_filter = ['sex', get_jalali_filter('_date', _('Inquiry Date')), 'marital_status', 'educational_stage']
    readonly_fields = ['date', 'image_tag']
    search_fields = ['last_name', 'first_name', 'national_code', 'operator_name', 'id_number', 'personal_no',
                     'alias', 'cooperation_reason', 'mobile', 'email', 'description', 'address']
    inlines = [AttachmentInline]

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)
