import requests

def translate(language, text):
    # data1 = { 'doctype': 'json', 'type': 'auto','i': '你吃饭了吗？' }
    data = { 'doctype': 'json', 'type': 'auto','i': text }
    r = requests.get("http://fanyi.youdao.com/translate", params=data)
    result = r.json()
    return result

if __name__ == '__main__':
    text = 'Did you eat?'
    print(translate('English', text))
