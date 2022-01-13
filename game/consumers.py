import json
import random
import time
from datetime import datetime

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from game.models import Player, RoomGame

usuarios = []


# Class to find a game room with a second player
class GameFindRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected in find_room')
        self.room_group_name = 'Fila'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        print('disconnected to find_room')
        self.room_group_name = 'Fila'
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user = await database_sync_to_async(Player.objects.get)(user=self.scope['user'])
        if user not in usuarios:
            usuarios.append(user)

        if 'sair_fila' in text_data_json:
            user = await database_sync_to_async(Player.objects.get)(user=self.scope['user'])
            if user in usuarios:
                usuarios.remove(user)

        if len(usuarios) > 1:
            user1 = usuarios[0]
            user2 = usuarios[1]
            usuarios.remove(user1)
            usuarios.remove(user2)
            print(user1.pk, user2.pk)

            room_game = RoomGame(player1=user1, player2=user2)
            await database_sync_to_async(room_game.save)()
            print(room_game)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cria_sala',
                    'sala': room_game.pk,
                    'users_list': [user1.pk, user2.pk]
                }
            )

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def cria_sala(self, event):
        if 'sala' in event:
            sala = event['sala']
            users_list = event['users_list']
            print(users_list)
            await self.send(text_data=json.dumps({
                'sala_id': sala,
                'users_list': users_list,
            }))


# Class that get all logic from the game match
class GameRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sala_pk = self.scope['url_route']['kwargs']['room_pk']
        self.room_group_name = 'GameRoom_' + self.sala_pk
        self.room_game = await database_sync_to_async(RoomGame.objects.get)(pk=self.sala_pk)
        print('connected to game_room')

        # If it has a winner in the game, show the winner to game room
        if self.room_game.game_situation == 'EG':
            print("Jogo acabado")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_room',
                    'sair': 'True',
                    'winner': await self.get_winner()
                }
            )
        # Otherwise, select a player to start the game
        else:
            selected = await database_sync_to_async(self.room_game.get_turn)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_room',
                    'selected': selected,
                }
            )
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    # Disconnect from game, if player is disconnected lose the game
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive data from frontend websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # If player hp <= 0 end the game
        if 'hp' in text_data_json:
            if text_data_json['hp'][0] <= 0:
                winner = await self.end_game_return_winner(username=text_data_json['hp'][1])
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_room',
                        'atk': '',
                        'selected': '',
                        'sair': 'True',
                        'winner': winner,
                    }
                )

                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
        # Send atack data to room
        elif 'atk' in text_data_json:
            attacker = text_data_json['atk']
            dado = random.randint(10, 40)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_room',
                    'atk': [attacker, dado],
                }
            )
        elif 'saiu' in text_data_json:
            room = await database_sync_to_async(RoomGame.objects.get)(pk=self.sala_pk)
            if room.game_situation == 'IG':
                winner = await self.end_game_return_winner(username=text_data_json['saiu'])
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_room',
                        'sair': 'True',
                        'winner': winner
                    }
                )
        elif 'cont' in text_data_json:
            print(text_data_json['cont'], text_data_json['turn'])
            if text_data_json['cont'] == 0:
                selected = ''
                players = await self.get_name()
                for player in players:
                    if player != text_data_json['turn']:
                        selected = player
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_room',
                        'selected': selected,
                    }
                )

    # Receive data from channel room
    async def game_room(self, event):
        # Return damage and next turn player (selected)
        if 'atk' in event and len(event['atk']) > 0:
            # Get current time
            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")

            # Select user turn
            players = await self.get_name()
            selected = ''
            for player in players:
                if player != event['atk'][0]:
                    selected = player
            dano = event['atk'][1]

            # Change player hp and save turn
            hp = await self.sync_turn_and_hp(username=selected, dano=dano)

            # Save Log
            log = f"[{dt_string}]: {event['atk'][0]} causou {dano} de dano"
            await self.save_log(data=log)

            await self.send(text_data=json.dumps({
                'selected': selected,
                'log': log,
                'hp': hp
            }))

        # Return selected player when start the room game
        elif 'selected' in event and len(event['selected']) > 0:
            selected = event['selected']
            print(f'Turn: {selected}')
            # Change player hp and save turn
            await self.sync_turn_and_hp(username=selected, dano=0)
            await self.send(text_data=json.dumps({
                'selected': selected,
            }))

        # Return winner and loser gamer / end the match
        elif 'sair' in event and len(event['sair']) > 0:
            await self.send(text_data=json.dumps({
                'sair': True,
                'winner': event['winner'],
            }))

    # Function to end game and select the winner
    @database_sync_to_async
    def end_game_return_winner(self, username):
        room = RoomGame.objects.get(pk=self.sala_pk)
        loser_user = User.objects.get(username=username)
        winner = ''
        if room.player1.user != loser_user:
            # save winner in room
            winner = self.room_game.player1.user.username
            room.winner = self.room_game.player1
            room.save()
            # Add xp to winner
            player = Player.objects.get(user=self.room_game.player1.user)
            player.add_xp()
        else:
            # save winner in room
            winner = self.room_game.player2.user.username
            room.winner = self.room_game.player2
            room.save()
            # Add xp to winner
            player = Player.objects.get(user=self.room_game.player2.user)
            player.add_xp()
        room.game_situation = 'EG'
        room.save()
        return winner

    # Function to get players in the room
    @database_sync_to_async
    def get_name(self):
        sala = RoomGame.objects.get(pk=self.sala_pk)
        return [sala.player1.user.username, sala.player2.user.username]

    # Function to return winner from this match
    @database_sync_to_async
    def get_winner(self):
        sala = RoomGame.objects.get(pk=self.sala_pk)
        return sala.winner.user.username

    # Function to save room log and return
    @database_sync_to_async
    def save_log(self, data):
        log = json.loads(self.room_game.game_log)
        log.insert(0, {"msg": data})
        self.room_game.game_log = json.dumps(log)
        self.room_game.save()
        return self.room_game.game_log

    # Function to sync players hp and return player HP
    @database_sync_to_async
    def sync_turn_and_hp(self, username, dano):
        user = User.objects.get(username=username)
        if self.room_game.player1.user == user:
            self.room_game.player1_hp -= dano
            self.room_game.turn = self.room_game.player1
            self.room_game.save()
            return self.room_game.player1_hp
        else:
            self.room_game.player2_hp -= dano
            self.room_game.turn = self.room_game.player2
            self.room_game.save()
            return self.room_game.player2_hp
