from django import template
from IRIB_HR import utils

register = template.Library()


@register.simple_tag()
def hr_data_loading(app_label):
    return app_label in ['IRIB_hr', 'index'] and utils.data_loading()
