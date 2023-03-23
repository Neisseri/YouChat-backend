import os
from django.core.mail import send_mail

os.environ['DJANGO_SETTINGS_MODULE'] = 'st_im_django.settings'

if __name__ == '__main__':   

    send_mail(
        '来自swimchat@sina.com的测试邮件',
        '欢迎访问您使用SwimChat',
        'swimchat@sina.com',
        ['neissertong@gmail.com'],
    )