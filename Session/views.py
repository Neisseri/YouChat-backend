from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from utils.utils_require import CheckRequire, require
from constants.session import DEFAULT_MESSAGE_SCALE, BUILT_SESSION, FRIEDN_SESSION
from Session.models import Session, UserAndSession, Message, UserandMessage
from constants.session import SESSION_HOST, SESSION_MANAGER, SESSION_MEMBER, SESSION_REQUEST
from User.models import User, UserGroup, Contacts
from utils.utils_request import request_failed, request_success, return_field, BAD_METHOD
import json
import base64
import requests
import urllib.parse, urllib.request
import http.client
import hashlib
from urllib import parse
import random
import uuid
import wave
import time
from WebSocket.consumers import MyConsumer

# check if the char is a number or English letter
def check_number_letter(c: any):
    if ('0' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z'):
        return True
    else:
        return False

# extract the fields in request.body for /user GET
# def check_for_session_data(body):

#     user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
#     session_name = require(body, "sessionName", "string", err_msg="Missing or error type of [sessionName]")
#     session_id = require(body, "sessionId", "int", err_msg="Missing or error type of [sessionId]")
#     message_scale = body["messageScale"] if "messageScale" in body.keys() else DEFAULT_MESSAGE_SCALE

#     assert 5 <= len(user_name) <= 20, "Bad length of [userName]"
#     assert 5 <= len(session_name) <= 20, "Bad length of [sessionName]"

#     for i in range(0, len(user_name)):
#         assert (check_number_letter(user_name[i]) or user_name[i] == '_'), "Invalid char in [userName]"
        
#     for i in range(0, len(session_name)):
#         assert (check_number_letter(user_name[i]) or user_name[i] == '_'), "Invalid char in [sessionName]"

#     return user_name, session_name, session_id, message_scale

@CheckRequire
def manage_chatroom(req: HttpRequest):

    body = json.loads(req.body.decode("utf-8"))
    
    if req.method == "PUT":
        user_id = body['userId']
        session_id = body['sessionId']

        session = Session.objects.filter(session_id = session_id).first()
        user = User.objects.filter(user_id = user_id).first()

        if not session:
            return request_failed(2, "Session Not Existed", 400)
        
        if not user:
            return request_failed(1, "User Not Existed or Permission Denied", 400)
        
        applicantId = body["applicantId"]
        applicantUser = User.objects.filter(user_id = applicantId).first()

        if not applicantUser:
            return request_failed(3, "Applicant Not Existed", 400)
        
        role = body["role"]
        
        manager_bond = UserAndSession.objects.filter(user = user, session = session).first()
        applicant_bond = UserAndSession.objects.filter(user = applicantUser, session = session).first()

        if not manager_bond or (manager_bond.permission != SESSION_HOST and manager_bond.permission != SESSION_MANAGER):
            return request_failed(1, "User Not Existed or Permission Denied", 400)

        if not applicant_bond:
            return request_failed(3, "Applicant Not Existed", 400)

        applicant_bond.permission = role
        applicant_bond.save()

        return request_success()

    else:
        return request_failed(-1, 'Bad Method', 400)

@CheckRequire
def setting(req: HttpRequest):

    if req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))

        user_id = body["userId"]
        session_id = body["sessionId"]
        isMute = body["isMute"]
        isTop = body["isTop"]

        user = User.objects.get(user_id = user_id)
        session = Session.objects.get(session_id = session_id)

        if not user or not session:
            return request_failed(2, "Set Failed", 400)
        
        bond = UserAndSession.objects.filter(user = user, session = session).first()

        if not bond:
            return request_failed(2, "Set Failed", 400)

        bond.isMute = isMute
        bond.isTop = isTop
        bond.save()

        return request_success()

    else:
        return request_failed(-1, 'Bad Method', 400)
    
@CheckRequire
def delete(req: HttpRequest):
    if req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))

        user_id = body["userId"]
        message_id = body["messageId"]

        user = User.objects.get(user_id = user_id)
        message = Message.objects.get(message_id = message_id)

        if not message:
            return request_failed(2, "Message Not Existed", 400)

        if not user:
            return request_failed(2, "User Not Existed", 400)
        
        bond = UserandMessage.objects.filter(user = user, message = message).first()

        if not bond:
            return request_failed(2, "UserandMessage bond Not Existed", 400)
        
        bond.is_delete = True
        bond.save()
        
        return request_success()

    else:
        return request_failed(-1, 'Bad Method', 400)
    
