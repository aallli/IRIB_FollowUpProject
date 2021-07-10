import os
from django.db import models
from django.conf import settings
from django.utils import translation
from django.dispatch import receiver
from django.utils.html import mark_safe
from IRIB_Shared_Lib.models import Month
from django_resized import ResizedImageField
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from IRIB_Shared_Lib.utils import to_jalali, format_date, set_now
from IRIB_Auth.models import User, MaritalStatus, EducationLevel, Sex


class Vote(models.TextChoices):
    AP = 'approved', _('Approved')
    RJ = 'rejected', _('Rejected')
    CN = 'conditional', _('Conditional Approve')
    PN = 'pending', _('Pending')


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


class BonusType(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=200, blank=False, unique=True)
    group = models.ForeignKey(Group, verbose_name=_('Allowed Group'), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = _('Bonus Type')
        verbose_name_plural = _('Bonus Types')
        ordering = ['title']

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.__str__()


class BonusSubType(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=200, blank=False)
    type = models.ForeignKey(BonusType, verbose_name=_('Bonus Type'), on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = _('Bonus Sub Type')
        verbose_name_plural = _('Bonus Sub Types')
        ordering = ['type', 'title']
        unique_together = ['title', 'type']

    def __str__(self):
        return '%s - %s' % (self.type, self.title)

    def __unicode__(self):
        return self.__str__()


class Bonus(models.Model):
    type = models.ForeignKey(BonusSubType, verbose_name=_('Type'), on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.SET_NULL, blank=True, null=True)
    _date = models.DateField(verbose_name=_('Pay Date'), blank=False)
    amount = models.IntegerField(_('Amount'), blank=False, default=0)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)

    class Meta:
        verbose_name = _('Bonus')
        verbose_name_plural = _('Bonuses')
        ordering = ['type', 'user', '_date']

    def __str__(self):
        return '%s - %s (%s)' % (self.type, self.user, self.date())

    def __unicode__(self):
        return self.__str__()

    def date(self):
        return to_jalali(self._date) if translation.get_language() == 'fa' else format_date(self._date)

    date.short_description = _('Pay Date')
    date.admin_order_field = 'date'


class PersonalInquiry(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, blank=False, null=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null=False)
    father_name = models.CharField(_('father name'), max_length=30, blank=True, null=True)
    id_number = models.CharField(_('ID number'), max_length=30, blank=True, null=True)
    issue_place = models.CharField(_('issue place'), max_length=30, blank=True, null=True)
    _date = models.DateField(verbose_name=_('inquiry date'), blank=False, default=set_now)
    _birthdate = models.DateField(verbose_name=_('birthdate'), blank=True, null=True)
    birth_place = models.CharField(_('birth place'), max_length=30, blank=True, null=True)
    religion = models.CharField(_('religion'), max_length=30, blank=True, null=True)
    personal_no = models.CharField(_('personal number'), max_length=10, blank=True, null=True)
    national_code = models.CharField(_('National ID'), max_length=10, blank=True, null=True)
    alias = models.CharField(_('alias'), max_length=30, blank=True, null=True)
    marital_status = models.CharField(verbose_name=_('marital status'), choices=MaritalStatus.choices,
                                      default=MaritalStatus.SG, max_length=30, null=False)
    cooperation_reason = models.CharField(verbose_name=_('cooperation reason'), max_length=255, blank=True, null=True)
    educational_stage = models.CharField(verbose_name=_('educational stage'), choices=EducationLevel.choices,
                                         default=EducationLevel.UP, max_length=50, blank=True, null=True)
    email = models.EmailField(_('Email address'), blank=True, null=True)
    mobile = models.CharField(_('Mobile no.'), max_length=13, blank=True, null=True, help_text=settings.MOBILE_VALIDATORS[0].message, validators=settings.MOBILE_VALIDATORS)
    tel = models.CharField(_('Tel'), max_length=13, blank=True, null=True)
    sex = models.CharField(verbose_name=_('Sex'), choices=Sex.choices, default=Sex.MALE, max_length=10, null=False)
    postal_code = models.CharField(_('postal code'), max_length=10, blank=True, null=True)
    address = models.TextField(verbose_name=_('Address'), max_length=4000, blank=True, null=True)
    operator_name = models.CharField(_('operator name'), max_length=255, blank=True, null=True)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    background = models.TextField(verbose_name=_('job background'), max_length=4000, blank=True, null=True)
    image = ResizedImageField(size=[settings.MAX_SMALL_IMAGE_WIDTH, settings.MAX_SMALL_IMAGE_HEIGHT],
                              verbose_name=_('Image'), upload_to='uploads/user-images/', blank=True, null=True)
    operator_vote = models.TextField(verbose_name=_('Operator Vote'), choices=Vote.choices, default=Vote.PN, max_length=20, null=False)
    operator_note = models.TextField(verbose_name=_('Operator Note'), max_length=2000, blank=True, null=True)
    security_vote = models.TextField(verbose_name=_('Security Vote'), choices=Vote.choices, default=Vote.PN, max_length=20, null=False)
    security_note = models.TextField(verbose_name=_('Security Note'), max_length=2000, blank=True, null=True)
    final_vote = models.TextField(verbose_name=_('Final Vote'), choices=Vote.choices, default=Vote.PN, max_length=20, null=False)
    final_note = models.TextField(verbose_name=_('Final Note'), max_length=2000, blank=True, null=True)

    class Meta:
        verbose_name = _('Personal Inquiry')
        verbose_name_plural = _('Personal Inquiries')
        ordering = ['_date', 'last_name', 'first_name', ]

    def __str__(self):
        return '%s - %s (%s)' % (self.last_name, self.first_name, self.date())

    def __unicode__(self):
        return self.__str__()

    def date(self):
        return to_jalali(self._date) if translation.get_language() == 'fa' else format_date(self._date)

    date.short_description = _('Inquiry Date')
    date.admin_order_field = 'date'

    def birthdate(self):
        return to_jalali(self._birthdate) if translation.get_language() == 'fa' else format_date(self._birthdate)

    birthdate.short_description = _('birthdate')
    birthdate.admin_order_field = 'birthdate'

    def image_tag(self):
        if self.image:
            return mark_safe(
                '<a href="%s%s" target="_blank"><img src="%s%s" title="%s" alt="%s" style="max-width:%spx;max-height:%spx;"/></a>' % (
                    settings.MEDIA_URL, self.image, settings.MEDIA_URL, self.image, self, self,
                    settings.MAX_SMALL_IMAGE_WIDTH, settings.MAX_SMALL_IMAGE_HEIGHT))
        else:
            return mark_safe('<img src="%simg/person-icon.jpg" width="150" height="150" title="%s" alt="%s"/>' % (
                settings.STATIC_URL, self.get_full_name(), self.get_full_name()))

    image_tag.short_description = _('Image')


class Attachment(models.Model):
    def directory_path(instance, filename):
        return '{0}/personal_inquiry/{1}/{2}'.format(settings.MEDIA_ROOT, instance.personal_inquiry.pk, filename)

    description = models.CharField(verbose_name=_('Description'), max_length=2000, blank=True, null=True)
    file = models.FileField(verbose_name=_('File'), upload_to=directory_path, blank=False)
    personal_inquiry = models.ForeignKey(PersonalInquiry, verbose_name=_('Personal Inquiry'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
        ordering = ['description']

    def __str__(self):
        return self.filename()

    def __unicode__(self):
        return self.filename()

    def filename(self):
        parts = self.file.name.split('/')
        return parts[len(parts) - 1]


@receiver(models.signals.post_delete, sender=Attachment)
def auto_delete_attachment_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Attachment` object is deleted.
    """
    if instance.file.name:
        try:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
        except Exception as e:
            print('Delete error: %s' % e.args[0])


@receiver(models.signals.pre_save, sender=Attachment)
def auto_delete_attachment_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Attachment` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Attachment.objects.get(pk=instance.pk).file
    except Attachment.DoesNotExist:
        return False

    if not old_file.name:
        return False

    new_file = instance.file
    try:
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Exception as e:
        print('Delete error: %s' % e.args[0])
        return False
