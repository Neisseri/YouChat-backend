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