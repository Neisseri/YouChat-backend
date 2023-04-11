import random
from django.test import TestCase, Client
from User.models import User, UserGroup, Contacts, FriendRequests, TokenPair
import json
from websockets.sync.client import connect
from django.http import HttpResponse, HttpRequest
import time

# Create your tests here.
class WebSocketTests(TestCase):

    # Initializer
    def setUp(self):
        alice = User.objects.create(name = "swim17", password = "abc1234567", 
                                    nickname = "Alice", email = "17@swim.com")
        
        bob = User.objects.create(name = "swim11", password = "abc12345678", 
                                    nickname = "Bob", email = "11@swim.com")
        
    # Utility Functions

    # Now start testcases.
    def test_ws_message(self):
        
        # with connect("ws://127.0.0.1:8000/ws/message/") as websocket:
        #     websocket.send(json.dumps({
        #         "type": "user_auth",
        #         "id": 1
        #     }))
        #     message = websocket.recv()
        #     self.assertEqual(message.json()['code'], 0)

        ws = connect("ws://127.0.0.1:8000/ws/message/")
        ws.send(json.dumps({
            "type": "user_auth",
            "id": 1
        }))
        message = ws.recv()
        self.assertEqual(message.json()['code'], 0)
    
