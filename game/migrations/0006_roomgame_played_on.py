# Generated by Django 3.2.8 on 2021-10-29 11:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20211028_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomgame',
            name='played_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]