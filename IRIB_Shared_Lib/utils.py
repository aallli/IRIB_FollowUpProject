import datetime
from django.conf import settings
from django.utils import timezone
from jalali_date import datetime2jalali
from django.contrib.admin import SimpleListFilter

from django.utils.translation import ugettext_lazy as _

msgid = _('Done')
msgid = _('TODO')

def get_admin_url(model, pk=None):
    from django.urls import reverse
    info = (model._meta.app_label, model._meta.model_name)
    return reverse('admin:%s_%s_change' % info, args=(pk,)) if pk else reverse('admin:%s_%s_changelist' % info, )


def get_model_fullname(self):
    return '%s_%s' % (self.opts.app_label, self.model._meta.model_name)


def format_date(date, second=False):
    if second:
        return date.strftime('%Y/%m/%d %H:%M:%S')
    else:
        return date.strftime('%Y/%m/%d %H:%M')


def to_jalali(date, no_time=False, second=False):
    if date:
        if no_time:
            return datetime2jalali(date).strftime('%Y/%m/%d')
        elif second:
            return datetime2jalali(date).strftime('%H:%M:%S %Y/%m/%d')
        else:
            return datetime2jalali(date).strftime('%H:%M %Y/%m/%d')
    return ''


def switch_lang_code(path, language):
    # Get the supported language codes
    lang_codes = [c for (c, name) in settings.LANGUAGES]

    # Validate the inputs
    if path == '':
        raise Exception('URL path for language switch is empty')
    elif path[0] != '/':
        raise Exception('URL path for language switch does not start with "/"')
    elif language not in lang_codes:
        raise Exception('%s is not a supported language code' % language)

    # Split the parts of the path
    parts = path.split('/')

    # Add or substitute the new language prefix
    if parts[1] in lang_codes:
        parts[1] = language
    else:
        parts[0] = "/" + language

    # Return the full new path
    return '/'.join(parts)


def set_now():
    return timezone.now()


def get_jalali_filter(field, filter_title):
    class JalaliDateFilter(SimpleListFilter):
        title = filter_title
        parameter_name = field

        def lookups(self, request, model_admin):
            return [('today', _('Today')), ('this_week', _('This week')), ('10days', _('Last 10 days')),
                    ('this_month', _('This month')), ('30days', _('Last 30 days')), ('90days', _('Last 3 months')),
                    ('180days', _('Last 6 months'))]

        def queryset(self, request, queryset):
            startdate = timezone.now()
            enddate = None
            if self.value() == 'today':
                enddate = startdate - datetime.timedelta(hours=startdate.hour) - datetime.timedelta(
                    minutes=startdate.minute) - datetime.timedelta(seconds=startdate.second)

            if self.value() == 'this_week':
                enddate = startdate - datetime.timedelta(days=(startdate.weekday() + 2) % 7)

            if self.value() == '10days':
                enddate = startdate - datetime.timedelta(days=9)

            if self.value() == 'this_month':
                enddate = startdate - datetime.timedelta(days=datetime2jalali(startdate).day - 1)

            if self.value() == '30days':
                enddate = startdate - datetime.timedelta(days=29)

            if self.value() == '90days':
                enddate = startdate - datetime.timedelta(days=89)

            if self.value() == '180days':
                enddate = startdate - datetime.timedelta(days=179)

            kwargs = {'{0}__range'.format(self.parameter_name): [enddate, startdate], }

            return queryset.filter(**kwargs) if enddate else queryset

    return JalaliDateFilter
