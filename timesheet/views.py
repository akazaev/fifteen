from datetime import datetime

import pytz

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render

from timesheet.forms import CreateForm
from timesheet.models import Activity, Record


def index(request):
    current = datetime.now()
    min_hour = max(0, current.hour - 2)
    max_hour = min(24, current.hour + 2)
    activities = Activity.objects.all()
    filter_date = datetime.now().replace(hour=0, minute=0, second=0)
    records = Record.objects.all().filter(date__gte=filter_date)
    records = {str(record.time): record.activity for record in records}
    intervals = []
    for h in range(min_hour, max_hour):
        for m in (0, 15, 30, 45):
            full = f'{h:02}:{m:02}:00'
            short = f'{h:02}:{m:02}'
            activity = records[full].id if full in records else None
            intervals.append((full, short, activity))
    context = {
        'intervals': intervals,
        'activities': activities,
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
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'})

    form = CreateForm()
    return render(request, 'create.html', {'form': form})
