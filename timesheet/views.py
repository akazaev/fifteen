from collections import defaultdict
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from timesheet.forms import CreateForm
from timesheet.models import Activity, Record


def index(request):
    current = datetime.now()
    prev = int(request.GET.get('prev', 2))
    min_hour = max(0, current.hour - prev)
    max_hour = min(24, current.hour + 2)
    activities = {(activity.id, activity.activity): 0
                  for activity in Activity.objects.all()}
    filter_date = datetime.now().replace(hour=0, minute=0, second=0)
    for record in Record.objects.all():
        activities[(record.activity.id, record.activity.activity)] += 1
    activities_choices = [k for k, _ in sorted(
        activities.items(), key=lambda x: x[1], reverse=True)]
    day_records = Record.objects.filter(date__gte=filter_date)
    day_records = {str(record.time): record.activity.id
                   for record in day_records}
    intervals = []
    for h in range(min_hour, max_hour):
        for m in (0, 15, 30, 45):
            full = f'{h:02}:{m:02}:00'
            short = f'{h:02}:{m:02}'
            activity = day_records[full] if full in day_records else None
            intervals.append((full, short, activity))
    context = {
        'intervals': intervals,
        'activities': activities_choices,
        'prev': prev + 2
    }
    return render(request, 'table.html', context=context)


def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            time = form.data['time']
            activity = form.data['activity']
            activity = Activity.objects.get(pk=activity)
            date = datetime.now().date()
            records = Record.objects.all().filter(date=date, time=time)
            if len(records) == 1:
                record = records[0]
                record.activity = activity
            elif len(records) > 1:
                records.delete()
                record = Record(time=time, activity=activity)
            else:
                record = Record(time=time, activity=activity)
            record.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'})

    form = CreateForm()
    return render(request, 'create.html', {'form': form})
