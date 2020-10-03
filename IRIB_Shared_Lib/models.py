from django.db import models
from django.utils.translation import ugettext_lazy as _


class Month(models.TextChoices):
    FARVARDIN = '01', _('Farvardin')
    ORDIBEHESHT = '02', _('Ordibehesht')
    KHORDAD = '03', _('Khordad')
    TIR = '04', _('Tir')
    MORDAD = '05', _('Mordad')
    SHAHRIVAR = '06', _('Shahrivar')
    MEHR = '07', _('Mehr')
    ABAN = '08', _('Aban')
    AZAR = '09', _('Azar')
    DAY = '10', _('Day')
    BAHMAN = '11', _('Bahman')
    ESFAND = '12', _('Esfand')
