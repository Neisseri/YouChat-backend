import random
from django.test import TestCase, Client
from User.models import User, UserGroup, Contacts, FriendRequests, TokenPair
import json
from websockets.sync.client import connect
from django.http import HttpResponse, HttpRequest
import time
import pytest

from channels.testing import WebsocketCommunicator
from WebSocket.consumers import MyConsumer
from channels.routing import URLRouter
from django.urls import path
# Create your tests here.
class WebSocketTests(TestCase):

    # Initializer
    def setUp(self):
        # alice = User.objects.create(name = "swim17", password = "abc1234567", 
        #                             nickname = "Alice", email = "17@swim.com")
        
        # bob = User.objects.create(name = "swim11", password = "abc12345678", 
        #                             nickname = "Bob", email = "11@swim.com")
        pass
        
    async def test_my_consumer(self):
        application = URLRouter([
            path('ws/message/', MyConsumer.as_asgi()),
        ])
        communicator = WebsocketCommunicator(application, "/ws/message/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # Test sending text
        send_message = {
            "type": "user_auth",
            "id": 1
        }
        await communicator.send_json_to(send_message)
        response = await communicator.receive_json_from()
        recv_message = {"code": 1, "info": "User Not Existed"}
        assert response == recv_message
        # Close
        await communicator.disconnect()

