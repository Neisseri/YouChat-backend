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

# reference: https://blog.csdn.net/qq_25691777/article/details/120823770#1_3
'''
data = { 'doctype': 'json', 'type': 'auto','i': text }
r = requests.get("http://fanyi.youdao.com/translate", params=data)
response = r.json()
result = response['translateResult'][0][0]
tgt = result['tgt']
return tgt
'''

# reference: https://blog.csdn.net/whatday/article/details/106057309
url_youdao = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=' \
    'http://www.youdao.com/'
dict = {}
dict['type'] = 'AUTO'
dict['doctype'] = 'json'
dict['xmlVersion'] = '1.8'
dict['keyfrom'] = 'fanyi.web'
dict['ue'] = 'UTF-8'
dict['action'] = 'FY_BY_CLICKBUTTON'
dict['typoResult'] = 'true'
dict['i'] = 'xqy is stupid'
data = urllib.parse.urlencode(dict).encode('utf-8')
response = urllib.request.urlopen(url_youdao, data)
content = response.read().decode('utf-8')
data = json.loads(content)
result = data['translateResult'][0][0]['tgt']

print(result)