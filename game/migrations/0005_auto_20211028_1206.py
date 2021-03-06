# Generated by Django 3.2.8 on 2021-10-28 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20211027_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='dex',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='player',
            name='luc',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='player',
            name='magic',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='player',
            name='strong',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='player',
            name='current_level_xp',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='player',
            name='next_level_xp',
            field=models.FloatField(default=20),
        ),
    ]
