import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "st_im_django.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import WebSocket.routing
from django.core.asgi import get_asgi_application

import os

# for voice communication
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "st_im_django.settings")

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            WebSocket.routing.websocket_urlpatterns
        )
    ),
    
    # "websocket": URLRouter([
    #     path("ws/webrtc/", consumers.WebRTCConsumer.as_asgi()),
    # ])
})
