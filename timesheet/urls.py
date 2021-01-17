from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('full/', views.full, name='full'),
    path('week/', views.week, name='week'),
    path('month/', views.month, name='month'),
    path('create/', views.create, name='create'),
    path('parse/', views.parse, name='parse'),
    path('chart', views.line_chart, name='line_chart'),
    path('chartJSON', views.line_chart_json, name='line_chart_json'),
]