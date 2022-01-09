from django.urls import path
from .views import HomeView, RoomGameView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<int:room_pk>/', RoomGameView.as_view(), name='room_game')
]
