from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from IRIB_Shared_Lib.utils import get_admin_url, get_model_fullname


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True

    def first(self, request):
        queryset = self.get_queryset(request)
        obj = queryset.first()
        return HttpResponseRedirect(get_admin_url(self.model, obj.pk if obj else None))

    def previous(self, request):
        pk = int(request.GET['pk'])
        queryset = self.get_queryset(request)
        try:
            pks = list(queryset.values_list('pk', flat=True))
            index = pks.index(pk)
            if index == 0:
                pk = pks[index]
            else:
                pk = pks[index - 1]
        except:
            pk = pks[0] if len(pks) else None

        return HttpResponseRedirect(get_admin_url(self.model, pk))

    def next(self, request):
        pk = int(request.GET['pk'])
        queryset = self.get_queryset(request)
        try:
            pks = list(queryset.values_list('pk', flat=True))
            index = pks.index(pk)
            if index == queryset.count() - 1:
                pk = pks[index]
            else:
                pk = pks[index + 1]
        except:
            pk = pks[len(pks) - 1] if len(pks) else None

        return HttpResponseRedirect(get_admin_url(self.model, pk))

    def last(self, request):
        queryset = self.get_queryset(request)
        obj = queryset.last()
        return HttpResponseRedirect(get_admin_url(self.model, obj.pk if obj else None))

    def get_urls(self):
        urls = super(BaseModelAdmin, self).get_urls()
        from django.urls import path
        return [path('first/', self.first, name="first-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                path('previous/', self.previous,
                     name="previous-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                path('next/', self.next, name="next-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                path('last/', self.last, name="last-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                ] + urls

    def changelist_view(self, request, extra_context=None):
        response = super(BaseModelAdmin, self).changelist_view(request, extra_context)
        model_full_name = get_model_fullname(self)
        if model_full_name in settings.NAVIGATED_MODELS:
            queryset_name = '%s_query_set' % model_full_name
            filtered_queryset_name = 'filtered_%s_query_set' % model_full_name
            request.session[filtered_queryset_name] = False
            if hasattr(response, 'context_data') and 'cl' in response.context_data:
                request.session[queryset_name] = list(response.context_data["cl"].queryset.values('pk'))
                if self.get_preserved_filters(request):
                    request.session[filtered_queryset_name] = True
        return response

    def get_queryset(self, request):
        queryset = super(BaseModelAdmin, self).get_queryset(request)
        model_full_name = get_model_fullname(self)
        if model_full_name in settings.NAVIGATED_MODELS:
            queryset_name = '%s_query_set' % model_full_name
            filtered_queryset_name = 'filtered_%s_query_set' % model_full_name
            if filtered_queryset_name in request.session and request.session[filtered_queryset_name]:
                queryset = queryset.filter(pk__in=[item['pk'] for item in request.session[queryset_name]])
        return queryset
