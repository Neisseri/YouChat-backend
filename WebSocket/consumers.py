import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from User.models import User
from Session.models import Session, UserAndSession, Message

from channels.generic.websocket import AsyncWebsocketConsumer

from channels.db import database_sync_to_async

class MyConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_user_by_id(self, id):
        return User.objects.filter(user_id=id).first()

    @database_sync_to_async
    def get_sessions_by_user(self):
        return UserAndSession.objects.filter(user=self.user).select_related('session')

    @database_sync_to_async
    def get_session_by_id(self, session_id):
        return Session.objects.filter(session_id).first()
    
    @database_sync_to_async
    def get_messages(self, session, message_scale):
        return Message.objects.filter(session=session).order_by("-time")[:message_scale]

    @database_sync_to_async
    def add_message(self, text, timestamp, session, user):
        return Message(text=text, time=timestamp, session=session, sender=user)

    @database_sync_to_async
    def delete_message(self, message_id):
        message = Message['message_id']
        message.delete()

    # user authority verification
    async def user_auth(self, id):

        self.user = await self.get_user_by_id(id)
        sessions = await self.get_sessions_by_user()

        for session in sessions:
            room_name = session.session.name
            room_group_name = "chat_%s" % room_name
            await self.channel_layer.group_add(room_group_name)
        
        response_data = {"code": 0, "info": "Succeed", "type": "user_auth"}
        await self.send(text_data=json.dumps(response_data))

    # pull message from specific session
    async def message_pull(self, session_id, message_scale):

        session = await self.get_session_by_id(session_id)
        messages = await self.get_messages(session, message_scale)
        response_data = {"code": 0, "info": "Succeed", "type": "pull", "messages": []}
        for message in messages:
            message_data = {
                "senderId": message.sender.user_id,
                "timestamp": message.time,
                "message": message.text
            }
            response_data["messages"].append(message_data)
        await self.send(text_data=json.dumps(response_data))

    # send message
    async def send_message(self, session_id, timestamp, text):

        session = await self.get_session_by_id(session_id)
        message = await self.add_message(text, timestamp, session, self.user)

        response = {
	        "code": 0,
	        "info": "Succeed",
	        "type": "send",
	        "sessionId": session_id,
	        "senderId": self.user.user_id,
	        "timestamp": timestamp,
	        "messageId": message.message_id,
	        "message": text 
        }
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": response}
        )
        

    # start up websocket connection
    async def connect(self):
        await self.accept()

    # end websocket connection
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json['type']

        if type == 'user_auth':
            id = text_data_json['id']
            self.user_auth(id)
        elif type == 'pull':
            session_id = text_data_json['sessionId']
            message_scale = text_data_json['messageScale']
            self.message_pull(session_id, message_scale)
        elif type == 'send':
            session_id = text_data_json['sessionId']
            timestamp = text_data_json['timestamp']
            text = text_data_json['message']
            self.send_message(session_id, timestamp, text)
        elif type == 'delete':
            message_id = text_data_json['messageId']
            await self.delete_message(message_id)
            response = {
                "code": 0,
                "info": "Succeed",
                "type": "delete",
                "messageId": 123
            }
            await self.send(text_data=json.dumps(response))

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
