from django import forms
from django.utils import timezone
from .models import Enactment, FollowUp


class EnactmentAdminForm(forms.ModelForm):
    class Meta:
        model = Enactment
        exclude = []

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            if Enactment.objects.count():
                last_obj = Enactment.objects.latest('pk')
                kwargs['initial'].update({
                    'session': last_obj.session,
                    'subject': last_obj.subject,
                    'assigner': last_obj.assigner,
                    '_review_date': last_obj.review_date
                })
        super(EnactmentAdminForm, self).__init__(*args, **kwargs)


def get_followup_inline_form(request):
    class FollowUpInlineForm(forms.ModelForm):
        class Meta:
            model = FollowUp
            fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(FollowUpInlineForm, self).__init__(*args, **kwargs)
            self.request = request
            if self.instance and self.instance.actor and self.instance.actor.pk == request.user.pk:
                self.fields['result'].widget.attrs['disabled'] = False
            else:
                self.fields['result'].widget.attrs['disabled'] = 'disabled'

        def save(self, commit=True):
            if 'result' in self.changed_data:
                self.instance._date = timezone.now()
            return super(FollowUpInlineForm, self).save(commit)

    return FollowUpInlineForm
