import locale, os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.utils import translation
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from IRIB_FollowUpProject.utils import to_jalali, format_date


class AccessLevel(models.TextChoices):
    USER = 'user', _('User')
    SECRETARY = 'secretary', _('Secretary')


class Title(models.TextChoices):
    MR = 'Mr', _('Mr')
    MRS = 'Mrs', _('Mrs')


class Supervisor(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=2000, blank=False, unique=True)

    class Meta:
        verbose_name = _('Supervisor Unit')
        verbose_name_plural = _('Supervisor Units')
        ordering = ['name']

    def __str__(self):
        return _(self.name).__str__()

    def __unicode__(self):
        return self.__str__()
#
#
# class User(AbstractUser):
#     user_id = models.IntegerField(verbose_name=_('User ID'), blank=True, null=True)
#     access_level = models.CharField(verbose_name=_('Access Level'), choices=AccessLevel.choices,
#                                     default=AccessLevel.USER, max_length=20, null=False)
#     _title = models.CharField(verbose_name=_('Title'), choices=Title.choices,
#                               default=Title.MR, max_length=100, null=False)
#     supervisor = models.ForeignKey('Supervisor', verbose_name=_('Supervisor Unit'), on_delete=models.SET_NULL,
#                                    null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'IRIB_Auth_user'
#
#     def last_login_jalali(self):
#         return to_jalali(self.last_login) if translation.get_language() == 'fa' else format_date(self.last_login)
#
#     last_login_jalali.short_description = _('last login')
#     last_login_jalali.admin_order_field = 'last_login'
#
#     def date_joined_jalali(self):
#         return to_jalali(self.date_joined) if translation.get_language() == 'fa' else format_date(self.date_joined)
#
#     date_joined_jalali.short_description = _('date joined')
#     date_joined_jalali.admin_order_field = 'date_joined'
#
#     def __str__(self):
#         return '%s %s' % (
#             self.last_name, self.first_name) if self.last_name or self.first_name else  self.get_username()
#
#     def __unicode__(self):
#         return self.__str__()
#
#     def title(self):
#         return Title(self._title).label
#
#     @property
#     def is_secretary(self):
#         return self.access_level == AccessLevel.SECRETARY
#
#     @property
#     def is_km_operator(self):
#         return self.groups.filter(name=settings.OPERATOR_GROUP_NAME) > 0
#
#     def delete(self, using=None, keep_parents=False):
#         if self.is_superuser:
#             raise Exception(_('Delete failed, Immutable user: (%s)' % self.username))
#         return super(User, self).delete(using, keep_parents)
