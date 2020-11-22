import os
import locale
from django.db import models
from django.conf import settings
from IRIB_Auth.models import User
from django.dispatch import receiver
from django.utils import translation
from django.utils.html import format_html
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _
from IRIB_Shared_Lib.utils import to_jalali, set_now, format_date

locale.setlocale(locale.LC_ALL, '')


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


class Assigner(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Task Assigner')
        verbose_name_plural = _('Task Assigners')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return _(self.name).__str__()


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


class Actor(models.Model):
    fname = models.CharField(verbose_name=_('First Name'), max_length=2000, blank=True, null=True)
    lname = models.CharField(verbose_name=_('Last Name'), max_length=2000, blank=False)
    supervisor = models.ForeignKey('Supervisor', verbose_name=_('Supervisor Unit'), on_delete=models.SET_NULL,
                                   null=True)

    class Meta:
        verbose_name = _('Supervisor')
        verbose_name_plural = _('Supervisors')
        ordering = ['lname', 'fname']
        unique_together = ['lname', 'fname']

    def __str__(self):
        return '%s, %s' % (self.lname, self.fname if self.fname else '-')

    def __unicode__(self):
        return '%s, %s' % (self.lname, self.fname if self.fname else '-')


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


class User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    query_name = models.CharField(verbose_name=_('Query Name'), max_length=200, blank=False)
    query = ArrayField(models.IntegerField(verbose_name=_('Code'), default=0, blank=False), size=100000, null=True,
                       blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.user.__str__()

    def __unicode__(self):
        return self.__str__()

    def username(self):
        return self.user.username

    username.short_description = _('username')

    def first_name(self):
        return self.user.first_name

    first_name.short_description = _('First Name')

    def last_name(self):
        return self.user.last_name

    last_name.short_description = _('Last Name')

    def access_level(self):
        return self.user.access_level

    access_level.short_description = _('Access Level')

    def supervisor(self):
        return self.user.supervisor.name if self.user.supervisor else ''

    supervisor.short_description = _('Supervisor Unit')

    def last_login_jalali(self):
        return self.user.last_login_jalali()

    last_login_jalali.short_description = _('last login')
    last_login_jalali.admin_order_field = 'last_login'


class Enactment(models.Model):
    row = models.IntegerField(verbose_name=_('Row'), default=1, blank=False, unique=True)
    code = models.IntegerField(verbose_name=_('Code'), default=1, blank=False)
    description = models.TextField(verbose_name=_('Description'), max_length=4000, blank=True, null=True)
    subject = models.ForeignKey(Subject, verbose_name=_('Subject'), on_delete=models.SET_NULL, null=True)
    first_actor = models.ForeignKey(Actor, verbose_name=_('First Actor'), on_delete=models.SET_NULL, blank=True,
                                    null=True, related_name='first_actor')
    second_actor = models.ForeignKey(Actor, verbose_name=_('Second Actor'), on_delete=models.SET_NULL, blank=True,
                                     null=True, related_name='second_actor')
    _date = models.DateTimeField(verbose_name=_('Assignment Date'), blank=False, default=set_now)
    follow_grade = models.CharField(verbose_name=_('Follow Grade'), max_length=100, blank=True, null=True)
    result = models.TextField(verbose_name=_('Result'), max_length=4000, blank=False, null=False, default='')
    session = models.ForeignKey(Session, verbose_name=_('Session'), on_delete=models.SET_NULL, null=True)
    assigner = models.ForeignKey(Assigner, verbose_name=_('Task Assigner'), on_delete=models.SET_NULL, null=True)
    _review_date = models.DateTimeField(verbose_name=_('Review Date'), blank=False, default=set_now)

    class Meta:
        verbose_name = _('Enactment')
        verbose_name_plural = _('Enactments')
        ordering = ['-_review_date', '-_date', 'session', 'subject', 'row']

    def __str__(self):
        return '%s: %s' % (self.session, self.row)

    def __unicode__(self):
        return '%s: %s' % (self.session, self.row)

    def description_short(self):
        return '%s...' % self.description[:50] if self.description else ''

    description_short.short_description = _('Description')

    def result_short(self):
        return '%s...' % self.result[:50] if self.result else ''

    result_short.short_description = _('Result')

    def date(self):
        return to_jalali(self._date) if translation.get_language() == 'fa' else format_date(self._date)

    date.short_description = _('Assignment Date')
    date.admin_order_field = '_date'

    def review_date(self):
        return to_jalali(self._review_date) if translation.get_language() == 'fa' else format_date(self._review_date)

    review_date.short_description = _('Review Date')
    review_date.admin_order_field = '_review_date'

    def first_supervisor(self):
        return self.first_actor.supervisor

    first_supervisor.short_description = _('First Supervisor')

    def second_supervisor(self):
        return self.second_actor.supervisor

    second_supervisor.short_description = _('Second Supervisor')

    def followups(self):
        if self.second_actor:
            return '%s, %s' % (self.first_actor, self.second_actor)
        else:
            return self.first_actor

    followups.short_description = _('Followups')

    def status_colored(self):
        status = 'TODO' if self.result == '' or self.result is None else 'Done'
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
    status_colored.admin_order_field = 'result'


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
