# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0004_remove_saving_expected_payback_period'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saving',
            name='guaranteed_payback_period',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='longevity',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='maturity_guaranteed_irr',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='y10_guaranteed_irr',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='y20_guaranteed_irr',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='y30_guaranteed_irr',
        ),
        migrations.RemoveField(
            model_name='saving',
            name='y50_guaranteed_irr',
        ),
    ]