@CheckRequire
def history(req: HttpRequest):
    if req.method == "GET":
        session_id = req.GET.get("sessionId")
        session = Session.objects.filter(session_id=session_id).first()

        if not session:
            return request_failed(2, 'Session Not exists', 400)
        
        user_id = req.GET.get("userId")
        user = User.objects.get(user_id = user_id)

        if not user:
            return request_failed(2, 'User Not exists', 400)
        
        messages = Message.objects.filter(session=session).order_by("-time")
        messages = list(messages)

        delete_ind = []
        for i in range(len(messages)):
            message = messages[i]
            umbond = UserandMessage.objects.filter(user = user, message = message).first()
            if not umbond or umbond.is_delete:
                delete_ind.append(i)
        delete_ind.reverse()
        for i in delete_ind:
            messages.pop(i)

        message_list = []
        for message in messages:
            message_data = {
                "senderId": message.sender.user_id,
                "senderName": message.sender.name,
                "timestamp": message.time,
                "messageId": message.message_id,
                "message": message.text,
                "messageType": message.message_type,
                "reply": 0
            }
            message_list.append(message_data)
        
        return request_success({"sessionId":session_id, "userId":user_id, "messages":message_list})

    else:
        return request_failed(-1, 'Bad Method', 400)


@CheckRequire
def image(req: HttpRequest):
    if req.method == "GET":
        image_id = req.GET.get("id")

        message = Message.objects.get(message_id = image_id)

        if not message or message.message_type != "photo":
            return request_failed(2, "Image Not Existed", 400)
        
        return request_success({"image": message.text})

    else:
        return request_failed(-1, 'Bad Method', 400)

@CheckRequire
def join_chatroom(req: HttpRequest):

    if req.method == "GET":
        session_id = req.GET.get("id")
        session = Session.objects.get(session_id = session_id)
        bonds = UserAndSession.objects.filter(session = session)

        members = []
        for bond in bonds:
            user = bond.user
            info = {}
            info["id"] = user.user_id
            info["nickname"] = user.nickname
            info["readTime"] = bond.read_time
            info["role"] = bond.permission

            members.append(info)

        session_name = session.name

        return request_success({"sessionName": session_name, "sessionId":session_id, "members": members})

    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))

        user_id = body["userId"]
        session_id = body["sessionId"]

        session = Session.objects.filter(session_id = session_id).first()
        user = User.objects.filter(user_id = user_id).first()

        if not user:
            return request_failed(1, "User Not Existed", 400)
        
        if not session:
            return request_failed(2, "Session Not Existed", 400)
        
        bond = UserAndSession(permission = SESSION_REQUEST, user = user, session = session)
        bond.save()
        
        return request_success()
    
    elif req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))

        user_id = body["userId"]
        user = User.objects.filter(user_id = user_id).first()
        initial_list = body["initial"]

        if not user:
            return request_failed(2, "User Not Existed", 400)

        session_name = body["sessionName"]

        group = UserGroup.objects.filter(user=user, group_name = "me").first()
        if not group:
            group = UserGroup(user=user, group_name = "me")
            group.save()
        contacts = Contacts.objects.filter(user=user, friend=user, group = group).first()
        if not contacts:
            contacts = Contacts(user=user, friend=user, group = group)
            contacts.save()

        session = Session(name = session_name, host = user, friend_contacts = contacts, type = BUILT_SESSION)
        session.save()
        UserAndSession.objects.create(permission = SESSION_HOST, user = user, session = session)


        for id in initial_list:
            user = User.objects.get(user_id = id)
            bond = UserAndSession.objects.filter(user = user, session = session)
            if not bond:
                UserAndSession.objects.create(permission = SESSION_MEMBER, user = user, session = session)


        return request_success()

    elif req.method == "DELETE":
        body = json.loads(req.body.decode("utf-8"))
        
        session_id = body["sessionId"]
        user_id = body["userId"]
        session = Session.objects.filter(session_id = session_id).first()
        user = User.objects.filter(user_id = user_id).first()

        if not user:
            return request_failed(1, "User Not Existed", 400)
        
        if not session:
            return request_failed(2, "Session Not Existed", 400)
        
        UserAndSession.objects.get(session = session, user = user).delete()
        
        return request_success()

    else:
        return request_success()
    
    
