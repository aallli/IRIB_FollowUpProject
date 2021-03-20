import os, datetime
from .utils import update_data
from django.conf import settings
from django.shortcuts import redirect


def update_data_view(request):
    update_data(request)
    return redirect(request.META['HTTP_REFERER'])


def open_personnel_access_view(request):
    try:
        url = settings.DATABASES['access-personnel']['NAME']
        now = datetime.datetime.now()
        hash = create_hash("%s|%s" % (request.user.username, create_hash("%s%s%s" % (now.minute, request.user.username, now.hour))))
        os.system("%s %s" % (url, hash))
    except:
        pass
    return redirect(request.META['HTTP_REFERER'])


def create_hash(key):
    hash = ""
    for c in key:
        try:
            hash += str(ord(c) ^ int(settings.SSO_SALT))
        except:
            pass

    return hash
