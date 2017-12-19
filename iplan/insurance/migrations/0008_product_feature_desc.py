# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0007_auto_20160911_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='feature_desc',
            field=models.TextField(null=True),
        ),
    ]
