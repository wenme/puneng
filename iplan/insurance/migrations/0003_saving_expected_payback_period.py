# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0002_remove_saving_expected_payback_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='saving',
            name='expected_payback_period',
            field=models.IntegerField(null=True),
        ),
    ]
