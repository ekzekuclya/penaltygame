# Generated by Django 4.2.9 on 2024-01-18 11:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('penalty_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=2555)),
                ('len_users', models.PositiveIntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='game',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 18, 11, 58, 59, 597151, tzinfo=datetime.timezone.utc)),
        ),
    ]