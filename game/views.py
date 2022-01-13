from django.shortcuts import render, redirect
from .models import Player, RoomGame
from django.views import View
from django.db.models import Q
from django.http import HttpResponseRedirect


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            player = Player.objects.get(user=request.user)
            partidas = player.historic()
            xp_bar = (player.current_level_xp * 100) / player.next_level_xp
            return render(request, 'game/home.html', {'current_xp': xp_bar, 'records': partidas})
        else:
            return HttpResponseRedirect('/accounts/login')


class RoomGameView(View):
    def get(self, request, room_pk):
        game_room = RoomGame.objects.get(pk=room_pk)
        return render(request, 'game/room_game.html', {'game_room': game_room})
