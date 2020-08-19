from IRIB_FollowUp.models import User
from django.shortcuts import render


def actor_supervisor_unit(request, pk=None):
    try:
        pk = request.GET.get('pk')
        unit = User.objects.get(pk=pk).supervisor.name
    except:
        unit = ''
    return render(request, 'admin/actor-supervisor-unit.html', {'unit': unit})
