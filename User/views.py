import json
import random
from django.http import HttpRequest, HttpResponse
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from User.models import User, Contacts, FriendRequests, UserGroup, TokenPair
from utils.utils_time import get_timestamp


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
    assert 3 <= len(email) <= 20, "Bad length of [email]"

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
def friends(req: HttpRequest):
    
    if req.method == "GET":
        token = req.GET.get("token")
        if not token:
            return request_failed(2, "Bad Token", status_code=400)
        token_pair = TokenPair.objects.filter(token=token).first()
        user = token_pair.user
        contact_list = Contacts.objects.filter(user=user)
        for contact in contact_list:
            contact.friend.serialize()
        return_data = {
            "friendList": {
                "default": [
                return_field(contact.friend.serialize(), ["userId", "nickname"]) 
            for contact in contact_list]},
        }
        return request_success(return_data)
        
    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        token = body['token']
        if not token:
            return request_failed(2, "Bad Token", status_code=400)
        token_pair = TokenPair.objects.filter(token=token).first()
        sendee = token_pair.user
        user_name = body["userName"]
        sender = User.objects.filter(name = user_name).first()
        request = FriendRequests.objects.filter(sender=sender, sendee=sendee).first()
        if not request:
            return request_failed(2, "[Some Message]", status_code=400)
        new_friend = Contacts(user=sender, friend=sendee, group = UserGroup.objects.get(user=sender, group_name = 'default'))
        new_friend_rev = Contacts(user=sendee, friend=sender, group = UserGroup.objects.get(user=sendee, group_name = 'default'))
        new_friend.save()
        new_friend_rev.save()
        request.delete()
        return request_success()
    
    elif req.method == "PUT":
        body = json.loads(req.body.decode("utf-8"))
        token = body['token']
        if not token:
            return request_failed(2, "Bad Token", status_code=400)
        token_pair = TokenPair.objects.filter(token=token).first()
        sender = token_pair.user
        user_name = body["userName"]
        sendee = User.objects.filter(name = user_name).first()
        friend_request = FriendRequests(sender=sender, sendee=sendee)
        friend_request.save()
        return request_success()
    
    elif req.method == "DELETE":
        token = req.COOKIES.get("token")
        token_pair = TokenPair.objects.filter(token=token).first()
        sender = token_pair.user
        user_name = body["userName"]
        sendee = User.objects.filter(name = user_name).first()
        Contacts.objects.get(user=sender, friend=sendee).delete()
        Contacts.objects.get(user=sendee, friend=sender).delete()
        return request_success()
                
    else:
        return BAD_METHOD

# /email/send view
def email_send(req: HttpRequest):

    body = json.loads(req.body.decode("utf-8"))

    if req.method == "GET":

        return request_success()
    
# email/verify view
def email_verify(req: HttpRequest):

    body = json.loads(req.body.decode("utf-8"))

    if req.method == "GET":

        return request_success()

