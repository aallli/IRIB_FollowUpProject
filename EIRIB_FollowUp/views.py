from .utils import update_data

from EIRIB_FollowUp.models import Actor
from django.shortcuts import redirect, render


def update_data_view(request):
    update_data()
    return redirect(request.META['HTTP_REFERER'])


def actor_supervisor_unit(request, pk=None):
    try:
        pk = request.GET.get('pk')
        unit = Actor.objects.get(pk=pk).supervisor.name
    except:
        unit = ''
    return render(request, 'admin/actor-supervisor-unit.html', {'unit': unit})
