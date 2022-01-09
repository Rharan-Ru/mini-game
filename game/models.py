from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import random


class Player(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='player', on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='img_profile/', default="img_profile/corazon.jpg", blank=True)
    level = models.IntegerField(default=1)
    current_level_xp = models.FloatField(default=1)
    next_level_xp = models.FloatField(default=20)

    magic = models.IntegerField(default=1)
    strong = models.IntegerField(default=1)
    dex = models.IntegerField(default=1)
    luc = models.IntegerField(default=1)

    def historic(self):
        partidas = []
        partidas_player1 = RoomGame.objects.filter(player1=self)
        partidas_player2 = RoomGame.objects.filter(player2=self)
        [partidas.append(x) for x in partidas_player1]
        [partidas.append(x) for x in partidas_player2]
        return partidas

    def add_xp(self):
        xp = random.randint(50, 150)
        self.current_level_xp += xp
        self.save()

    def save(self, *args, **kwargs):
        while self.current_level_xp > self.next_level_xp:
            self.level += 1
            self.next_level_xp += self.next_level_xp * (self.level * 0.12)

            if self.level < 20:
                self.magic += 3
                self.strong += 3
                self.dex += 3
                self.luc += 3
            else:
                self.magic += 1
                self.strong += 1
                self.dex += 1
                self.luc += 1
        super(Player, self).save(*args, **kwargs)

    # def method to create a user profile when some new user is created
    @receiver(post_save, sender=User)  # add this
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Player.objects.create(user=instance)

    @receiver(post_save, sender=User)  # add this
    def save_user_profile(sender, instance, **kwargs):
        instance.player.save()


class RoomGame(models.Model):
    IN_GAME = 'IG'
    END_GAME = 'EG'
    GAME_SITUATION = [
        (IN_GAME, 'In Game'),
        (END_GAME, 'End Game')
    ]

    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player2')

    game_situation = models.CharField(max_length=2, choices=GAME_SITUATION, default=IN_GAME)
    turn = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='turn', null=True)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)

    played_on = models.DateTimeField(default=timezone.now)

    def first_turn(self):
        player = random.choice([self.player1, self.player2])
        self.turn = player
        self.save()
        return player.user.username

    def get_turn(self):
        if self.turn:
            return self.turn.user.username
        else:
            return False
