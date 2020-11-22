import os
import locale
from django.db import models
from django.conf import settings
from django.utils import timezone
from IRIB_Auth.models import User
from django.dispatch import receiver
from django.utils import translation
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from IRIB_Shared_Lib.utils import to_jalali, format_date

locale.setlocale(locale.LC_ALL, '')


def set_now():
    return timezone.now()


class AccessLevel(models.TextChoices):
    USER = 'user', _('User')
    SECRETARY = 'secretary', _('Secretary')


class Title(models.TextChoices):
    MR = 'Mr', _('Mr')
    MRS = 'Mrs', _('Mrs')


class EnactmentType(models.TextChoices):
    AG = 'AGENDA', _('Agenda')
    EN = 'ENACTMENT', _('Enactment')
    FI = 'FOR_INFORMATION', _('For Information')
    RG = 'REGULATIONS', _('Regulations')


class SessionBase(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Meeeting')
        verbose_name_plural = _('Meeetings')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class Session(models.Model):
    session = models.ForeignKey(SessionBase, verbose_name=_('Meeeting'), on_delete=models.CASCADE, blank=False)
    _date = models.DateTimeField(verbose_name=_('Attended Date'), blank=False, default=set_now)

    class Meta:
        verbose_name = _('Minute')
        verbose_name_plural = _('Minutes')
        ordering = ['session__name', '_date']

    def __str__(self):
        return '%s (%s)' % (self.session.name, self.date())

    def __unicode__(self):
        return self.__str__()

    def date(self):
        return to_jalali(self._date) if translation.get_language() == 'fa' else format_date(self._date)

    date.short_description = _('Attended Date')
    date.admin_order_field = '_date'

    def presents(self):
        if self.pk:
            presents = ''
            for member in Member.objects.filter(session=self.session):
                if Attendant.objects.filter(user=member.user, session=self).count() != 0:
                    if member.user:
                        presents += '%s, ' % member.user
            return presents[0: presents.__len__() - 2] if presents else _('All absent')
        else:
            return '-'

    presents.short_description = _('Presents')

    def absents(self):
        if self.pk:
            absents = ''
            for member in Member.objects.filter(session=self.session):
                if Attendant.objects.filter(user=member.user, session=self).count() == 0:
                    if member.user:
                        absents += '%s, ' % member.user
            return absents[0: absents.__len__() - 2] if absents else _('All ready')
        else:
            return '-'

    absents.short_description = _('Absents')


class Attendant(models.Model):
    session = models.ForeignKey(Session, verbose_name=_('Minute'), on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Attendant')
        verbose_name_plural = _('Attendants')
        ordering = ['session__session__name', 'user__last_name', 'user__first_name']
        unique_together = ['session', 'user']

    def __str__(self):
        return '%s: %s' % (self.session, self.user)

    def __unicode__(self):
        return self.__str__()


class Member(models.Model):
    session = models.ForeignKey(SessionBase, verbose_name=_('Session'), on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        ordering = ['session__name', 'user__last_name', 'user__first_name']
        unique_together = ['session', 'user']

    def __str__(self):
        return '%s: %s' % (self.session, self.user)

    def __unicode__(self):
        return self.__str__()


class Subject(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return self.__str__()


class Enactment(models.Model):
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    subject = models.ForeignKey(Subject, verbose_name=_('Subject'), on_delete=models.SET_NULL, null=True)
    follow_grade = models.CharField(verbose_name=_('Follow Grade'), max_length=100, blank=False, null=False, default=1)
    session = models.ForeignKey(Session, verbose_name=_('Minute'), on_delete=models.SET_NULL, null=True)
    assigner = models.ForeignKey(User, verbose_name=_('Task Assigner'), on_delete=models.SET_NULL, null=True)
    _review_date = models.DateTimeField(verbose_name=_('Review Date'), blank=False, default=set_now)
    _type = models.CharField(verbose_name=_('Type'), choices=EnactmentType.choices,
                             default=EnactmentType.FI, max_length=30, null=False)

    class Meta:
        verbose_name = _('Enactment')
        verbose_name_plural = _('Enactments')
        ordering = ['-_review_date', 'session', 'subject', 'id']

    def __str__(self):
        return '%s: %s' % (self.session, self.pk)

    def __unicode__(self):
        return self.__str__()

    def description_short(self):
        return '%s...' % self.description[:50] if self.description else ''

    description_short.short_description = _('Description')
    description_short.admin_order_field = 'description'

    def type(self):
        return EnactmentType(self._type).label

    type.short_description = _('Type')
    type.admin_order_field = '_type'

    def row(self):
        return self.id if self.id else '-'

    row.short_description = _('Row')
    row.admin_order_field = 'id'

    def review_date(self):
        return to_jalali(self._review_date) if translation.get_language() == 'fa' else format_date(self._review_date)

    review_date.short_description = _('Review Date')
    review_date.admin_order_field = '_review_date'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self._review_date = timezone.now()
        super(Enactment, self).save(force_insert, force_update, using, update_fields)

    def session_date(self):
        return self.session.date()

    session_date.short_description = _('Attended Date')
    session_date.admin_order_field = 'session___date'

    def session_absents(self):
        return self.session.absents()

    session_absents.short_description = _('Absents')

    def session_presents(self):
        return self.session.presents()

    session_presents.short_description = _('Presents')

    def followups(self):
        return ', '.join(followup.actor.full_titled_name() for followup in FollowUp.objects.filter(enactment=self))

    followups.short_description = _('Follow Ups')

    def status_colored(self):
        status = 'Done' if FollowUp.objects.filter(enactment=self).filter(result='').count() == 0 else 'TODO'
        colors = {
            'Done': 'green',
            'TODO': 'red',
        }
        return format_html(
            '<b style="color:{};">{}</b>',
            colors[status],
            _(status),
        )

    status_colored.short_description = _('Status')


class FollowUp(models.Model):
    actor = models.ForeignKey(User, verbose_name=_('Actor'), on_delete=models.SET_NULL, blank=True, null=True)
    _date = models.DateTimeField(verbose_name=_('Response Date'), blank=True, null=True)
    result = models.TextField(verbose_name=_('Result'), max_length=4000, blank=False, null=False, default='')
    enactment = models.ForeignKey(Enactment, verbose_name=_('Enactment'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Follow Up')
        verbose_name_plural = _('Follow Ups')
        ordering = ['actor__last_name', 'actor__first_name']
        unique_together = ['actor', 'enactment']

    def __str__(self):
        return '%s: %s' % (self.enactment, self.actor)

    def __unicode__(self):
        return self.__str__()

    def date(self):
        return to_jalali(self._date) if translation.get_language() == 'fa' else format_date(self._date)

    date.short_description = _('Response Date')
    date.admin_order_field = 'date'

    def supervisor(self):
        return self.actor.supervisor or '-'

    supervisor.short_description = _('Supervisor Unit')


class Attachment(models.Model):
    def directory_path(instance, filename):
        return '{0}/{1}/{2}'.format(settings.MEDIA_ROOT, instance.enactment.pk, filename)

    description = models.CharField(verbose_name=_('Description'), max_length=2000, blank=True, null=True)
    file = models.FileField(verbose_name=_('File'), upload_to=directory_path, blank=False)
    enactment = models.ForeignKey(Enactment, verbose_name=_('Enactment'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
        ordering = ['description']

    def __str__(self):
        return self.filename()

    def __unicode__(self):
        return self.__str__()

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


class Group(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=200, blank=False, unique=True)

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class GroupUser(models.Model):
    group = models.ForeignKey(Group, verbose_name=_('Group'), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Group User')
        verbose_name_plural = _('Group Users')
        ordering = ['group', 'user']
        unique_together = ['group', 'user']

    def __str__(self):
        return '%s: %s' % (self.group, self.user)

    def __unicode__(self):
        return self.__str__()


class GroupFollowUp(models.Model):
    group = models.ForeignKey(Group, verbose_name=_('Group'), on_delete=models.CASCADE)
    enactment = models.ForeignKey(Enactment, verbose_name=_('Enactment'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Group FollowUp')
        verbose_name_plural = _('Group FollowUps')

    def __str__(self):
        return '%s: %s' % (self.group, self.enactment)

    def __unicode__(self):
        return self.__str__()
