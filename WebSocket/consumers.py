import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from User.models import User
from Session.models import Session, UserAndSession, Message

from channels.db import database_sync_to_async

class MyConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user_by_id(self, id):
        return User.objects.filter(user_id=id).first()

    @database_sync_to_async
    def get_sessions_by_user(self):
        sessions =  UserAndSession.objects.filter(user=self.user).select_related('session')
        room_name_list = []
        for session in sessions:
            room_name_list.append(session.session.session_id)
        return room_name_list

    @database_sync_to_async
    def get_session_id_by_message_id(self, message_id):
        message = Message.objects.filter(message_id=message_id).first()
        return message.session.session_id
    
    @database_sync_to_async
    def get_messages(self, session_id, message_scale):
        session = Session.objects.get(session_id=session_id)
        if not session:
            return None
        messages = Message.objects.filter(session=session).order_by("-time")[:message_scale]
        message_list = []
        for message in messages:
            message_data = {
                "senderId": message.sender.user_id,
                "timestamp": message.time,
                "message": message.text
            }
            message_list.append(message_data)
        return message_list

    @database_sync_to_async
    def add_message(self, text, timestamp, session_id, user_id):
        user = User.objects.get(user_id=user_id)
        session = Session.objects.get(session_id=session_id)
        message = Message(text=text, time=timestamp, session=session, sender=user)
        message.save()
        return message.message_id


    @database_sync_to_async
    def delete_message(self, message_id):
        message = Message.objects.filter(message_id=message_id).first()
        message.delete()

    # user authority verification
    async def user_auth(self, id):

        self.user = await self.get_user_by_id(id)
        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        self.user_id = id
        self.room_name_list = await self.get_sessions_by_user()

        for room_name in self.room_name_list:
            room_group_name = "chat_%s" % room_name
            await self.channel_layer.group_add(room_group_name, self.channel_name)
        
        response_data = {"code": 0, "info": "Succeed", "type": "user_auth"}
        await self.send(text_data=json.dumps(response_data))

    # pull message from specific session
    async def message_pull(self, session_id, message_scale):

        message_list = await self.get_messages(session_id, message_scale)
        if not message_list:
            response_data = {
                "code": 1,
                "info": "User Not Existed"
            }
            await self.send(text_data=json.dumps(response_data))
            return
        response_data = {"code": 0, "info": "Succeed", "type": "pull", "messages": []}
        response_data["messages"] = message_list
        await self.send(text_data=json.dumps(response_data))

    # send message
    async def send_message(self, session_id, timestamp, text):

        message_id = await self.add_message(text, timestamp, session_id, self.user_id)

        response = {
	        "code": 0,
	        "info": "Succeed",
	        "type": "send",
	        "sessionId": session_id,
	        "senderId": self.user_id,
	        "timestamp": timestamp,
	        "messageId": message_id,
	        "message": text 
        }

        # Send message to room group
        await self.channel_layer.group_send(
            "chat_%s" % session_id, {"type": "chat_message", "message": response}
        )

    async def group_delete_message(self, message_id):

        session_id = await self.get_session_id_by_message_id(message_id)

        response = {
	        "code": 0,
	        "info": "Succeed",
	        "type": "send",
	        "messageId": message_id
        }

        await self.send(text_data=json.dumps(response))
        # Send message to room group
        await self.channel_layer.group_send(
            "chat_%s" % session_id, {"type": "chat_message", "message": response}
        )
        

    # start up websocket connection
    async def connect(self):
        await self.accept()

    # end websocket connection
    async def disconnect(self, close_code):
        # Leave room group
        for room_name in self.room_name_list:
            room_group_name = "chat_%s" % room_name
            await self.channel_layer.group_discard(room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]

        if type == 'user_auth':
            id = text_data_json['id']
            await self.user_auth(id)
        elif type == 'pull':
            session_id = text_data_json['sessionId']
            message_scale = text_data_json['messageScale']
            await self.message_pull(session_id, message_scale)
        elif type == 'send':
            session_id = text_data_json['sessionId']
            timestamp = text_data_json['timestamp']
            text = text_data_json['message']
            await self.send_message(session_id, timestamp, text)
        elif type == 'delete':
            message_id = text_data_json['messageId']
            await self.group_delete_message(message_id)
            await self.delete_message(message_id)
        else:
            raise RuntimeError

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = "demo"
        # self.room_group_name = "chat_%s" % self.room_name

        # # Join room group
        # await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        pass

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.send(text_data=json.dumps({"message": message}))

        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name, {"type": "chat_message", "message": message}
        # )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