@CheckRequire
def message(req: HttpRequest, id: int):

    if req.method == "GET":
        user = User.objects.filter(user_id = id).first()

        if not user:
            return request_failed(2, "UserId Not Exists", 400)

        sessionsbond = UserAndSession.objects.filter(user = user)

        session_info = []
        for bond in sessionsbond:
            session = bond.session

            info = {}
            info["sessionId"] = session.session_id
            info["sessionName"] = session.name
            info["sessionType"] = session.type

            info["isTop"] = bond.isTop
            info["isMute"] = bond.isMute
            
            read_time = bond.read_time

            messages = Message.objects.filter(session=session)

            if messages:
                messages = messages.order_by("-time")

            messages = list(messages)

            delete_ind = []
            for i in range(len(messages)):
                message = messages[i]
                umbond = UserandMessage.objects.filter(user = user, message = message).first()
                if (not umbond) or umbond.is_delete:
                    delete_ind.append(i)
            delete_ind.reverse()
            for i in delete_ind:
                messages.pop(i)

            if messages:
                message = messages[0]
                info["timestamp"] = message.time
                info["type"] = message.message_type
                info["lastSender"] = message.sender.name
                info["message"] = message.text
                if info["type"] == 'history':
                    info["message"] = "转发消息"

                def get_time_pos(messages, timestamp):
                    for pos in range(len(messages)):
                        message = messages[pos]
                        if message.time <= timestamp:
                            return pos
                        
                    return len(messages)
                
                timepos = get_time_pos(messages, read_time)

                info["unread"] = timepos

            else:
                info["timestamp"] = session.time
                info["type"] = "text"
                info["lastSender"] = ""
                info["message"] = ""

                info["unread"] = 0


            # user_binds = UserAndSession.objects.filter(session = session)
            # time_list = {}

            # for user_bind in user_binds:
            #     user = user_bind.user
            #     user_name = user.name

            #     timestamp = user_bind.read_time

            #     time_list[user_name] = timestamp

            # info["readTimeList"] = time_list

            session_info.append(info)

        def get_time(info):
            return info["timestamp"]
        
        session_info.sort(key=get_time)

        return request_success({"data": session_info})
    
    elif req.method == "POST":
        user = User.objects.filter(user_id = id).first()

        if not user:
            return request_failed(2, "User Not Existed", 400)

        body = json.loads(req.body.decode("utf-8"))

        session_id = body["sessionId"]
        session = Session.objects.get(session_id = session_id)

        if not session:
            return request_failed(3, "Session Not Existed", 400)

        timestamp = body["readTime"]

        bond = UserAndSession.objects.filter(user = user, session = session).first()

        bond.read_time = timestamp

        bond.save()

        return request_success()

    else:
        return BAD_METHOD

# 有道智云 https://ai.youdao.com/#/
def translate2chinese(text):

    youdao_url = 'https://openapi.youdao.com/api'   # 有道api地址

    # 需要翻译的文本
    translate_text = text

    # 翻译文本生成sign前进行的处理
    input_text = ""

    # 当文本长度小于等于20时，取文本
    if(len(translate_text) <= 20):
        input_text = translate_text
        
    # 当文本长度大于20时，进行特殊处理
    elif(len(translate_text) > 20):
        input_text = translate_text[:10] + str(len(translate_text)) + translate_text[-10:]
        
    time_curtime = int(time.time())   # 秒级时间戳获取
    app_id = "370b2d1bac6778ea"   # 应用id
    uu_id = uuid.uuid4()   # 随机生成的uuid数，为了每次都生成一个不重复的数。
    app_key = "Ibip0pFh5u1LDSZNgWjFMEkbiCrCmaxO"   # 应用密钥

    sign = hashlib.sha256((app_id + input_text + str(uu_id) + str(time_curtime) + app_key).encode('utf-8')).hexdigest()   # sign生成

    data = {
        'q':translate_text,   # 翻译文本
        'from':"auto",   # 源语言，设置为自动识别
        'to':"zh-CHS",   # 翻译语言：中文
        'appKey':app_id,   # 应用id
        'salt':uu_id,   # 随机生产的uuid码
        'sign':sign,   # 签名
        'signType':"v3",   # 签名类型，固定值
        'curtime':time_curtime,   # 秒级时间戳
    }

    r = requests.get(youdao_url, params = data).json()   
    # 获取返回的json()内容
    return r["translation"][0]   # 获取翻译内容


@CheckRequire
def message_translate(req: HttpRequest):

    # https://www.deepl.com/zh/pro-api/
    if req.method == 'PUT':

        body = json.loads(req.body.decode('utf-8'))
        text = body['text']
            
        translated_text = translate2chinese(text)
        
        response = {
            'code': 0,
            'info': 'Succeed',
            'text': translated_text
        }

        return request_success(response)

    else:
        return BAD_METHOD
    
def transaudio2chinese(audio):
        
    YOUDAO_URL = 'https://openapi.youdao.com/asrapi'
    APP_KEY = '337af8c31d798a2c'
    APP_SECRET = 't17A2QK4mt81JGWOEhWXjoPOeoU34oub'
    
    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size-10:size]

    def encrypt(signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()

    def do_request(data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(YOUDAO_URL, data=data, headers=headers)

    q = audio

    data = {}
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['signType'] = "v2"
    data['langType'] = 'zh-CHS'
    data['rate'] = 16000
    data['format'] = 'wav'
    data['channel'] = 1
    data['type'] = 1

    response = do_request(data)
    return response.content.decode('utf-8')["result"][0]

@CheckRequire
def message_transaudio(req: HttpRequest):

    if req.method == 'PUT':
        body = json.loads(req.body.decode('utf-8'))
        audio = body['audio']
            
        text = transaudio2chinese(audio)
        
        response = {
            'code': 0,
            'info': 'Succeed',
            'text': text
        }

        return request_success(response)

    else:
        return BAD_METHOD