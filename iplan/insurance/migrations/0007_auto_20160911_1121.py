# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0006_auto_20160704_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ci',
            name='cancer_total_claim',
            field=models.FloatField(null=True),
        ),
    ]
