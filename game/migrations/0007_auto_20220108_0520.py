# Generated by Django 3.2.8 on 2022-01-08 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_roomgame_played_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomgame',
            name='loser',
        ),
        migrations.AddField(
            model_name='roomgame',
            name='turn',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='turn', to='game.player'),
        ),
    ]
