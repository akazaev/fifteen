import datetime

from colorfield.fields import ColorField

from django.apps import AppConfig
from django.db import models


class TimesheetConfig(AppConfig):
    name = 'timesheet'


class Activity(models.Model):
    activity = models.CharField(max_length=30)
    color = ColorField(default='#FFFFFF')

    def __str__(self):
        return self.activity


class Record(models.Model):
    date = models.DateField(default=datetime.datetime.now())
    time = models.TimeField()
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.activity, self.time)