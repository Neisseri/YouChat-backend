from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from utils.utils_require import CheckRequire, require
from constants.session import DEFAULT_MESSAGE_SCALE
from Session.models import Session, UserAndSession, Message
from constants.session import SESSION_HOST, SESSION_MANAGER, SESSION_MEMBER, SESSION_REQUEST
from User.models import User
from utils.utils_request import request_failed, request_success, return_field
import json

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

    user_name = req.GET.get("userName")
    session_id = req.GET.get("sessionId")
    body = json.loads(req.body.decode("utf-8"))

    if req.method == "PUT":
        user_name = body["userName"]
        session_id = body["sessionId"]
        session = Session.objects.filter(session_id = session_id).first()
        user = User.objects.filter(name = user_name).first()

        if not session:
            return request_failed(2, "Session Not Existed", 400)
        
        if not user:
            return request_failed(1, "User Not Existed or Permission Denied", 400)
        
        applicantName = body["applicantName"]
        applicantUser = User.objects.filter(name = applicantName).first()

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
        return request_success()

@CheckRequire
def join_chatroom(req: HttpRequest):

    body = json.loads(req.body.decode("utf-8"))
    user_name = req.GET.get("userName")

    if req.method == "POST":
        user_name = body["userName"]
        session_name = body["sessionName"]
        session_id = body["sessionId"]

        session = Session.objects.filter(name = session_name, session_id = session_id).first()
        user = User.objects.filter(name = user_name).first()

        if not user:
            return request_failed(1, "User Not Existed", 400)
        
        if not session:
            return request_failed(2, "Session Not Existed", 400)
        
        bond = UserAndSession(permission = SESSION_REQUEST, user = user, session = session)
        bond.save()
        
        return request_success()
    
    elif req.method == "PUT":
        user_name = body["userName"]
        user = User.objects.filter(name = user_name).first()

        if not user:
            return request_failed(2, "User Not Existed", 400)

        session_name = body["sessionName"]
        session = Session(name = session_name, host = user)
        session.save()
        bond = UserAndSession(permission = SESSION_HOST, user = user, session = session)
        bond.save()

        return request_success()

    elif req.method == "DELETE":
        session_id = req.GET.get("sessionId")
        session = Session.objects.filter(session_id = session_id).first()
        user = User.objects.filter(name = user_name).first()

        if not user:
            return request_failed(1, "User Not Existed", 400)
        
        if not session:
            return request_failed(2, "Session Not Existed", 400)
        
        UserAndSession.objects.get(session = session, user = user).delete()
        
        return request_success()

    else:
        return request_success()
