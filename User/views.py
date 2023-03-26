import json
import random
from django.http import HttpRequest, HttpResponse
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from User.models import User, Contacts, FriendRequests, UserGroup, TokenPair
from utils.utils_time import get_timestamp
from django.urls import path, re_path
from django.core.mail import send_mail
import random

veri_code: int

# check if the char is a number or English letter
def check_number_letter(c: any):
    if ('0' <= c <= '9' or 'a' <= c <= 'z' or 'A' <= c <= 'Z'):
        return True
    else:
        return False

# extract the fields in request.body for /user GET
def check_for_user_data(body):

    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")
    nickname = require(body, "nickname", "string", err_msg="Missing or error type of [nickname]")
    email = require(body, "email", "string", err_msg="Missing or error type of [email]")

    assert 5 <= len(user_name) <= 20, "Bad length of [userName]"
    assert 5 <= len(password) <= 20, "Bad length of [password]"
    assert 1 <= len(nickname) <= 10, "Bad length of [nickname]"
    assert 3 <= len(email) <= 40, "Bad length of [email]"

    for i in range(0, len(user_name)):
        assert (check_number_letter(user_name[i]) or user_name[i] == '_'), "Invalid char in [userName]"
        
    for i in range(0, len(password)):
        assert (check_number_letter(password[i]) or password[i] == '_' or password[i] == '*'), "Invalid char in [password]"

    for i in range(0, len(nickname)):
        assert (check_number_letter(nickname[i]) or nickname[i] == '_' or nickname[i] == '*'), "Invalid char in [nickname]"

    for i in range(0, len(email)):
        assert (check_number_letter(email[i]) or email[i] == '.' or email[i] == '@'), "Invalid char in [email]"

    return user_name, password, nickname, email

def check_for_user_name_password(body):

    user_name = require(body, "userName", "string", err_msg="Missing or error type of [userName]")
    password = require(body, "password", "string", err_msg="Missing or error type of [password]")

    assert 5 <= len(user_name) <= 20, "Bad length of [userName]"
    assert 5 <= len(password) <= 20, "Bad length of [password]"

    for i in range(0, len(user_name)):
        assert (check_number_letter(user_name[i]) or user_name[i] == '_'), "Invalid char in [userName]"
        
    for i in range(0, len(password)):
        assert (check_number_letter(password[i]) or password[i] == '_' or password[i] == '*'), "Invalid char in [password]"

    return user_name, password


# /user view
@CheckRequire
def user(req: HttpRequest):

    body = json.loads(req.body.decode("utf-8"))

    if req.method == "POST":
        user_name, password= check_for_user_name_password(body)
        
        user = User.objects.filter(name=user_name).first()

        if not user:
            return request_failed(2, "User Not Found", status_code=400)

        if user.password != password:
            return request_failed(2, "Wrong Password", status_code=400)

        token = random.randint(0, 1000)
        tokenPair = TokenPair(user=user, token=token)
        tokenPair.save()

        return request_success({"token":token})
        
    
    elif req.method == "PUT":
        user_name, password, nickname, email = check_for_user_data(body)

        #find the user to check if exists.
        user = User.objects.filter(name=user_name).first()

        if not user:
            #create a new user
            user = User(name=user_name, password = password, nickname = nickname, email = email)
            user.save()
        else :
            return request_failed(8, "User exists", status_code=400)

        token = random.randint(0, 1000)
        tokenPair = TokenPair(user=user, token=token)
        tokenPair.save()

        return request_success({"token":token})

    elif req.method == "DELETE":
        user_name, password= check_for_user_name_password(body)
        
        user = User.objects.filter(name=user_name).first()

        if not user:
            return request_failed(2, "User Not Found", status_code=400)

        if user.password != password:
            return request_failed(2, "Wrong Password", status_code=400)

        user.delete()

        return request_failed(0, "Success Deleted", status_code=200)
        
    else:
        return request_success()

