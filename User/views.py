import json
from django.http import HttpRequest, HttpResponse
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from User.models import User, Contacts, FriendRequests
from utils.utils_time import get_timestamp

# Create your views here.

def friends(req: HttpRequest):
    if req.method == "GET":
        
        return request_success()
        
    
    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        return request_success()
        
        
    else:
        return request_success()

def user(req: HttpRequest):
    if req.method == "GET":
        
        return request_success()
        
    
    elif req.method == "POST":
        body = json.loads(req.body.decode("utf-8"))
        return request_success()
        
        
    else:
        return request_success()

