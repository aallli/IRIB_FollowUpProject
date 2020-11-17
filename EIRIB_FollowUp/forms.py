from django import forms
from .models import Enactment


class EnactmentAdminForm(forms.ModelForm):
    class Meta:
        model = Enactment
        exclude = []

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            last_obj = Enactment.objects.order_by('row').latest('row')
            kwargs['initial'].update({
                'session': last_obj.session,
                'subject': last_obj.subject,
                'assigner': last_obj.assigner,
                '_date': last_obj._date,
                '_review_date': last_obj._review_date
            })
        super(EnactmentAdminForm, self).__init__(*args, **kwargs)
