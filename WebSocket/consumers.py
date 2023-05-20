import json

from channels.generic.websocket import AsyncWebsocketConsumer

from User.models import User
from Session.models import Session, UserAndSession, Message, UserandMessage

from channels.db import database_sync_to_async

import constants.session as constants

import datetime

class MyConsumer(AsyncWebsocketConsumer):
    all_groups = {}
        
    @database_sync_to_async
    def set_channel_name(self, user_id, channel_name):
        user = User.objects.filter(user_id=user_id).first()
        if user:
            user.channel_name = channel_name
            user.save()
        return True
    
    @database_sync_to_async
    def get_channel_name(self, user_id):
        user = User.objects.filter(user_id=user_id).first()
        return user.channel_name
  
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
    def get_users_by_session(self, session_id):
        session = Session.objects.filter(session_id=session_id).first()
        users =  UserAndSession.objects.filter(session=session).select_related('user')
        user_list = []
        for user in users:
            user_list.append(user.user.channel_name)
        return user_list

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
    def get_messages(self, session_id, message_scale, timestamp):
        updateReadTime = False

        session = Session.objects.filter(session_id=session_id).first()
        if not session:
            return None, updateReadTime
        messages = Message.objects.filter(session=session).order_by("-time")
        messages = list(messages)

        delete_ind = []
        for i in range(len(messages)):
            message = messages[i]
            umbond = UserandMessage.objects.filter(user = self.user, message = message).first()
            if (not umbond) or umbond.is_delete:
                delete_ind.append(i)
        delete_ind.reverse()
        for i in delete_ind:
            messages.pop(i)

        bond = UserAndSession.objects.filter(user = self.user, session = session).first()
        if bond.read_time < timestamp:
            bond.read_time = timestamp
            bond.save()

            updateReadTime = True

        def get_time_pos(messages, timestamp):
            for pos in range(len(messages)):
                message = messages[pos]
                if message.time <= timestamp:
                    return pos
                
            return len(messages)

        timepos = get_time_pos(messages, timestamp)
        lst_pos = timepos + message_scale if timepos + message_scale <= len(messages) else len(messages)
        messages = messages[timepos : lst_pos]

        message_list = []
        for message in messages:
            message_data = {
                "senderId": message.sender.user_id,
                "senderName": message.sender.name,
                "timestamp": message.time,
                "messageId": message.message_id,
                "message": message.text,
                "reply": message.reply,
                "messageType": message.message_type
            }
            message_list.append(message_data)
        return message_list, updateReadTime

    @database_sync_to_async
    def add_message(self, text, timestamp, session_id, user_id, message_type = "text", reply = -1):
        user = User.objects.get(user_id=user_id)
        session = Session.objects.get(session_id=session_id)
        message = Message(text=text, time=timestamp, session=session, sender=user, message_type = message_type, reply = reply)
        message.save()

        usbonds = UserAndSession.objects.filter(session = session)
        
        for usbond in usbonds:
            suser = usbond.user
            umbond = UserandMessage(user = suser, message = message)
            umbond.save()

        return message.message_id

    @database_sync_to_async
    def delete_message(self, message_id):
        message = Message.objects.filter(message_id=message_id).first()
        if message:
            message.delete()

    @database_sync_to_async
    def check_invalid_message(self, text):
        if len(text) < constants.MAX_MESSAGE_LENGTH:
            return True
        return False

    # user authority verification
    async def user_auth(self, id):
        #self.channel_name = "specific." + "channel_%s" % id

        if self.user_id:
            response_data = {"code": 0, "info": "Succeed", "type": "user_auth"}
            await self.send(text_data=json.dumps(response_data))
            return

        self.user = await self.get_user_by_id(id)
        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        self.user_id = id
        self.room_name_list = await self.get_sessions_by_user()
        await self.set_channel_name(self.user_id, self.channel_name)

        for room_name in self.room_name_list:
            room_group_name = "chat_%s" % room_name
            # if MyConsumer.all_groups.get(room_group_name) is not None:
            #     MyConsumer.all_groups[room_group_name].append(self)
            # else:
            #     MyConsumer.all_groups[room_group_name] = [self]
            # await self.channel_layer.group_add(room_group_name, self.channel_name)
            await self.channel_layer.group_add(room_group_name, await self.get_channel_name(self.user_id))
        
        response_data = {"code": 0, "info": "Succeed", "type": "user_auth"}
        await self.send(text_data=json.dumps(response_data))

    # pull message from specific session
    async def message_pull(self, session_id, message_scale, timestamp):
        
        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if not await self.get_session(session_id):
            response_data = {"code": 2, "info": "Session Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return

        message_list, updateReadTime = await self.get_messages(session_id, message_scale, timestamp)

        if updateReadTime:
            response = {
                "type": "updateReadTime",
                "readTime": timestamp,
                "userId": self.user.user_id
            }
            
            await self.channel_layer.group_send(
                "chat_%s" % session_id, {"type": "chat_message", "message": response}
            )

        response_data = {"code": 0, "info": "Succeed", "type": "pull", "messages": []}
        response_data["messages"] = message_list
        await self.send(text_data=json.dumps(response_data))

    # send message
    async def send_message(self, session_id, timestamp, text, message_type = "text", reply = -1):

        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        # if not await self.get_session(session_id):
        #     response_data = {"code": 2, "info": "Session Not Existed"}
        #     await self.send(text_data=json.dumps(response_data))
        #     return

        if not await self.check_invalid_message(text):
            response_data = {"code": 3, "info": "Message Invalid"}
            await self.send(text_data=json.dumps(response_data))
            return

        message_id = await self.add_message(text, timestamp, session_id, self.user_id, message_type, reply)
        
        response = {
	        "code": 0,
	        "info": "Succeed",
	        "type": "send",
	        "sessionId": session_id,
	        "senderId": self.user_id,
            "senderName": self.user.name,
	        "timestamp": timestamp,
	        "messageId": message_id,
	        "message": text,
            "messageType": message_type
        }


        # for consumers in MyConsumer.all_groups["chat_%s" % session_id]:
        #     consumers: MyConsumer
        #     await consumers.message_from_others(response)

        # Send message to room group
        await self.channel_layer.group_send(
            "chat_%s" % session_id, {"type": "chat_message", "message": response}
        )
        
    async def videoconnect(self, session_id, fro, too, req_josn):
        
        type = req_josn['type']
        data = req_josn['data']
        
        response = {
	        "code": 0,
	        "info": "Succeed",
            "sessionId": session_id,
	        "type": type,
	        "from": fro,
            "to": too,
            "data": data
        }

        await self.channel_layer.group_send(
            "chat_%s" % session_id, {"type": "chat_message", "message": response}
        )
        
    async def notice_video(self, session_id, fro, too, req_josn):
        
        type = req_josn['type']
        status = req_josn['status']
        is_video = req_josn['is_video']
        
        response = {
	        "code": 0,
	        "info": "Succeed",
            "sessionId": session_id,
	        "type": type,
	        "from": fro,
            "to": too,
            "is_video": is_video,
            "status": status
        }

        await self.channel_layer.group_send(
            "chat_%s" % session_id, {"type": "chat_message", "message": response}
        )
        

    async def group_delete_message(self, message_id, role):

        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        message = await self.get_message(message_id)
        
        if not message:
            response_data = {"code": 2, "info": "Message Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        session_id = await self.get_session_id_by_message_id(message_id)
        sender = await self.get_message_sender(message)
        time = await self.get_message_time(message)
        
        if sender != self.user and role == 2:
            response_data = {"code": 3, "info": "Permission Denied"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        # await self.send(text_data=json.dumps({"code": 000, "info": "test"}))
        # date1 = datetime.datetime.fromtimestamp(time)
        # await self.send(text_data=json.dumps({"code": 999, "info": "test"}))
        # date2 = datetime.datetime.now()
        # await self.send(text_data=json.dumps({"code": 888, "info": "test"}))
        # seconds = (date2 - date1).total_seconds()
        # await self.send(text_data=json.dumps({"code": 777, "info": "test"}))

        # if seconds > constants.WITHDRAW_TIME and role == 2:
        #     await self.send(text_data=json.dumps({"code": 666, "info": "test"}))
        #     response_data = {"code": 4, "info": "Time Limit Exceeded"}
        #     await self.send(text_data=json.dumps(response_data))
        #     return

        await self.delete_message(message_id)

        response = {
	        "code": 0,
	        "info": "Succeed",
	        "type": "delete",
	        "messageId": message_id
        }

        # await self.send(text_data=json.dumps(response))
        # Send message to room group
        await self.channel_layer.group_send(
            "chat_%s" % session_id, {"type": "chat_message", "message": response}
        )

    async def create_group(self, session_id):
        
        if not self.user:
            response_data = {"code": 1, "info": "User Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        if not await self.get_session(session_id):
            response_data = {"code": 2, "info": "Session Not Existed"}
            await self.send(text_data=json.dumps(response_data))
            return
        
        user_list = await self.get_users_by_session(session_id)

        for user in user_list:
            channel_name = user
            room_group_name = "chat_%s" % session_id
            await self.channel_layer.group_add(room_group_name, channel_name)

        response = {"code": 0, "info": "Succeed", "type": "new_session", "sessionId": session_id}
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
        await self.set_channel_name(self.user_id, "None")
        if self.room_name_list:
            for room_name in self.room_name_list:
                room_group_name = "chat_%s" % room_name
                await self.channel_layer.group_discard(room_group_name, self.channel_name)
                # MyConsumer.all_groups[room_group_name].remove(self)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        type = text_data_json["type"]

        if type == 'user_auth':
            id = text_data_json['id']
            await self.user_auth(id)
        elif type == 'pull':
            # id = dict(text_data_json).get('id')
            # if id:
            #     await self.user_auth(id)
            session_id = text_data_json['sessionId']
            message_scale = text_data_json['messageScale']
            timestamp = text_data_json['timestamp']
            await self.message_pull(session_id, message_scale, timestamp)
        elif type == 'send':
            # id = dict(text_data_json).get('id')
            # if id:
            #     await self.user_auth(id)
            session_id = text_data_json['sessionId']
            timestamp = text_data_json['timestamp']
            text = text_data_json['message']
            message_type = text_data_json['messageType']
            reply = -1
            if "reply" in text_data_json.keys():
                reply = text_data_json['reply']
            await self.send_message(session_id, timestamp, text, message_type, reply)
        elif type == 'answer' or type == 'offer' or type == 'candid':
            session_id = text_data_json['sessionId']
            fro = text_data_json['from']
            too = text_data_json['to']
            await self.videoconnect(session_id, fro, too, text_data_json)
        elif type == 'notice_video':
            session_id = text_data_json['sessionId']
            fro = text_data_json['from']
            too = text_data_json['to']
            await self.notice_video(session_id, fro, too, text_data_json)
        elif type == 'delete':
            # id = dict(text_data_json).get('id')
            # if id:
            #     await self.user_auth(id)
            message_id = text_data_json['messageId']
            role = text_data_json['role']
            await self.group_delete_message(message_id, role)
        elif type == 'new_session':
            session_id = text_data_json['sessionId']
            await self.create_group(session_id)
        else:
            raise RuntimeError

    # Receive message from room group
    async def chat_message(self, event):
        message = dict(event["message"])

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))

    async def message_from_others(self, message):

        await self.send(text_data=json.dumps(message))
