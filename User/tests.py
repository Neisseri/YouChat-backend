import random
from django.test import TestCase
from User.models import User

# Create your tests here.
class UserTests(TestCase):

    def setUp(self):
        User.objects.create(name = "swim", password = "abc1234567", nickname = "Alice", email = "17@swim.com")

    def post_user(self, name, password, nickname, email):
        payload = {
            "userName": name,
            "password": password,
            "nickname": nickname,
            "email": email
        }
        return self.client.post("/people/user", data=payload, content_type="application/json")

    def test_add_user(self):
        random.seed(1) 
        for _ in range(50):
            password = ''.join([random.choice("qwertyuiop12345678") for _ in range(20)])
            name = ''.join([random.choice("qwertyuiop12345678") for _ in range(20)])
            nickname = ''.join([random.choice("asdfghjkl12345678") for _ in range(20)])
            email = ''.join([random.choice("asdfghjkl12345678") for _ in range(20)])
            res = self.post_user(name, password, nickname, email)
            
            #test here
