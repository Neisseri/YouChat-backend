from django.middleware.csrf import get_token
from django.http import HttpRequest, HttpResponse
import json

# 获取csrftoken
def getToken(request: HttpRequest):
    token = get_token(request)
    return HttpResponse(json.dumps({'token': token}), content_type="application/json,charset=utf-8")
