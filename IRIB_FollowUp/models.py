import locale, os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from IRIB_FollowUpProject.utils import to_jalali
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

locale.setlocale(locale.LC_ALL, '')


def set_now():
    return timezone.now()


class AccessLevel(models.TextChoices):
    USER = 'user', _('User')
    SECRETARY = 'secretary', _('Secretary')


class Title(models.TextChoices):
    MR = 'Mr', _('Mr')
    MRS = 'Mrs', _('Mrs')


class Session(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class Attendant(models.Model):
    session = models.ForeignKey('Session', verbose_name=_('Session'), on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey('User', verbose_name=_('User'), on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _('Attendant')
        verbose_name_plural = _('Attendants')
        ordering = ['session__name', 'user__last_name', 'user__first_name']
        unique_together = ['session', 'user']

    def __str__(self):
        return '%s: %s' % (self.session, self.user)

    def __unicode__(self):
        return '%s: %s' % (self.session, self.user)


class Subject(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class Supervisor(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Supervisor Unit')
        verbose_name_plural = _('Supervisor Units')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


class User(AbstractUser):
    user_id = models.IntegerField(verbose_name=_('User ID'), blank=True, null=True)
    access_level = models.CharField(verbose_name=_('Access Level'), choices=AccessLevel.choices,
                                    default=AccessLevel.USER, max_length=20, null=False)
    _title = models.CharField(verbose_name=_('Title'), choices=Title.choices,
                              default=Title.MR, max_length=100, null=False)
    supervisor = models.ForeignKey('Supervisor', verbose_name=_('Supervisor Unit'), on_delete=models.SET_NULL,
                                   null=True)

    def last_login_jalali(self):
        return to_jalali(self.last_login)

    last_login_jalali.short_description = _('last login')

    def date_joined_jalali(self):
        return to_jalali(self.date_joined)

    date_joined_jalali.short_description = _('date joined')

    def __str__(self):
        return self.get_full_name() or self.get_username()

    def title(self):
        return Title(self._title).label

    @property
    def is_secretary(self):
        return self.access_level == AccessLevel.SECRETARY


class Enactment(models.Model):
    code = models.IntegerField(verbose_name=_('Code'), default=1, blank=False)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    subject = models.ForeignKey(Subject, verbose_name=_('Subject'), on_delete=models.SET_NULL, null=True)
    date = models.DateField(verbose_name=_('Assignment Date'), blank=False, default=set_now)
    follow_grade = models.CharField(verbose_name=_('Follow Grade'), max_length=100, blank=False, null=False, default=1)
    session = models.ForeignKey(Session, verbose_name=_('Session'), on_delete=models.SET_NULL, null=True)
    assigner = models.ForeignKey(User, verbose_name=_('Task Assigner'), on_delete=models.SET_NULL, null=True)
    review_date = models.DateField(verbose_name=_('Review Date'), blank=False, default=set_now)

    class Meta:
        verbose_name = _('Enactment')
        verbose_name_plural = _('Enactments')
        ordering = ['-review_date', 'id']

    def __str__(self):
        return '%s: %s' % (self.session, self.pk)

    def __unicode__(self):
        return '%s: %s' % (self.session, self.pk)

    def description_short(self):
        return '%s...' % self.description[:50] if self.description else ''

    description_short.short_description = _('Description')

    def row(self):
        return self.id if self.id else '-'

    row.short_description = _('Row')

    def date_jalali(self):
        return to_jalali(self.date)

    date_jalali.short_description = _('Assignment Date')
    date_jalali.admin_order_field = 'date'

    def review_date_jalali(self):
        return to_jalali(self.review_date)

    review_date_jalali.short_description = _('Review Date')
    review_date_jalali.admin_order_field = 'review_date'


class FollowUp(models.Model):
    actor = models.ForeignKey(User, verbose_name=_('Actor'), on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(verbose_name=_('Response Date'), blank=True, null=True)
    result = models.TextField(verbose_name=_('Result'), max_length=4000, blank=True, null=True)
    enactment = models.ForeignKey(Enactment, verbose_name=_('Enactment'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Follow Up')
        verbose_name_plural = _('Follow Ups')
        ordering = ['actor__last_name', 'actor__first_name']
        unique_together = ['actor', 'enactment']

    def __str__(self):
        return '%s: %s' % (self.enactment, self.actor)

    def __unicode__(self):
        return '%s: %s' % (self.enactment, self.actor)

    def date_jalali(self):
        return to_jalali(self.date)

    date_jalali.short_description = _('Response Date')
    date_jalali.admin_order_field = 'date'

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
