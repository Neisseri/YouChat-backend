import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from User.models import User
from Session.models import Session, UserAndSession

from channels.generic.websocket import AsyncWebsocketConsumer

class MyConsumer(AsyncWebsocketConsumer):

    async def user_auth(self, id):
        user = User.objects.filter(user_id=id).first()
        sessions = UserAndSession.objects.filter(user=user).select_related('session')

        for session in sessions:
            room_name = session.session.name
            room_group_name = "chat_%s" % room_name
            await self.channel_layer.group_add(room_group_name)
        
        response_data = {"code": 0, "info": "Succeed", "type": "user_auth"}
        await self.send(text_data=json.dumps(response_data))

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["group"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

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

        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
