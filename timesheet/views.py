from collections import defaultdict
from datetime import datetime

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render

from timesheet.forms import CreateForm
from timesheet.models import Activity, Record


COLORS_MAP = {
    10: '#5eb91e',
    9: '#5eb91e',
    8: '#bbe33d',
    7: '#bbe33d',
    6: '#d4ea6b',
    5: '#d4ea6b',
    4: '#e8f2a1',
    3: '#e8f2a1',
    2: '#f6f9d4',
    1: '#f6f9d4',
    0: '#ffffff',
    -1: '#ffd7d7',
    -2: '#ffd7d7',
    -3: '#ffa6a6',
    -4: '#ffa6a6',
    -5: '#ff6d6d',
    -6: '#ff6d6d',
    -7: '#ff3838',
    -8: '#ff3838',
    -9: '#f10d0c',
    -10: '#f10d0c',
}


def _get_activity_color(rating):
    if rating in COLORS_MAP:
        return COLORS_MAP[rating]
    elif rating > 10:
        return COLORS_MAP[10]
    elif rating < -10:
        return COLORS_MAP[-10]


def index(request):
    current = datetime.now()
    prev = int(request.GET.get('prev', 2))
    min_hour = max(0, current.hour - prev)
    max_hour = min(24, current.hour + 2)
    activities = {}
    activities_colors = {}
    for activity in Activity.objects.all():
        activities[(activity.id, activity.activity)] = 0
        activities_colors[activity.id] = _get_activity_color(activity.rating)

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
        'activities_choices': activities_choices,
        'activities_colors': activities_colors,
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
    return HttpResponseForbidden()


def full(request):
    intervals = [f'{h:02}:{m:02}' for h in range(24) for m in (0, 15, 30, 45)]
    empty_day = {}
    for interval in intervals:
        empty_day[interval] = None

    records = {}
    for record in Record.objects.order_by('date', 'time'):
        date = str(record.date)
        if date not in records:
            records[date] = empty_day.copy()
        records[date][record.time.strftime('%H:%M')] = record.activity.activity

    context = {
        'intervals': intervals,
        'records': dict(records),
    }
    return render(request, 'full.html', context=context)
