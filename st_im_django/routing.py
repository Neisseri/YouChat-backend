import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "st_im_django.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import WebSocket.routing
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            WebSocket.routing.websocket_urlpatterns
        )
    ),
})
