# Generated by Django 3.1.4 on 2020-12-12 08:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0007_auto_20201212_0824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 12, 12, 8, 28, 15, 732290)),
        ),
    ]