from django import forms
from django.utils import timezone
from .models import ActivityAssessment


def get_activity_assessment_inline_form(request):
    class ActivityAssessmentInlineForm(forms.ModelForm):
        class Meta:
            model = ActivityAssessment
            fields = '__all__'

        def __init__(self, *args, **kwargs):
            super(ActivityAssessmentInlineForm, self).__init__(*args, **kwargs)
            self.request = request
            if self.instance and self.instance.pk and not self.instance.cardtable.closed and \
                    self.instance.member and self.instance.member.user.pk == request.user.pk:
                self.fields['description'].widget.attrs['disabled'] = False
            else:
                self.fields['description'].widget.attrs['disabled'] = 'disabled'

    return ActivityAssessmentInlineForm
