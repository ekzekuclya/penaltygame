# Generated by Django 4.2.9 on 2024-01-09 23:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penalty_app', '0005_alter_game_created_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 9, 23, 5, 37, 922590, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(blank=True, to='penalty_app.telegramuser'),
        ),
    ]
