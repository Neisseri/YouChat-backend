import requests

def translate(language, text):
    data1 = { 'doctype': 'json', 'type': 'auto','i': '你吃饭了吗？' }
    data2 = { 'doctype': 'json', 'type': 'auto','i': 'Did you eat?' }
    r = requests.get("http://fanyi.youdao.com/translate",params=data1)
    result = r.json()
    print(result)
    r = requests.get("http://fanyi.youdao.com/translate",params=data2)
    result = r.json()
    print(result)
