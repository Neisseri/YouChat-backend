import random
from django.test import TestCase, Client
from User.models import User, UserGroup, Contacts, FriendRequests, TokenPair
import json
from django.http import HttpResponse, HttpRequest

# Create your tests here.
class UserTests(TestCase):
    
    # Initializer
    def setUp(self):
        alice = User.objects.create(name = "swim", password = "abc1234567", 
                                    nickname = "Alice", email = "17@swim.com")
        
        bob = User.objects.create(name = "swim2", password = "abc12345678", 
                                    nickname = "Bob", email = "11@swim.com")

    # Utility Functions
    def put_user(self, user_name, password, nickname, email):
        payload = {
            "userName": user_name,
            "password": password,
            "nickname": nickname,
            "email": email
        }
        return self.client.put("/people/user", data=payload, content_type="application/json")

    def post_user(self, user_name, password):
        payload = {
            "userName": user_name,
            "password": password
        }
        return self.client.post("/people/user", data=payload, content_type="application/json")
    
    def delete_user(self, user_name, password):
        payload = {
            "userName": user_name,
            "password": password
        }
        return self.client.delete("/people/user", data=payload, content_type="application/json")
    
    def post_modify(self, user_name, password):
        payload = {
            "userName": user_name,
            "password": password
        }
        return self.client.post("/people/modify", data=payload, content_type="application/json")
    
    def put_modify(self, code, new):
        payload = {
            "code": code,
            "new": new
        }
        return self.client.put("people/modify", data=payload, content_type="application/json")
    
    def get_friends(self, query):
        return self.client.get(f"people/friends/{query}")
    
    def put_friends(self, id, group):
        payload = {
            "id": id,
            "group": group
        }
        return self.client.put(f"people/friends", data=payload, content_type="application/json")
    
    def get_profile(self, id):
        return self.client.get(f"people/profile/{id}")
    
    def get_email_send(self, email):
        return self.client.get(f"people/send/{email}")
    
    def get_email_verify(self, veri_code):
        return self.client.get(f"people/verify/{veri_code}")
    
    # Now start testcases.

    # user register
    def test_add_user(self):

        random.seed(1)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            nn_len = random.randint(1, 10)
            em_len = random.randint(3, 40)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
            email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            res = self.put_user(user_name, password, nickname, email)
            
            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Succeed")
            self.assertEqual(res.status_code, 200)
            self.assertTrue(User.objects.filter(name=user_name).exists())

    # `userName` key missing
    def test_add_user_without_username(self):

        random.seed(2)
        pw_len = random.randint(5, 20)
        nn_len = random.randint(1, 10)
        em_len = random.randint(3, 40)
        password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
        nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
        email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
        res = self.put_user(None, password, nickname, email)
            
        self.assertNotEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"code": 2, "info": "Missing or error type of userName"})
        self.assertFalse(User.objects.filter(password=password).exists())
    
    # `password` key length incorrect
    def test_add_user_password_length_incorrect(self):
        
        random.seed(3)
        un_len = random.randint(5, 20)
        nn_len = random.randint(1, 10)
        em_len = random.randint(3, 40)
        user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
        password = ''
        nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
        email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
        res = self.put_user(user_name, password, nickname, email)

        self.assertNotEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"code": 2, "info": "Bad length of password"})
        self.assertFalse(User.objects.filter(name=user_name).exists())

    # `nickname` key with invalid char
    def test_add_user_nickname_invalid_char(self):

        random.seed(4)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            nn_len = random.randint(1, 10)
            em_len = random.randint(3, 40)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            nickname = ''.join([random.choice("?><@#$%^&") for _ in range(nn_len)])
            email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            res = self.put_user(user_name, password, nickname, email)

            self.assertNotEqual(res.status_code, 200)
            self.assertJSONEqual(res.content, {"code": 2, "info": "Invalid char in nickname"})
            self.assertFalse(User.objects.filter(name=user_name).exists())

    # `userName` key points to existing user
    def test_add_user_username_exists(self):
        
        random.seed(5)
        un_len = random.randint(5, 20)
        pw_len = random.randint(5, 20)
        nn_len = random.randint(1, 10)
        em_len = random.randint(3, 40)
        user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
        password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
        nickname = ''.join([random.choice("?><@#$%^&") for _ in range(nn_len)])
        email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
        self.put_user(user_name, password, nickname, email)

        password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
        nickname = ''.join([random.choice("?><@#$%^&") for _ in range(nn_len)])
        email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
        res = self.put_user(user_name, password, nickname, email)

        self.assertNotEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {"code": 8, "info": "User exists"})

    # user login
    def test_user_login(self):

        random.seed(6)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            nn_len = random.randint(1, 10)
            em_len = random.randint(3, 40)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
            email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            self.put_user(user_name, password, nickname, email)
            
            res = self.post_user(user_name, password)

            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Succeed")
            self.assertEqual(res.status_code, 200)

    # user delete
    def test_user_delete(self):

        random.seed(6)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            nn_len = random.randint(1, 10)
            em_len = random.randint(3, 40)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
            email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            self.put_user(user_name, password, nickname, email)
            
            res = self.delete_user(user_name, password)

            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Success Deleted")
            self.assertEqual(res.status_code, 200)

    # user delete with incorrect password
    def test_user_delete_with_incorrect_password(self):

        random.seed(6)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            nn_len = random.randint(1, 10)
            em_len = random.randint(3, 40)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
            email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            self.put_user(user_name, password, nickname, email)
            
            res = self.delete_user(user_name, "aaaaaaaaaa")

            self.assertEqual(res.json()['code'], 2)
            self.assertEqual(res.json()['info'], "Wrong Password")
            self.assertEqual(res.status_code, 400)

    # user delete without corresponding user
    def test_user_delete_user_not_existed(self):

        random.seed(6)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])

            res = self.delete_user(user_name, password)

            self.assertEqual(res.json()['code'], 2)
            self.assertEqual(res.json()['info'], "User Not Found")
            self.assertEqual(res.status_code, 400)
