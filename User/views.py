import json
from django.http import HttpRequest, HttpResponse
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from User.models import User, Contacts, FriendRequests
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

# /user view
def user(req: HttpRequest):

    body = json.loads(req.body.decode("utf-8"))

    if req.method == "GET":
        user_name, password, nickname, email = check_for_user_data(body)
        
        return request_success()
        
    
    elif req.method == "POST":
        
        return request_success()

    elif req.method == "DELETE":

        return request_success()
        
    else:
        return request_success()

# /friends view
def friends(req: HttpRequest):
    if req.method == "GET":
        
        return request_success()
        
    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        return request_success()
                
    else:
        return request_success()

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

