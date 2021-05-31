from django.db import models
from IRIB_Shared_Lib.models import Month
from django.utils.translation import ugettext_lazy as _


class PaySlip(models.Model):
    month = models.CharField(verbose_name=_('Month'), choices=Month.choices, default=Month.FARVARDIN, max_length=30)
    year = models.IntegerField(verbose_name=_('Year'), blank=False, default=99)
    first_name = models.CharField(_('first name'), max_length=200, blank=True)
    last_name = models.CharField(_('last name'), max_length=200, blank=True)
    national_id = models.CharField(_('National ID'), max_length=20, blank=True)
    personnel_id = models.CharField(_('Personnel ID'), max_length=20, blank=True)
    account_no = models.CharField(_('Account Number'), max_length=50, blank=True)
    insurance_no = models.CharField(_('Insurance Number'), max_length=50, blank=True)
    department = models.CharField(_('Department'), max_length=200, blank=True)
    working_place = models.CharField(_('Working Place'), max_length=200, blank=True)
    job_title = models.CharField(_('Job Title'), max_length=200, blank=True)
    contract_type = models.CharField(_('Contract Type'), max_length=200, blank=True)
    basic_salary = models.IntegerField(_('Basic Salary'), blank=False, default=0)
    supplementary_allowance = models.IntegerField(_('Supplementary Allowance'), blank=False, default=0)
    operation = models.IntegerField(_('Operation'), blank=False, default=0)
    overtime_working = models.IntegerField(_('Overtime Working'), blank=False, default=0)
    overtime = models.IntegerField(_('Overtime'), blank=False, default=0)
    special_allowance = models.IntegerField(_('Special Allowance'), blank=False, default=0)
    post_allowance = models.IntegerField(_('Post Allowance'), blank=False, default=0)
    children_allowance = models.IntegerField(_('Children Allowance'), blank=False, default=0)
    etc = models.IntegerField(_('etc'), blank=False, default=0)
    difference = models.IntegerField(_('Difference'), blank=False, default=0)
    grocery_salary = models.IntegerField(_('Grocery Allowance'), blank=False, default=0)
    housing_salary = models.IntegerField(_('Housing Allowance'), blank=False, default=0)
    spouse_salary = models.IntegerField(_('Spouse Allowance'), blank=False, default=0)
    mobile_salary = models.IntegerField(_('Mobile  Allowance'), blank=False, default=0)
    food_cost = models.IntegerField(_('Food Cost'), blank=False, default=0)
    insurance = models.IntegerField(_('Insurance'), blank=False, default=0)
    tax = models.IntegerField(_('Tax'), blank=False, default=0)
    loan_installments = models.IntegerField(_('Loan Installments'), blank=False, default=0)
    supplementary_insurance = models.IntegerField(_('Supplementary Insurance'), blank=False, default=0)
    leave_balance = models.IntegerField(_('Leave Balance'), blank=False, default=0)
    atieh_balance = models.IntegerField(_('Atieh Fund Balance'), blank=False, default=0)
    refah_balance = models.IntegerField(_('Refah Fund Balance'), blank=False, default=0)

    class Meta:
        verbose_name = _('Pay Slip')
        verbose_name_plural = _('Pay Slips')
        ordering = ['year', 'month']

    def __str__(self):
        return '%s %s (%s %s)' % (self.last_name, self.first_name, Month(self.month).label, self.year)

    def __unicode__(self):
        return self.__str__()

    def date(self):
        return '%s%s' % (self.year, self.month)

    date.short_description = _('Date')
    date.admin_order_field = '_date'

    def gross_salary(self):
        return self.basic_salary + self.supplementary_allowance + self.overtime + self.special_allowance + \
               self.post_allowance + self.children_allowance + self.grocery_salary + self.housing_salary + \
               self.spouse_salary + self.mobile_salary + self.etc + self.difference + self.food_cost

    gross_salary.short_description = _('Gross Salary')

    def deductions_sum(self):
        return self.tax + self.insurance + self.loan_installments

    deductions_sum.short_description = _('Total deductions')

    def salary_net(self):
        return self.gross_salary() - self.deductions_sum()

    salary_net.short_description = _('Net Salary')
