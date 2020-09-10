from django import template
from IRIB_FollowUp import utils
from IRIB_FollowUpProject import settings
from django.utils.translation import ugettext_lazy as _

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


@register.simple_tag()
def navigation_counter(request, pk):
    if pk:
        return {'item': request.session['enactment_query_set'].index({'pk': pk}) + 1,
                'items': len(request.session['enactment_query_set']),
                'filtered': request.session['filtered_enactment_query_set']}
    else:
        return {'item': _('New'),
                'items': len(request.session['enactment_query_set']),
                'filtered': request.session['filtered_enactment_query_set']}
