# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wordclips', '0002_auto_20170526_2138'),
    ]

    operations = [
        migrations.RenameField(
            model_name='speaker',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='speaker',
            old_name='last_name',
            new_name='lastname',
        ),
    ]
