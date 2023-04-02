from django.urls import path
from WebSocket.consumers import MyConsumer

websocket_urlpatterns = [
    path('ws/foo/<group>/', MyConsumer.as_asgi()),
]
