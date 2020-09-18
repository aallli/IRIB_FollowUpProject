from django import template
from Knowledge_Management.models import ActivityStatus

register = template.Library()


@register.simple_tag()
def can_send(item):
    return item and item.pk and item._status == ActivityStatus.DR
