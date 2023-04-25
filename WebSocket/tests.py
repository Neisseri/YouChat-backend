import random
from django.test import TestCase, Client
from User.models import User, UserGroup, Contacts, FriendRequests, TokenPair
from Session.models import Session, UserAndSession
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
        alice = User.objects.create(name = "swim17", password = "abc1234567", 
                                    nickname = "Alice", email = "17@swim.com")
        alice.save()
        
        bob = User.objects.create(name = "swim11", password = "abc12345678", 
                                    nickname = "Bob", email = "11@swim.com")
        bob.save()

        userGroup1 = UserGroup.objects.create(user=alice)
        userGroup1.save()

        userGroup2 = UserGroup.objects.create(user=bob)
        userGroup2.save()

        contact1 = Contacts.objects.create(user=alice, friend=bob, group=userGroup1)
        contact1.save()

        contact2 = Contacts.objects.create(user=bob, friend=alice, group=userGroup2)
        contact2.save()

        session = Session.objects.create(name='friend', type=1, friend_contacts=contact1, host=alice)
        session.save()

        userAndSession1 = UserAndSession.objects.create(user=alice, session=session, permission=0)
        userAndSession1.save()

        userAndSession2 = UserAndSession.objects.create(user=bob, session=session, permission=1)
        userAndSession2.save()

        pass
        
    async def test_my_consumer_user_not_exist(self):
        application = URLRouter([
            path('ws/message/', MyConsumer.as_asgi()),
        ])
        communicator = WebsocketCommunicator(application, "/ws/message/")
        connected, subprotocol = await communicator.connect()
        assert connected
        # Test sending text
        send_message = {
            "type": "user_auth",
            "id": 3
        }
        await communicator.send_json_to(send_message)
        response = await communicator.receive_json_from()
        recv_message = {"code": 1, "info": "User Not Existed"}
        assert response == recv_message
        # Close
        await communicator.disconnect()

    