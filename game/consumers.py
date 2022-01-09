import json
import random
import time

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
        self.situation = self.room_game.game_situation
        print('connected to game_room')

        # If it has a winner in the game, show the winner to game room
        if self.situation == 'EG':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_room',
                    'sair': 'True',
                    'winner': await self.get_winner()
                }
            )

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        # Otherwise, select a player to start the game
        else:
            selected = await database_sync_to_async(self.room_game.get_turn)()
            if selected is False:
                print("Selecionando User")
                selected = await database_sync_to_async(self.room_game.first_turn)()
            print(selected)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_room',
                    'selected': selected,
                }
            )
        await self.accept()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

    # Disconnect from game, if player is disconnected lose the game
    async def disconnect(self, close_code):
        # winner = ''
        # loser = self.scope['user']
        # if self.room_game.player1 != loser:
        #     winner = self.room_game.player1.user.username
        # elif self.room_game.player2 != loser:
        #     winner = self.room_game.player2.user.username
        #
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'game_room',
        #         'atk': '',
        #         'selected': '',
        #         'sair': 'True',
        #         'winner': winner,
        #     }
        # )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive data from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # If player hp <= 0 end the game
        if 'hp' in text_data_json:
            if text_data_json['hp'][0] <= 0:
                winner = ''
                loser = text_data_json['hp'][1]
                if self.room_game.player1.username != loser:
                    winner = self.room_game.player1.username
                elif self.room_game.player2.username != loser:
                    winner = self.room_game.player2.username
                await self.get_winner(player=winner)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_room',
                        'atk': '',
                        'selected': '',
                        'sair': 'True',
                        'derrota': loser,
                        'winner': winner,
                    }
                )

                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

        # Send atack data to room
        if 'atk' in text_data_json:
            attacker = text_data_json['atk']
            dado = random.randint(10, 40)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_room',
                    'atk': [attacker, dado],
                }
            )

    # Receive data from room
    async def game_room(self, event):
        print(event)
        # Return damage and next turn player (selected)
        if 'atk' in event and len(event['atk']) > 0:
            players = await self.get_name()
            selected = ''
            for player in players:
                if player != event['atk'][0]:
                    selected = player
            dano = event['atk'][1]
            await self.send(text_data=json.dumps({
                'selected': selected,
                'log': f'{event["atk"][0]} causou {dano} de dano',
                'dano': dano,
            }))

        # Return selected player when start the room game
        elif 'selected' in event and len(event['selected']) > 0:
            selected = event['selected']
            print(f'Turn: {selected}')
            await self.send(text_data=json.dumps({
                'selected': selected,
            }))

        # Return winner and loser gamer and end the match
        elif 'sair' in event and len(event['sair']) > 0:
            await self.send(text_data=json.dumps({
                'sair': True,
                'derrota': event['derrota'],
                'winner': event['winner'],
            }))

    # Functions to get data from database
    # Get players in the room
    @database_sync_to_async
    def get_name(self):
        sala = RoomGame.objects.get(pk=self.sala_pk)
        return [sala.player1.user.username, sala.player2.user.username]

    # Return/Save winner
    @database_sync_to_async
    def get_winner(self, player=False):
        sala = RoomGame.objects.get(pk=self.sala_pk)
        if player:
            user = User.objects.get(username=player)
            player_winner = Player.objects.get(user=user)

            sala.winner = player_winner

            sala.save()
            return player_winner.user.username

        if sala.winner:
            return sala.winner.user.username
        else:
            return False
