# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='city_salary',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name=b'id', primary_key=True)),
                ('city', models.CharField(max_length=50)),
                ('province', models.CharField(max_length=50)),
                ('update_date', models.DateTimeField()),
                ('employee_avg_salary', models.FloatField(null=True)),
                ('retiree_avg_salary', models.FloatField(null=True)),
            ],
        ),
    ]
