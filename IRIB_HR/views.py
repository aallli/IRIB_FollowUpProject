from .utils import update_data
from django.shortcuts import redirect


def update_data_view(request):
    update_data(request)
    return redirect(request.META['HTTP_REFERER'])
