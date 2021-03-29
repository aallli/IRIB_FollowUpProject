import datetime
from .utils import update_data
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect


def update_data_view(request):
    update_data(request)
    return redirect(request.META['HTTP_REFERER'])


def open_personnel_access_view(request):
    try:
        url = settings.DATABASES['access-personnel']['NAME']
        now = datetime.datetime.now()
        hash = create_hash(
            "%s|%s" % (request.user.username, create_hash("%s%s%s" % (now.minute, request.user.username, now.hour))))
    except:
        pass

    resp = HttpResponse("%s %s" % (url, hash), content_type="application/octet-stream")
    resp['Content-Disposition'] = 'attachment; filename=run.bat'
    return resp


def create_hash(key):
    hash = ""
    for c in key:
        try:
            hash += str(ord(c) ^ int(settings.SSO_SALT))
        except:
            pass

    return hash
