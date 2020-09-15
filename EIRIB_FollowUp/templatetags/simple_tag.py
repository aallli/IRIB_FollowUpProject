from django import template
from EIRIB_FollowUp import utils
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
def navigation_counter(request, model, pk):
    status = model in ['enactment', 'personalcardtable']
    if status:
        queryset_name = '%s_query_set' % model
        filtered_queryset_name = 'filtered_%s_query_set' % model

        if pk:
            return {
                'status': status,
                'item': request.session[queryset_name].index({'pk': pk}) + 1,
                'items': len(request.session[queryset_name]),
                'filtered': request.session[filtered_queryset_name]}
        else:
            return {
                'status': status,
                'item': _('New'),
                'items': len(request.session[queryset_name]),
                'filtered': request.session[filtered_queryset_name]}

    return {'status': False}
