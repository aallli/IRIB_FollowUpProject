"""IRIB_FollowUpProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from IRIB_FollowUp import views
from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from EIRIB_FollowUp.views import update_data_view
from django.utils.translation import ugettext_lazy as _


admin.site.site_header = settings.SITE_HEADER
admin.site.site_title = _('Welcome to EIRIB administration system')

urlpatterns = [
    path('', lambda request: redirect('/fa/admin/', permanent=False)),
    path('ajax/actor_supervisor_unit/', views.actor_supervisor_unit, name='ajax_actor_supervisor_unit'),
]

urlpatterns += i18n_patterns(
    path('admin/start_sync/', update_data_view),
    path('admin/', admin.site.urls),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
