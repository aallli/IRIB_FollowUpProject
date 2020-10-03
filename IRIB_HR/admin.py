import locale

from .models import PaySlip
from django.urls import path
from django.contrib import admin
from .utils import get_excel_sheet
from IRIB_Shared_Lib.models import Month
from django.utils import timezone, translation
from IRIB_Shared_Lib.admin import BaseModelAdmin
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
    list_filter = ['year']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        user = None if request.user.is_superuser else request.user
        for payment in self.get_payment(user):
            try:
                kwargs = dict(
                    month=Month(str(int(payment[30]))[2:4]),
                    year=str(int(payment[30]))[:2],
                    first_name=payment[2],
                    last_name=payment[1],
                    personnel_id=int(payment[0]),
                    account_no='-',
                    insurance_no='-',
                    department=payment[28],
                    working_place=payment[27],
                    job_title='-',
                    basic_salary=payment[6],
                    supplementary_allowance=payment[9],
                    operation=payment[3],
                    overtime_working=payment[4],
                    overtime=payment[10],
                    special_allowance=payment[7],
                    post_allowance=int(payment[8]) + int(payment[14]) + int(payment[17]),
                    children_allowance=payment[12],
                    etc=int(payment[16]),
                    grocery_salary=0,
                    housing_salary=payment[15],
                    spouse_salary=payment[13],
                    mobile_salary=0,
                    food_cost=payment[11],
                    insurance=payment[18],
                    tax=payment[19],
                    loan_installments=int(payment[20]),
                    supplementary_insurance=0,
                    contract_type=payment[26],
                    leave_balance=0,
                    atieh_balance=0,
                    refah_balance=0,
                )

                try:
                    kwargs['national_id'] = str(int(kwargs['national_id']))
                except:
                    pass

                try:
                    kwargs['personnel_id'] = str(int(kwargs['personnel_id']))
                except:
                    pass

                try:
                    kwargs['account_no'] = str(int(kwargs['account_no']))
                except:
                    pass

                try:
                    kwargs['insurance_no'] = str(int(kwargs['insurance_no']))
                except:
                    pass

                payslip = PaySlip.objects.filter(personnel_id=kwargs['personnel_id'], month=kwargs['month'],
                                                 year=kwargs['year'])
                if payslip.count() == 1:
                    payslip = payslip[0]
                    payslip.first_name = kwargs['first_name']
                    payslip.last_name = kwargs['last_name']
                    payslip.personnel_id = kwargs['personnel_id']
                    payslip.account_no = kwargs['account_no']
                    payslip.insurance_no = kwargs['insurance_no']
                    payslip.department = kwargs['department']
                    payslip.working_place = kwargs['working_place']
                    payslip.job_title = kwargs['job_title']
                    payslip.basic_salary = kwargs['basic_salary']
                    payslip.supplementary_allowance = kwargs['supplementary_allowance']
                    payslip.operation = kwargs['operation']
                    payslip.overtime_working = kwargs['overtime_working']
                    payslip.overtime = kwargs['overtime']
                    payslip.special_allowance = kwargs['special_allowance']
                    payslip.post_allowance = kwargs['post_allowance']
                    payslip.children_allowance = kwargs['children_allowance']
                    payslip.etc = kwargs['etc']
                    payslip.grocery_salary = kwargs['grocery_salary']
                    payslip.housing_salary = kwargs['housing_salary']
                    payslip.spouse_salary = kwargs['spouse_salary']
                    payslip.mobile_salary = kwargs['mobile_salary']
                    payslip.food_cost = kwargs['food_cost']
                    payslip.insurance = kwargs['insurance']
                    payslip.tax = kwargs['tax']
                    payslip.loan_installments = kwargs['loan_installments']
                    payslip.supplementary_insurance = kwargs['supplementary_insurance']
                    payslip.contract_type = kwargs['contract_type']
                    payslip.leave_balance = kwargs['leave_balance']
                    payslip.atieh_balance = kwargs['atieh_balance']
                    payslip.refah_balance = kwargs['refah_balance']
                else:
                    payslip = PaySlip.objects.create(**kwargs)

                payslip.save()
            except:
                pass

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

    def get_payment(self, user):
        try:
            payments = []
            sheet = get_excel_sheet()
            for i in range(1, sheet.nrows):
                try:
                    value = str(int(sheet.cell_value(i, 0)))
                except:
                    value = ''

                if not user or value == user.username:
                    # date filter: and str( int(sheet.cell_value(i, sheet.ncols - 1))) == str(date)
                    payments.append(sheet.row_values(i))
            return payments
        except:
            return None

    def report(self, request, pk=None):
        payslip = PaySlip.objects.get(pk=pk)
        payslip.month = Month(payslip.month).label
        incomes_sum = locale.format("%d", payslip.gross_salary(), grouping=True),
        deductions_sum = locale.format("%d", payslip.deductions_sum(), grouping=True),
        net_salary = locale.format("%d", payslip.salary_net(), grouping=True),
        payslip.tax = locale.format("%d", payslip.tax, grouping=True)
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
            [PaySlip._meta.get_field('food_cost').verbose_name, payslip.food_cost], ]:
            if item[1] > 0:
                incomes.append([item[0], f'{item[1]:n}'])

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
