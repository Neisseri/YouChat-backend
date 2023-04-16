import requests

# reference: https://blog.csdn.net/qq_25691777/article/details/120823770#1_3
def translate(language, text):
    # data1 = { 'doctype': 'json', 'type': 'auto','i': '你吃饭了吗？' }
    data = { 'doctype': 'json', 'type': 'auto','i': text }
    r = requests.get("http://fanyi.youdao.com/translate", params=data)
    response = r.json()
    result = response['translateResult'][0][0]
    tgt = result['tgt']
    return tgt

if __name__ == '__main__':
    text = 'Did you eat?'
    print(translate('English', text))
