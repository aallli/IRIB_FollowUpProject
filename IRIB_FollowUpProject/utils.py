from django.contrib import admin
from jalali_date import datetime2jalali
from IRIB_FollowUpProject import settings
from django.http import HttpResponseRedirect


def get_admin_url(self):
    """the url to the Django admin interface for the model instance"""
    from django.urls import reverse

    info = (self._meta.app_label, self._meta.model_name)
    return reverse('admin:%s_%s_change' % info, args=(self.pk,))


def to_jalali(date, no_time=False):
    if date:
        if no_time:
            return datetime2jalali(date).strftime('%Y/%m/%d')
        else:
            return datetime2jalali(date).strftime('%H:%M:%S %Y/%m/%d')
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


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True

    def first(self, request):
        queryset = self.get_queryset(request)
        return HttpResponseRedirect(get_admin_url(queryset.first()))

    def previous(self, request):
        pk = int(request.GET['pk'])
        queryset = self.get_queryset(request)
        index = list(queryset.values_list('pk', flat=True)).index(pk)
        if index == 0:
            obj = queryset[index]
        else:
            obj = queryset[index - 1]
        return HttpResponseRedirect(get_admin_url(obj))

    def next(self, request):
        pk = int(request.GET['pk'])
        queryset = self.get_queryset(request)
        index = list(queryset.values_list('pk', flat=True)).index(pk)
        if index == queryset.count() - 1:
            obj = queryset[index]
        else:
            obj = queryset[index + 1]
        return HttpResponseRedirect(get_admin_url(obj))

    def last(self, request):
        queryset = self.get_queryset(request)
        return HttpResponseRedirect(get_admin_url(queryset.last()))

    def get_urls(self):
        urls = super(BaseModelAdmin, self).get_urls()
        from django.urls import path
        return [path('first/', self.first, name="first-%s" % self.model._meta.model_name),
                path('previous/', self.previous, name="previous-%s" % self.model._meta.model_name),
                path('next/', self.next, name="next-%s" % self.model._meta.model_name),
                path('last/', self.last, name="last-%s" % self.model._meta.model_name),
                ] + urls
