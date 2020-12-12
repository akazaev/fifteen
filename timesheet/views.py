from datetime import datetime

import pytz

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from timesheet.forms import CreateForm
from timesheet.models import Activity, Record


def index(request):
    current = datetime.now()
    min_hour = max(0, current.hour - 2)
    max_hour = min(24, current.hour + 2)
    activities = Activity.objects.all()
    context = {
        'intervals': [f'{h:02}:{m:02}' for h in range(min_hour, max_hour)
                      for m in (0, 15, 30, 45)],
        'activities': activities
    }
    return render(request, 'table.html', context=context)


def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            time = form.data['time']
            activity = form.data['activity']
            activity = Activity.objects.get(pk=activity)
            record = Record(time=time, activity=activity)
            record.save()
            return HttpResponseRedirect('/')
    else:
        form = CreateForm()

    return render(request, 'create.html', {'form': form})
