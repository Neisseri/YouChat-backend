import json

from channels.generic.websocket import AsyncWebsocketConsumer

from User.models import User
from Session.models import Session, UserAndSession, Message

from channels.db import database_sync_to_async

import constants.session as constants

import datetime

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
    def get_session(self, session_id):
        session = Session.objects.filter(session_id=session_id).first()
        return session
    
    @database_sync_to_async
    def get_message(self, message_id):
        message = Message.objects.filter(message_id = message_id).first()
        return message
    
    @database_sync_to_async
    def get_message_test(self, message: Message):
        text = message.text
        return text
    
    @database_sync_to_async
    def get_message_sender(self, message: Message):
        sender = message.sender
        return sender
    
    @database_sync_to_async
    def get_message_time(self, message: Message):
        time = message.time
        return time

    @database_sync_to_async
    def get_messages(self, session_id, message_scale):
        session = Session.objects.filter(session_id=session_id).first()
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

    def check_invalid_message(self, text):
        if len(text) < constants.MAX_MESSAGE_LENGTH:
            return True
        
        return False

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
        
        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if not self.get_session(session_id):
            response_data = {"code": 2, "info": "Session Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return

        message_list = await self.get_messages(session_id, message_scale)
        response_data = {"code": 0, "info": "Succeed", "type": "pull", "messages": []}
        response_data["messages"] = message_list
        await self.send(text_data=json.dumps(response_data))

    # send message
    async def send_message(self, session_id, timestamp, text):

        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if not await self.get_session(session_id):
            response_data = {"code": 2, "info": "Session Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if await self.check_invalid_message(text):
            response_data = {"code": 3, "info": "Message Invalid"}
            await self.send(text_data=json.dumps(response_data))
            return

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
        message = await self.get_message(message_id)
        sender = await self.get_message_sender(message)
        time = await self.get_message_time(message)

        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if not message:
            response_data = {"code": 2, "info": "Message Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if sender != self.user:
            response_data = {"code": 3, "info": "Permission Denied"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        date1 = datetime.fromtimestamp(time)
        date2 = datetime.datetime.now()
        seconds = (date2 - date1).total_seconds()

        if seconds > constants.WITHDRAW_TIME:
            response_data = {"code": 4, "info": "Time Limit Exceeded"}
            await self.send(text_data=json.dumps(response_data))
            return

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
        self.user = None
        self.room_name_list = None
        self.user_id = None

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
