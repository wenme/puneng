# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0005_auto_20160704_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='saving',
            name='expected_payback_period',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='saving',
            name='guaranteed_payback_period',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='saving',
            name='longevity',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='saving',
            name='maturity_guaranteed_irr',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='saving',
            name='y10_guaranteed_irr',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='saving',
            name='y20_guaranteed_irr',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='saving',
            name='y30_guaranteed_irr',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='saving',
            name='y50_guaranteed_irr',
            field=models.FloatField(null=True),
        ),
    ]