# /friends view
def friends(req: HttpRequest, query: any):
    
    if req.method == "GET":
        token = req.COOKIES.get("token")

        if not token:
            return request_failed(2, "Bad Token", status_code=400)
        
        user = TokenPair.objects.filter(token=token).first().user()

        query_list = User.objects.filter(Q(name_contains=query) | Q(nickname_contains=query) | Q(email_contains=query))

        contact_list = Contacts.objects.filter(user=user)

        request_list = Contacts.objects.filter(sendee=user)

        return_data = {
            "friendList": [
                {
                    "group": "Default", 
                    "list": []
                }
            ]
        }

        def where_is_group(group_name):
            
            for i in range(len(return_data["friendList"])):
                if return_data["friendList"][i]["group"] == group_name:
                    return i
            
            return -1

        for query_item in query_list:
            contact = contact_list.filter(friend=query_item).first()
            if contact:
                group_index = where_is_group(contact.group)
                
                if group_index != -1:   #already exists in friendList
                    return_data["friendList"][group_index]['list'].append(return_field(query_item.serialize(), ["id", "nickname"]))
                
                else:
                    return_data["friendList"].append(
                        {
                            "group": contact.group, 
                            "list": [return_field(query_item.serialize(), ["id", "nickname"])]
                        }
                    )
            else:
                request = request_list.filter(sender=query_item).first()
                if request:
                    group_index = where_is_group("Request")

                    if group_index != -1:   #already exists in friendList
                        return_data["friendList"][group_index]['list'].append(return_field(query_item.serialize(), ["id", "nickname"]))
                    
                    else:
                        return_data["friendList"].append(
                            {
                                "group": "Request", 
                                "list": [return_field(query_item.serialize(), ["id", "nickname"])]
                            }
                        )
                else:
                    group_index = where_is_group("Stranger")
                    
                    if group_index != -1:   #already exists in friendList
                        return_data["friendList"][group_index]['list'].append(return_field(query_item.serialize(), ["id", "nickname"]))
                    
                    else:
                        return_data["friendList"].append(
                            {
                                "group": "Stranger", 
                                "list": [return_field(query_item.serialize(), ["id", "nickname"])]
                            }
                        )

        return request_success(return_data)

    elif req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))

        token = req.COOKIES.get('token')
        
        if not token:
            return request_failed(2, "Bad Token", status_code=400)
        
        user = TokenPair.objects.filter(token=token).first().user()
        target = User.objects.filter(user_id=body['id'])

        if (body['group'] != 'Request' and body['group'] != 'Stranger'):

            request = FriendRequests.objects.filter(sendee=user, sender=target).first()
            
            if request:
                group = UserGroup.objects.filter(user=target, group_name = 'Default')
                group_rev = UserGroup.objects.filter(user=user, group_name = body['group'])

                if not group:
                    user_group = UserGroup(user=target, group_name = 'Default')
                    user_group.save()

                if not group_rev:
                    user_group = UserGroup(user=user, group_name = body['group'])
                    user_group.save()

                new_friend = Contacts(user=target, friend=user, group = UserGroup.objects.get(user=target, group_name = 'Default'))
                new_friend_rev = Contacts(user=user, friend=target, group = UserGroup.objects.get(user=user, group_name = body['group']))
                
                new_friend.save()
                new_friend_rev.save()
                
                request.delete()
            
            else:
                contact = Contacts.objects.filter(user=user, friend=target).first()

                if contact:
                    contact.group = body['group']
                    contact.save()
                
                else:
                    return request_failed(2, "Haven't requested", status_code=400)

        if (body['group'] == 'Request'):
            friend_request = FriendRequests.objects.filter(sender=user, sendee=target).first()
            if friend_request:
                friend_request.delete()

            friend_request = FriendRequests(sender=user, sendee=target)
            friend_request.save()

        if (body['group'] == 'Stranger'):
            contact = Contacts.objects.filter(user=user, friend=target).first()
            if not contact:
                return request_failed(2, "not have thist friend", status_code=400)

            Contacts.objects.get(user=user, friend=target).delete()
            Contacts.objects.get(user=target, friend=user).delete()

        return request_success()

    else:
        return BAD_METHOD


def generate_veri_code():
    # 6 digit verification code
    veri_code = ""
    for i in range(6):
        veri_code += str(random.randint(0, 9))
    return veri_code


# /email/send view
def email_send(req: HttpRequest, email):

    if req.method == "GET":
        global veri_code
        veri_code = generate_veri_code()
        # declare veri_code as a global variable

        mail_num = send_mail(
            'YouChat验证码',
            '欢迎您使用YouChat, 您的验证码为: ' + veri_code,
            'swimchat@sina.com',
            [email],
        )
        
        if (mail_num == 1):
            return request_success()
        else:
            return request_failed(code=2, info="Email Not Existed or Sending Failure")
    
# email/verify view
def email_verify(req: HttpRequest, v_code):

    if req.method == "GET":

        global veri_code
        if int(v_code) == int(veri_code):

            token = random.randint(1, 1000)
            response = {
                "code": 0,
	            "info": "Login Success",
	            "token": token
            }
            return request_success(response)
        
        else:

            return request_failed(code=2, info="Login Failure")

def profile(req: HttpRequest, id: any):

    token = req.COOKIES.get('token')
        
    if not token:
        return request_failed(2, "Bad Token", status_code=400)
    
    user = TokenPair.objects.filter(token=token).first().user()
    target = User.objects.filter(user_id=id).first()

    return_data = {
            "profile": return_field(target.serialize(), ["id", "nickname", "username", "email"])
        }
    
    contact = Contacts.objects.filter(user=user, friend=target).first()
    if contact:
        return_data["profile"]['group'] = contact.group
    
    else:
        request = FriendRequests.objects.filter(sendee=user, sender=target).first()
        if request:
            return_data["profile"]['group'] = "Request"
            
        else:
            return_data["profile"]['group'] = "Stranger"
    
    return request_success(return_data)
