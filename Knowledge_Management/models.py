from django.db import models
from django.conf import settings
from django.utils import translation
from IRIB_FollowUp.models import User
from django.utils.translation import ugettext_lazy as _
from IRIB_FollowUpProject.utils import to_jalali, set_now, format_date


class ActivityStatus(models.TextChoices):
    DR = 'DRAFT', _('Draft')
    NW = 'NEW', _('New')
    AC = 'ACCEPTED', _('Accepted')
    RJ = 'REJECTED', _('Rejected')
    CN = 'CONDITIONAL', _('Conditional')
    AP = 'APPROVED', _('Approved')


class Category(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Knowledge Category')
        verbose_name_plural = _('Knowledge Categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False)
    category = models.ForeignKey(Category, verbose_name=_('Category'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Knowledge Sub-Category')
        verbose_name_plural = _('Knowledge Sub-Categories')
        ordering = ['category', 'name']
        unique_together = ['name', 'category']

    def __str__(self):
        return '%s: %s' % (self.category, self.name)

    def __unicode__(self):
        return '%s: %s' % (self.category, self.name)


class Activity(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)
    max_score = models.IntegerField(verbose_name=_('Maximum Score'), default=10, blank=False)
    limit = models.IntegerField(verbose_name=_('Limit'), default=1, blank=False)

    class Meta:
        verbose_name = _('Knowledge Activity')
        verbose_name_plural = _('Knowledge Activities')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class CommitteeMember(models.Model):
    user = models.OneToOneField(User, verbose_name=_('User'), on_delete=models.CASCADE, unique=True)
    chairman = models.BooleanField(verbose_name=_('Chairman'), default=False)

    class Meta:
        verbose_name = _('Committee Member')
        verbose_name_plural = _('Committee Members')

    def __str__(self):
        return self.user.__str__()

    def __unicode__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        if self.chairman:
            for cm in CommitteeMember.objects.all():
                if cm.pk != self.pk:
                    cm.chairman = False
                    cm.save()
        return super(CommitteeMember, self).save(*args, **kwargs)

    @staticmethod
    def is_committee_member(user):
        return CommitteeMember.objects.filter(user=user).count() > 0


class Indicator(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Indicator')
        verbose_name_plural = _('Indicators')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ActivityIndicator(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=_('Activity'), on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, verbose_name=_('Indicator'), on_delete=models.CASCADE)
    weight = models.IntegerField(verbose_name=_('Weight'), default=1, blank=False)

    class Meta:
        verbose_name = _('Activity Indicator')
        verbose_name_plural = _('Activity Indicators')
        ordering = ['activity', 'indicator']
        unique_together = ['activity', 'indicator']

    def __str__(self):
        return '%s: %s' % (self.activity, self.indicator)

    def __unicode__(self):
        return '%s: %s' % (self.activity, self.indicator)


class CardtableBase(models.Model):
    activity = models.ForeignKey(Activity, verbose_name=_('Activity'), on_delete=models.SET_NULL, null=True)
    _date = models.DateTimeField(verbose_name=_('Creation Date'), blank=False, default=set_now)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    user = models.ForeignKey(User, verbose_name=_('Knowledge User'), on_delete=models.SET_NULL, null=True)
    _status = models.CharField(verbose_name=_('Status'), choices=ActivityStatus.choices,
                               default=ActivityStatus.DR, max_length=30, null=False)

    class Meta:
        verbose_name = _('Cardtable Base')
        verbose_name_plural = _('Cardtable Bases')
        ordering = ['activity']

    def __str__(self):
        return '%s: %s' % (self.activity, self.date())

    def __unicode__(self):
        return self.__str__()

    def row(self):
        return self.pk or '-'

    row.short_description = _('Row')
    row.admin_order_field = 'id'

    def max_score(self):
        return self.activity.max_score if self.activity else 0

    max_score.short_description = _('Maximum Score')

    def score(self):
        score = 0
        assessments = ActivityAssessment.objects.filter(cardtable=self)
        for assessment in assessments:
            score += assessment.score()
        return round(score / assessments.count()) if assessments.count() > 0 else 0

    score.short_description = _('Score')

    def limit(self):
        return self.activity.limit if self.activity else 0

    limit.short_description = _('Limit')

    def quantity(self):
        return CardtableBase.objects.filter(user=self.user, activity=self.activity, _date__year=self._date.year,
                                            _status=ActivityStatus.DR).count()

    quantity.short_description = _('Quantity')

    def date(self):
        return to_jalali(self._date) if translation.get_language() == 'fa' else format_date(self._date)

    date.short_description = _('Creation Date')
    date.admin_order_field = 'date'

    def status(self):
        return ActivityStatus(self._status).label

    status.short_description = _('Status')
    status.admin_order_field = '_status'


class PersonalCardtable(CardtableBase):
    class Meta:
        verbose_name = _('Personal Cardtable')
        verbose_name_plural = _('Personal Cardtables')
        proxy = True


class AssessmentCardtable(CardtableBase):
    class Meta:
        verbose_name = _('Assessment Cardtable')
        verbose_name_plural = _('Assessment Cardtables')
        proxy = True


class FinancialCardtable(CardtableBase):
    class Meta:
        verbose_name = _('Financial Cardtable')
        verbose_name_plural = _('Financial Cardtables')
        proxy = True


class Attachment(models.Model):
    def directory_path(instance, filename):
        return '{0}/{1}/{2}'.format(settings.MEDIA_ROOT, instance.cardtable.pk, filename)

    description = models.CharField(verbose_name=_('Description'), max_length=2000, blank=True, null=True)
    file = models.FileField(verbose_name=_('File'), upload_to=directory_path, blank=False)
    cardtable = models.ForeignKey(CardtableBase, verbose_name=_('Personal Cardtable'), on_delete=models.CASCADE)

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


class ActivityAssessment(models.Model):
    member = models.ForeignKey(CommitteeMember, verbose_name=_('Committee Member'), on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_('Assessment Date'), blank=True, null=True)
    scores = models.CharField(verbose_name=_('Scores'), blank=True, null=True, max_length=1000)
    description = models.TextField(verbose_name=_('Description'), max_length=2000, blank=True, null=True)
    cardtable = models.ForeignKey(CardtableBase, verbose_name=_('Personal Cardtable'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Activity Assessment')
        verbose_name_plural = _('Activity Assessments')
        unique_together = ['cardtable', 'member']
        ordering = ['cardtable', 'member']

    def __str__(self):
        return '%s: %s' % (self.cardtable, self.member)

    def __unicode__(self):
        return '%s: %s' % (self.cardtable, self.member)

    def date_jalali(self):
        return to_jalali(self.date)

    date_jalali.short_description = _('Assessment Date')
    date_jalali.admin_order_field = 'date'

    def score(self):
        score = 0
        if self.scores:
            scores = self.scores.split(',')
            indicators = self.cardtable.activity.activityindicator_set.all()
            for index in range(indicators.count()):
                score += int(scores[index]) * indicators[index].weight
            score /= sum(indicator.weight for indicator in indicators)
        return round(score, 0)

    score.short_description = _('Score')
