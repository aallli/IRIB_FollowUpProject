from django.contrib import admin
from django.http import HttpResponseRedirect

from IRIB_FollowUpProject.utils import get_admin_url


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
