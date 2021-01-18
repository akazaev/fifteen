from collections import defaultdict, namedtuple, OrderedDict
from datetime import datetime, timedelta

from chartjs.views.lines import BaseLineChartView
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls.base import reverse
import holidays

from timesheet.forms import CreateForm
from django.db.models import Count
from timesheet.models import Activity, Record


INTERVAL = 15
HOUR = 60


def _get_time_display(time):
    hours = time // HOUR
    minutes = time % HOUR
    result = []
    if hours:
        result.append(f'{hours} h')
    if minutes:
        result.append(f'{minutes} m')
    return ' '.join(result)


def index(request):
    current = datetime.now()
    prev = int(request.GET.get('prev', 2))
    filter_date = request.GET.get('date')

    min_hour = 0
    max_hour = 24
    if not filter_date:
        min_hour = max(0, current.hour - prev)
        max_hour = min(24, current.hour + 3)

    activities = {activity.id: activity for activity in Activity.objects.all()}

    if not filter_date:
        cur_date = datetime.now()
        filter_date = cur_date.strftime('%Y-%m-%d')
    else:
        cur_date = datetime.strptime(filter_date, '%Y-%m-%d')

    activity_stat = Record.objects.all().values('activity').annotate(
        count=Count('activity_id')).order_by('-count')

    activities_choices = [(activity['activity'],
                           activities[activity['activity']])
                          for activity in activity_stat]
    records = Record.objects.filter(date=filter_date)
    day_stats = defaultdict(int)
    day_records = {}
    for record in records:
        stime = str(record.time)
        day_records[stime] = record.activity.id
        day_stats[record.activity.activity] += 1

    day_stats = [(activity, count, _get_time_display(count * INTERVAL))
                 for activity, count in day_stats.items()]
    day_stats.sort(key=lambda x: x[1], reverse=True)

    intervals = []
    for h in range(min_hour, max_hour):
        for m in (0, INTERVAL, INTERVAL * 2, INTERVAL * 3):
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
                               if activity.rating is not None},
        'prev': prev + 2,
        'cur_date': cur_date.strftime('%Y-%m-%d'),
        'prev_date': (cur_date - timedelta(1)).strftime('%Y-%m-%d'),
        'day_stats': day_stats
    }
    return render(request, 'tracker.html', context=context)


def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        date = form.data['date']
        time = form.data['time']
        activity = form.data['activity']
        if not activity and date and time:
            records = Record.objects.all().filter(date=date, time=time)
            records.delete()
            return JsonResponse({'status': 'ok'})

        if form.is_valid():
            activity = Activity.objects.get(pk=activity)
            if not date:
                date = datetime.now().date()
            records = Record.objects.all().filter(date=date, time=time)
            if len(records) == 1:
                record = records[0]
                record.activity = activity
            elif len(records) > 1:
                records.delete()
                record = Record(time=time, activity=activity, date=date)
            else:
                record = Record(time=time, activity=activity, date=date)
            record.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error'})
    return HttpResponseForbidden()


Cell = namedtuple('Cell', ['color', 'rating', 'activity'])


def _report(days=None):
    intervals = [f'{h:02}:{m:02}' for h in range(7, 24)
                 for m in (0, INTERVAL, INTERVAL * 2, INTERVAL * 3)]
    empty_day = {}
    for interval in intervals:
        empty_day[interval] = None

    activities = {}
    for activity in Activity.objects.all():
        activities[activity.id] = activity

    if days:
        filter_date = datetime.now().replace(hour=0, minute=0, second=0)
        filter_date -= timedelta(days=days - 1)
        records = Record.objects.filter(
            date__gte=filter_date).order_by('-date', 'time').values(
            'date', 'time', 'activity_id')
    else:
        records = Record.objects.order_by('-date', 'time').values(
            'date', 'time', 'activity_id')

    ru_holidays = holidays.RU()
    ru_holidays.append({"2020-12-31": ""})

    report = {}
    for record in records:
        date = record['date']
        time = record['time'].strftime('%H:%M')
        dayoff = date in ru_holidays or date.weekday() in (5, 6, )

        if date not in report:
            report[date] = empty_day.copy(), dayoff

        activity_id = record['activity_id']
        report[date][0][time] = Cell(color=activities[activity_id].color,
                                     rating=activities[activity_id].rating,
                                     activity=activities[activity_id].activity)
    return intervals, report


def full(request):
    intervals, records = _report()
    context = {
        'intervals': intervals,
        'records': records,
    }
    return render(request, 'timesheet.html', context=context)


def week(request):
    intervals, records = _report(7)
    context = {
        'intervals': intervals,
        'records': records,
    }
    return render(request, 'timesheet.html', context=context)


