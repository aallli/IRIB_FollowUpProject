from django import template
from EIRIB_FollowUp import utils


register = template.Library()


@register.simple_tag()
def data_loading():
    return utils.data_loading()

