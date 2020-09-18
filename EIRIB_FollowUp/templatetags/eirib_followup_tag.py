from django import template
from EIRIB_FollowUp import utils

register = template.Library()


@register.simple_tag()
def data_loading(app_label):
    return app_label in ['EIRIB_FollowUp', 'index'] and utils.data_loading()
