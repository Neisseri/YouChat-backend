from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from utils.utils_require import CheckRequire, require
from constants.session import DEFAULT_MESSAGE_SCALE, BUILT_SESSION, FRIEDN_SESSION
from Session.models import Session, UserAndSession, Message
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
import time

# check if the char is a number or English letter
def check_number_letter(c: any):
    if ('0' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z'):
        return True
    else:
        return False

# extract the fields in request.body for /user GET
def check_for_session_data(body):

    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    session_name = require(body, "sessionName", "string", err_msg="Missing or error type of [sessionName]")
    session_id = require(body, "sessionId", "int", err_msg="Missing or error type of [sessionId]")
    message_scale = body["messageScale"] if "messageScale" in body.keys() else DEFAULT_MESSAGE_SCALE

    assert 5 <= len(user_name) <= 20, "Bad length of [userName]"
    assert 5 <= len(session_name) <= 20, "Bad length of [sessionName]"

    for i in range(0, len(user_name)):
        assert (check_number_letter(user_name[i]) or user_name[i] == '_'), "Invalid char in [userName]"
        
    for i in range(0, len(session_name)):
        assert (check_number_letter(user_name[i]) or user_name[i] == '_'), "Invalid char in [sessionName]"

    return user_name, session_name, session_id, message_scale

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
        
        manager_bond = UserAndSession.objects.filter(user = user, session = session).first()
        applicant_bond = UserAndSession.objects.filter(user = applicantUser, session = session).first()

        if not manager_bond or (manager_bond.permission != SESSION_HOST and manager_bond.permission != SESSION_MANAGER):
            return request_failed(1, "User Not Existed or Permission Denied", 400)

        if not applicant_bond:
            return request_failed(3, "Applicant Not Existed", 400)
        
        if applicant_bond.permission != SESSION_REQUEST:
            return request_failed(4, "Already In Session", 400)

        applicant_bond.permission = SESSION_MEMBER
        applicant_bond.save()

        return request_success()

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
            info["role"] = bond.permission

            members.append(info)

        session_name = session.name

        return request_success({"sessionName": session_name, "members": members})

    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))

        user_id = body["userId"]
        session_name = body["sessionName"]
        session_id = body["sessionId"]

        session = Session.objects.filter(name = session_name, session_id = session_id).first()
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
        
        sessions = []
        for bond in sessionsbond:
            sessions.append(bond.session)

        session_info = []
        for session in sessions:
            info = {}
            info["sessionId"] = session.session_id
            info["sessionName"] = session.name
            info["isTop"] = session.isTop
            info["isMute"] = session.isMute
            info["sessionType"] = session.type
            
            message = Message.objects.filter(session=session)
            if message:
                message = message.order_by("-time").first()
                info["timestamp"] = message.time
                info["type"] = message.type
                info["message"] = message.text
            else:
                info["timestamp"] = session.time
                info["type"] = "message"
                info["message"] = ""

            user_binds = UserAndSession.objects.filter(session = session)
            time_list = {}

            for user_bind in user_binds:
                user = user_bind.user
                user_name = user.name

                timestamp = user_bind.read_time

                time_list[user_name] = timestamp

            info["readTimeList"] = time_list

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

        bond = UserAndSession.objects.filter(user = user, session = session)

        bond.read_time = timestamp

        bond.save()

    else:
        return BAD_METHOD

def translate2chinese(language, text):

    youdao_url = 'https://openapi.youdao.com/api'   # 有道api地址

    # 需要翻译的文本'
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
        'from':"en",   # 源语言
        'to':"zh-CHS",   # 翻译语言
        'appKey':app_id,   # 应用id
        'salt':uu_id,   # 随机生产的uuid码
        'sign':sign,   # 签名
        'signType':"v3",   # 签名类型，固定值
        'curtime':time_curtime,   # 秒级时间戳
    }

    r = requests.get(youdao_url, params = data).json()   # 获取返回的json()内容
    return r["translation"][0]   # 获取翻译内容


@CheckRequire
def message_translate(req: HttpRequest):

    # https://www.deepl.com/zh/pro-api/

    if req.method == 'PUT':
        body = json.loads(req.body.decode('utf-8'))
        language = body['language']
        text = body['text']
            
        translated_text = translate2chinese(language, text)
        
        response = {
            'code': 0,
            'info': 'Succeed',
            'text': translated_text
        }

        return request_success(response)

    else:
        return BAD_METHOD