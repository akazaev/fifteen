# Generated by Django 3.1.4 on 2021-01-14 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0015_auto_20210111_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='date',
            field=models.DateField(),
        ),
    ]
