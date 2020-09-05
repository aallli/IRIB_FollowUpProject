from django.shortcuts import render


def view_activity_assessment(request, pk=None):
    try:
        pk = request.GET.get('pk')
        # unit = Actor.objects.get(pk=pk).supervisor.name
    except:
        unit = ''
    return render(request, 'admin/custom/activity_assessment_details.html', {'items': unit})
