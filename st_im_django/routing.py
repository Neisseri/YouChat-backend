import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "st_im_django.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import WebSocket.routing
from django.core.asgi import get_asgi_application

# for voice communication
from WebRTC import WebRTCConsumer
from django.urls import path
from django.urls import re_path

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            WebSocket.routing.websocket_urlpatterns + [re_path('ws/webrtc/', WebRTCConsumer.as_asgi())]
        )
    ),
})