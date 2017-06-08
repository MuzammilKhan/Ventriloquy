# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videoadmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='celerytask',
            name='celery_task_status',
            field=models.CharField(max_length=20, default=None),
        ),
    ]
