# Generated by Django 4.2.9 on 2024-01-06 12:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penalty_app', '0006_game_waiting_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='waiting_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 6, 12, 45, 56, 303212, tzinfo=datetime.timezone.utc)),
        ),
    ]
