from django import template
from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]


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
def navigation_counter(request, app, model, pk):
    status = '%s_%s' % (app, model) in settings.NAVIGATED_MODELS
    if status:
        queryset_name = '%s_%s_query_set' % (app, model)
        filtered_queryset_name = 'filtered_%s_%s_query_set' % (app, model)
        queryset = request.session[queryset_name]

        if pk:
            try:
                index = queryset.index([pk]) + 1
            except:
                index = '?'

            try:
                items = len(queryset)
            except:
                items = '?'

            try:
                filtered = request.session[filtered_queryset_name]
            except:
                filtered = '?'

            return {
                'status': status,
                'item': index,
                'items': items,
                'filtered': filtered,
            }
        else:
            model = apps.get_model(app, model)
            return {
                'status': status,
                'item': '%s %s' % (_(model._meta.verbose_name), _('New')),
            }

    return {'status': False}
