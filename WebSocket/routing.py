from django.urls import path
from WebSocket.consumers import MyConsumer, ChatConsumer

websocket_urlpatterns = [
    path('ws/message/', MyConsumer.as_asgi()),
]
