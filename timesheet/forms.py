from django import forms

from timesheet.models import Activity


TIME_CHOICES = (
    (f'{h:02}:{m:02}:00', f'{h:02}:{m:02}')
    for h in range(24) for m in (0, 15, 30, 45)
)


class CreateForm(forms.Form):
    time = forms.ChoiceField(label='Time', choices=tuple(TIME_CHOICES))
    activity = forms.ModelChoiceField(queryset=Activity.objects.all())
