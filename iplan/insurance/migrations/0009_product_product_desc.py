# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0008_product_feature_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_desc',
            field=models.TextField(null=True),
        ),
    ]
