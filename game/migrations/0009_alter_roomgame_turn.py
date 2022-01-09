# Generated by Django 3.2.8 on 2022-01-08 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_roomgame_game_situation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roomgame',
            name='turn',
            field=models.ForeignKey(default=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player1', to='game.player'), null=True, on_delete=django.db.models.deletion.CASCADE, related_name='turn', to='game.player'),
        ),
    ]