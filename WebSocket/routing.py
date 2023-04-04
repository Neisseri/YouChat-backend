from django.urls import path
from WebSocket.consumers import MyConsumer

websocket_urlpatterns = [
    path('/ws/message/', MyConsumer.as_asgi()),
]
