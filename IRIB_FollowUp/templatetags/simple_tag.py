from django import template
from IRIB_FollowUp import utils
from IRIB_FollowUpProject import settings

register = template.Library()


@register.simple_tag()
def version():
    return settings.VERSION


@register.simple_tag()
def admin_tel():
    return settings.ADMIN_TEL


@register.simple_tag()
def admin_email():
    return settings.ADMIN_EMAIL


@register.simple_tag()
def data_loading():
    return utils.data_loading()
