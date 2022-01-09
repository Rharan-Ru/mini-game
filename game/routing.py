from django.urls import re_path

from .consumers import GameFindRoomConsumer, GameRoomConsumer


websocket_urlpatterns = [
    # Game url patterns
    re_path(r'ws/game/(?P<room_pk>\w+)/$', GameRoomConsumer.as_asgi()),
    re_path(r'ws/game/', GameFindRoomConsumer.as_asgi()),
]
