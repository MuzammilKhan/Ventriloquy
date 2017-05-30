# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wordclips', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wordclip',
            name='speaker',
        ),
        migrations.AddField(
            model_name='wordclip',
            name='speaker',
            field=models.ForeignKey(to='wordclips.Speaker', null=True),
        ),
    ]
