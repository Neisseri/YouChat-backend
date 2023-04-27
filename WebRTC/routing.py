from django.urls import re_path
from WebRTC import consumers

websocket_urlpatterns = [
    re_path('ws/webrtc/', consumers.WebRTCConsumer.as_asgi()),
]
