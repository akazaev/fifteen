from collections import defaultdict, namedtuple
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render

from timesheet.forms import CreateForm
from django.db.models import Count
from timesheet.models import Activity, Record


def index(request):
    current = datetime.now()
    prev = int(request.GET.get('prev', 2))
    min_hour = max(0, current.hour - prev)
    max_hour = min(24, current.hour + 2)
    activities = {activity.id: activity for activity in Activity.objects.all()}

    filter_date = datetime.now().replace(hour=0, minute=0, second=0)
    activity_stat = Record.objects.all().values('activity').annotate(
        count=Count('activity_id')).order_by('-count')

    activities_choices = [(activity['activity'],
                           activities[activity['activity']])
                          for activity in activity_stat]
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
        'activities_colors': {activity_id: activity.color
                              for activity_id, activity in activities.items()
                              if activity.color},
        'activities_ratings': {activity_id: activity.rating
                               for activity_id, activity in activities.items()
                               if activity.rating},
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


Cell = namedtuple('Cell', ['time', 'color', 'rating', 'activity'])


def _report(days=None):
    intervals = [f'{h:02}:{m:02}' for h in range(7, 24)
                 for m in (0, 15, 30, 45)]
    empty_day = {}
    for interval in intervals:
        empty_day[interval] = None

    activities = {}
    for activity in Activity.objects.all():
        activities[activity.id] = activity

    if days:
        filter_date = datetime.now().replace(hour=0, minute=0, second=0)
        filter_date -= timedelta(days=days + 1)
        records = Record.objects.filter(
            date__gte=filter_date).order_by('date', 'time').values(
            'date', 'time', 'activity_id')
    else:
        records = Record.objects.order_by('date', 'time').values(
            'date', 'time', 'activity_id')

    report = defaultdict(list)
    for record in records:
        date = record['date']
        time = record['time'].strftime('%H:%M')
        if not report[date]:
            report[date].extend([''] * intervals.index(time))
        activity_id = record['activity_id']
        cell = Cell(time=time, color=activities[activity_id].color,
                    rating=activities[activity_id].rating,
                    activity=activities[activity_id].activity)
        report[date].append(cell)
    for day in report:
        day_records = report[day]
        tail = len(intervals) - intervals.index(day_records[-1].time) - 1
        if tail:
            day_records.extend([''] * tail)
    return intervals, report


def full(request):
    intervals, records = _report()
    context = {
        'intervals': intervals,
        'records': dict(records),
    }
    return render(request, 'full.html', context=context)


def week(request):
    intervals, records = _report(7)
    context = {
        'intervals': intervals,
        'records': dict(records),
    }
    return render(request, 'full.html', context=context)


def month(request):
    intervals, records = _report(30)
    context = {
        'intervals': intervals,
        'records': dict(records),
    }
    return render(request, 'full.html', context=context)


def parse(request):
    activities = {}
    for activity in Activity.objects.all():
        activities[activity.activity] = activity

    data = []
    with open('timesheet/full.csv') as f:
        while line := f.readline():
            data.append(line.split(';'))

    for l in data:
        assert len(data[0]) == len(l)

    intervals = []
    for line in data:
        interval = line[0].strip()
        if interval:
            intervals.append(interval)

    for i in range(1, len(data[0])):
        day = []
        date = data[0][i].strip().split('.')
        date = f"{date[2]}-{date[1]}-{date[0]}"
        for line in data[1:]:
            day.append(line[i].strip())

        for time, activity in zip(intervals, day):
            if activity:
                record = Record(date=date, time=time,
                                activity=activities[activity])
                record.save()
    return HttpResponse()
