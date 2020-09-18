from django import template
from django.apps import apps
from django.conf import settings
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
def navigation_counter(request, app, model, pk):
    status = '%s_%s' % (app, model) in settings.NAVIGATED_MODELS
    if status:
        queryset_name = '%s_%s_query_set' % (app, model)
        filtered_queryset_name = 'filtered_%s_%s_query_set' % (app, model)

        if pk:
            return {
                'status': status,
                'item': request.session[queryset_name].index({'pk': pk}) + 1,
                'items': len(request.session[queryset_name]),
                'filtered': request.session[filtered_queryset_name]
            }
        else:
            model = apps.get_model(app, model)
            return {
                'status': status,
                'item': '%s %s' % (_(model._meta.verbose_name), _('New'))
            }

    return {'status': False}
