from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from IRIB_Shared_Lib.utils import get_admin_url, get_model_fullname


class BaseModelAdmin(admin.ModelAdmin):
    save_on_top = True

    def first(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = request.session['%s_query_set' % model_full_name]
        obj = queryset[0][0]
        return HttpResponseRedirect(
            '%s?%s' % (get_admin_url(self.model, obj if obj else None), request.GET.urlencode()))

    def previous(self, request, pk):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = request.session['%s_query_set' % model_full_name]
        try:
            index = queryset.index([pk])
            if index == 0:
                pk = queryset[index][0]
            else:
                pk = queryset[index - 1][0]
        except:
            pk = queryset[0][0] if len(queryset) else None

        return HttpResponseRedirect('%s?%s' % (get_admin_url(self.model, pk), request.GET.urlencode()))

    def next(self, request, pk):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = request.session['%s_query_set' % model_full_name]
        try:
            index = queryset.index([pk])
            if index == len(queryset) - 1:
                pk = queryset[index][0]
            else:
                pk = queryset[index + 1][0]
        except:
            pk = queryset[len(queryset) - 1][0] if queryset else None

        return HttpResponseRedirect('%s?%s' % (get_admin_url(self.model, pk), request.GET.urlencode()))

    def last(self, request):
        super(BaseModelAdmin, self).changelist_view(request)
        model_full_name = get_model_fullname(self)
        queryset = request.session['%s_query_set' % model_full_name]
        obj = queryset[len(queryset) - 1][0]
        return HttpResponseRedirect(
            '%s?%s' % (get_admin_url(self.model, obj if obj else None), request.GET.urlencode()))

    def get_urls(self):
        urls = super(BaseModelAdmin, self).get_urls()
        from django.urls import path
        return [path('first/', self.first, name="first-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                path('<int:pk>/previous/', self.previous,
                     name="previous-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                path('<int:pk>/next/', self.next,
                     name="next-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                path('last/', self.last, name="last-%s-%s" % (self.opts.app_label, self.model._meta.model_name)),
                ] + urls

    def changelist_view(self, request, extra_context=None):
        response = super(BaseModelAdmin, self).changelist_view(request, extra_context)
        model_full_name = get_model_fullname(self)
        if model_full_name in settings.NAVIGATED_MODELS:
            queryset_name = '%s_query_set' % model_full_name
            filtered_queryset_name = 'filtered_%s_query_set' % model_full_name
            request.session[filtered_queryset_name] = self.get_preserved_filters(request) != ''
            if hasattr(response, 'context_data') and 'cl' in response.context_data:
                request.session[queryset_name] = list(response.context_data["cl"].queryset.values_list('pk'))
        return response
