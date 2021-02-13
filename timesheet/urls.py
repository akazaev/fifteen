from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('full/', views.full, name='full'),
    path('week/', views.week, name='week'),
    path('month/', views.month, name='month'),
    path('create/', views.create, name='create'),
    path('parse/', views.parse, name='parse'),
    path('charts/avg/', views.avg_chart, name='avg_chart'),
    path('charts/avg.json', views.avg_chart_json, name='avg_chart_json'),
    path('charts/weekday/', views.weekday_chart, name='weekday_chart'),
    path('charts/weekday.json', views.weekday_chart_json,
         name='weekday_chart_json'),
    path('charts/week/', views.week_chart, name='week_chart'),
    path('charts/week.json', views.week_chart_json, name='week_chart_json'),
    path('charts/hour/', views.hour_chart, name='hour_chart'),
    path('charts/hour.json', views.hour_chart_json, name='hour_chart_json'),
    path('charts/level/', views.level_chart, name='level_chart'),
    path('charts/level.json', views.level_chart_json, name='level_chart_json'),
    path('charts/day_level/', views.day_level_chart, name='day_level_chart'),
    path('charts/day_level.json', views.day_level_chart_json,
         name='day_level_chart_json'),
]