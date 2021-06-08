import locale
from django.urls import path
from django.contrib import admin
from IRIB_Shared_Lib.models import Month
from .models import PaySlip, BonusType, Bonus
from django.utils import timezone, translation
from IRIB_Shared_Lib.admin import BaseModelAdmin
from jalali_date.admin import ModelAdminJalaliMixin
from django.template.response import TemplateResponse
from IRIB_Shared_Lib.utils import to_jalali, format_date

# Used for thousands separator for numbers... usage: f'{value:n}'
locale.setlocale(locale.LC_ALL, '')


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


@admin.register(Bonus)
class BonusAdmin(ModelAdminJalaliMixin, BaseModelAdmin):
    model = Bonus
    list_display = ['type', 'date', 'amount']
    list_display_links = ['type', 'date', 'amount']
    list_filter = ['type']

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        return Bonus.objects.all() if request.user.is_superuser else Bonus.objects.filter(
            user_id=request.user.pk)

    def get_list_display(self, request):
        return self.list_display + ['user',] if request.user.is_superuser else self.list_display

    def get_list_display_links(self, request, list_display):
        return self.list_display_links + ['user', ] if request.user.is_superuser else self.list_display_links

    def get_list_filter(self, request):
        return self.list_filter + ['user', ] if request.user.is_superuser else self.list_filter