def month(request):
    intervals, records = _report(30)
    context = {
        'intervals': intervals,
        'records': records,
    }
    return render(request, 'timesheet.html', context=context)


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
        if len(date) != 3:
            continue
        date = f"{date[2]}-{date[1]}-{date[0]}"
        for line in data[1:]:
            day.append(line[i].strip())

        for time, activity in zip(intervals, day):
            if activity:
                record = Record(date=date, time=time,
                                activity=activities[activity])
                record.save()
    return HttpResponse()


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        records = Record.objects.order_by('date', 'time').values(
            'date', 'activity_id')
        ru_holidays = holidays.RU()
        ru_holidays.append({"2020-12-31": ""})

        data = []
        for record in records:
            date = record['date']
            if date in ru_holidays or date.weekday() in (5, 6,):
                continue
            if record['activity_id'] in (1, 2, ):
                if date not in data:
                    data.append(date)
        return data

    def get_providers(self):
        return ["work", "avg work", "inet", "avg inet"]

    def get_data(self):
        records = Record.objects.order_by('date', 'time').values(
            'date', 'activity_id')
        ru_holidays = holidays.RU()
        ru_holidays.append({"2020-12-31": ""})

        data1 = OrderedDict()
        data2 = OrderedDict()
        sum1 = sum2 = 0
        avg_list1 = []
        avg_list2 = []
        c1 = c2 = 0
        for record in records:
            date = record['date']
            if date in ru_holidays or date.weekday() in (5, 6,):
                continue
            if date not in data1:
                data1[date] = 0
            if date not in data2:
                data2[date] = 0
            if record['activity_id'] == 2:
                data1[date] += 1
            if record['activity_id'] == 1:
                data2[date] += 1
        for day, value in data1.items():
            sum1 += value
            c1 += 1
            avg_list1.append(sum1 / c1)
        for day, value in data2.items():
            sum2 += value
            c2 += 1
            avg_list2.append(sum2 / c2)
        return [list(data1.values()), avg_list1,
                list(data2.values()), avg_list2]


def avg_chart(request):
    context = {
        'json_url': reverse('avg_chart_json'),
    }
    return render(request, 'line_chart.html', context=context)


def avg_chart_json(request):
    default_opts = {
        "hidden": True,
        "backgroundColor": "rgba(171, 9, 0, 0.5)",
        "borderColor": "rgba(171, 9, 0, 1)",
        "pointBackgroundColor": "rgba(171, 9, 0, 1)",
        "pointBorderColor": "#fff",
    }

    ru_holidays = holidays.RU()
    ru_holidays.append({"2020-12-31": ""})
    collect = (2, 12, 15, 4, 3, 1, )
    activities = {}
    for activity in Activity.objects.all():
        if activity.id in collect:
            activities[activity.id] = activity.activity

    records = Record.objects.order_by('date', 'time').values(
        'date', 'activity_id')

    datasets = []
    for activity_id, activity_name in activities.items():
        data = OrderedDict()
        sum = c = 0
        avg = []
        for record in records:
            date = record['date']
            if date in ru_holidays or date.weekday() in (5, 6,):
                continue
            if date not in data:
                data[date] = 0
            if record['activity_id'] == activity_id:
                data[date] += INTERVAL / HOUR

        for day, value in data.items():
            sum += value
            c += 1
            avg.append(sum / c)
        datasets.append({'data': avg, 'label': activity_name,
                         'name': activity_name, **default_opts})

    labels = list(range(len(datasets[0]['data'])))
    return JsonResponse(data={'datasets': datasets, 'labels': labels})


def weekday_chart(request):
    context = {
        'json_url': reverse('weekday_chart_json'),
    }
    return render(request, 'bar_chart.html', context=context)


def weekday_chart_json(request):
    default_opts = {
        "hidden": True,
        "backgroundColor": "rgba(171, 9, 0, 0.5)",
        "borderColor": "rgba(171, 9, 0, 1)",
        "pointBackgroundColor": "rgba(171, 9, 0, 1)",
        "pointBorderColor": "#fff",
    }

    ru_holidays = holidays.RU()
    ru_holidays.append({"2020-12-31": ""})
    collect = (2, 12, 15, 4, 3, 1,)
    activities = {}
    for activity in Activity.objects.all():
        if activity.id in collect:
            activities[activity.id] = activity.activity

    records = Record.objects.order_by('date', 'time').values(
        'date', 'activity_id')

    datasets = []
    for activity_id, activity_name in activities.items():
        data = defaultdict(int)
        data_all = defaultdict(int)
        for record in records:
            date = record['date']
            if record['activity_id'] == activity_id:
                data[date] += INTERVAL / HOUR
            data_all[date] += 1

        values = [0] * 7
        counts = [0] * 7
        for date, value in data.items():
            if data_all[date] >= 50:
                values[date.weekday()] += value
                counts[date.weekday()] += 1
        dataset = [v/c if c else 0 for v, c in zip(values, counts)]
        datasets.append({'data': dataset, 'label': activity_name,
                         'name': activity_name, **default_opts})

    labels = list(range(len(datasets[0]['data'])))
    return JsonResponse(data={'datasets': datasets, 'labels': labels})


def week_chart(request):
    context = {
        'json_url': reverse('week_chart_json'),
    }
    return render(request, 'bar_chart.html', context=context)


def week_chart_json(request):
    collect = 2

    records = Record.objects.order_by('date', 'time').values(
        'date', 'activity_id')

    weeks = []
    week = None
    prev_monday = None
    week_interval = None
    for record in records:
        if record['activity_id'] != collect:
            continue
        date = record['date']
        weekday = date.weekday()

        if not weekday and (not prev_monday or prev_monday != date):
            if prev_monday:
                weeks.append(week)
            prev_monday = date
            week = [0] * 7
            week_interval = date, date + timedelta(days=6)

        if not week_interval:
            continue

        if week_interval[0] <= date <= week_interval[1]:
            week[weekday] += 1

    if week:
        weeks.append(week)

    dataset = [sum(week) * INTERVAL / HOUR for week in weeks if all(week[0:5])]

    labels = list(range(len(dataset)))
    return JsonResponse(data={'datasets': [{'data': dataset}],
                              'labels': labels})
