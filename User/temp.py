import os
import sys
# sys.path.append("../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'st_im_django.settings' # 配置文件
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
django.setup()

from User.models import User

user1 = User.objects.filter(name='a').first()
if not user1:
    user1 = User(name='a')
    user1.save()
user2 = User.objects.filter(name='b').first()
if not user2:
    user2 = User(name='b')
    user2.save()
user1.friend_requests.add(user2)
print(user1.friend_requests.all())
print(user2.requests_received.first().sendee)
user2.requests_received.first().sendee.delete()

