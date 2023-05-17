from django.test import TestCase
from User.models import User, UserGroup, Contacts
from Session.models import Session, UserAndSession
import time
import time

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

    async def test_my_consumer(self):
        application = URLRouter([
            path('ws/message/', MyConsumer.as_asgi()),
        ])
        communicator1 = WebsocketCommunicator(application, "/ws/message/")
        communicator2 = WebsocketCommunicator(application, "/ws/message/")
        connected1, subprotocol1 = await communicator1.connect()
        connected2, subprotocol1 = await communicator2.connect()
        assert connected1, connected2
        # Test sending text
        send_message_1 = {
            "type": "user_auth",
            "id": 1
        }
        await communicator1.send_json_to(send_message_1)
        response1 = await communicator1.receive_json_from()
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "user_auth"
        }
        assert response1 == recv_message
        
        send_message_2 = {
            "type": "user_auth",
            "id": 2
        }
        await communicator2.send_json_to(send_message_2)
        response2 = await communicator2.receive_json_from()
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "user_auth"
        }
        assert response2 == recv_message

        timestamp = time.time()

        send_message_1 = {
            "type": "send",
            "sessionId": 1,
            "timestamp": timestamp,
            "message": "Hello World",
            "messageType": "text",
            "reply": -1
        }
        await communicator1.send_json_to(send_message_1)
        response1 = await communicator1.receive_json_from()
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "send",
            "sessionId": 1,
            "senderId": 1,
            "senderName": "swim17",
            "timestamp": timestamp,
            "messageId": 1,
            "message": "Hello World",
            "messageType": "text"
        }
        assert response1 == recv_message

        response2 = await communicator2.receive_json_from()
        assert response2 == recv_message

        send_message = {
            "type": "pull",
            "id": 1,
            "sessionId": 1,
            "messageScale": 30,
            "timestamp": 1145141919810
        }
        await communicator1.send_json_to(send_message)
        response = await communicator1.receive_json_from()
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "pull",
            "messages": [
                {
                    "senderId": 1,
                    "senderName": "swim17",
                    "timestamp": timestamp,
                    "messageId": 1,
                    "message": "Hello World",
                    "messageType": "text",
                    "reply": -1
                }
            ]
        }
        assert response == recv_message

        send_message = {
            "type": "delete",
            "id": 1,
            "messageId": 1,
            "role": 0
        }
        await communicator1.send_json_to(send_message)
        response = await communicator1.receive_json_from()
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "delete",
            "messageId": 1
        }
        # assert response == recv_message

        response2 = await communicator2.receive_json_from()
        # assert response2 == recv_message

        # Close
        await communicator1.disconnect()
        await communicator2.disconnect()

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

    async def test_my_consumer_session_not_exist(self):
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
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "user_auth"
        }
        assert response == recv_message
        send_message = {
            "type": "pull",
            "id": 1,
            "sessionId": 114514,
            "messageScale": 30,
            "timestamp": 1145141919810
        }
        await communicator.send_json_to(send_message)
        response = await communicator.receive_json_from()
        recv_message = {"code": 2, "info": "Session Not Existed"}
        assert response == recv_message
        #Close
        await communicator.disconnect()

    async def test_my_consumer_delete_message_not_exist(self):
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
        recv_message = {
            "code": 0,
            "info": "Succeed",
            "type": "user_auth"
        }
        assert response == recv_message
        send_message = {
            "type": "delete",
            "id": 1,
            "messageId": 114514,
            "role": 0
        }
        await communicator.send_json_to(send_message)
        response = await communicator.receive_json_from()
        recv_message = {"code": 2, "info": "Message Not Existed"}
        assert response == recv_message
        #Close
        await communicator.disconnect()
    