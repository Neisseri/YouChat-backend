import random
from django.test import TestCase
from User.models import User
import zmail
import time

# Create your tests here.
class UserTests(TestCase):
    
    # Initializer
    def setUp(self):
        alice = User.objects.create(name = "swim17", password = "abc1234567", 
                                    nickname = "Alice", email = "17@swim.com")
        
        bob = User.objects.create(name = "swim11", password = "abc12345678", 
                                    nickname = "Bob", email = "11@swim.com")

    # Utility Functions
    def put_user(self, user_name, password, nickname, email):
        if user_name:
            payload = {
                "userName": user_name,
                "password": password,
                "nickname": nickname,
                "email": email
            }
        else :
            payload = {
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
    
    def put_modify(self, user_name, code, new):
        payload = {
            "userName": user_name,
            "code": code,
            "new": new
        }
        return self.client.put("/people/modify", data=payload, content_type="application/json")
    
    def get_friends(self, query, token_value):
        self.client.cookies.load({"token": token_value})
        return self.client.get(f"/people/friends/{query}")
    
    def put_friends(self, id, group, token_value):
        self.client.cookies.load({"token": token_value})
        payload = {
            "id": id,
            "group": group
        }
        return self.client.put(f"/people/friends", data=payload, content_type="application/json")
    
    def get_profile(self, id):
        return self.client.get(f"/people/profile/{id}")
    
    def get_email_send(self, email):
        return self.client.get(f"/people/email/send/{email}")
    
    def get_email_verify(self, email, veri_code):
        payload = {
            "email" : email,
            "veri_code" : veri_code
        }
        return self.client.post(f"/people/email/verify", data=payload, content_type="application/json")

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
        self.assertJSONEqual(res.content, {"code": 2, "info": "Missing or error type of [userName]"})
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
        self.assertJSONEqual(res.content, {"code": 2, "info": "Bad length of [password]"})
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
            self.assertJSONEqual(res.content, {"code": 2, "info": "Invalid char in [nickname]"})
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
        nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
        email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
        self.put_user(user_name, password, nickname, email)

        password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
        nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
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
            res = self.put_user(user_name, password, nickname, email)
            
            self.assertEqual(res.json()['code'], 0)

            res = self.delete_user(user_name, password)

            self.assertEqual(res.json()['info'], "Success Deleted")
            self.assertEqual(res.json()['code'], 0)
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

    # user secondary login
    def test_user_secondary_login(self):

        random.seed(7)
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

            res = self.post_modify(user_name, password)

            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Succeed")
            self.assertEqual(res.status_code, 200)

    def test_put_modify(self):

        random.seed(7)
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

            login = self.post_user(user_name, password)

            token = login.json()["token"]
            self.client.cookies["token"] = str(token)

            # user name
            new_user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            res = self.put_modify(user_name, 1, new_user_name)
            
            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Succeed")

            # password
            new_password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            res = self.put_modify(user_name, 2, new_password)
            
            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Succeed")

            # email
            new_email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            res = self.put_modify(user_name, 4, new_email)
            
            self.assertEqual(res.json()['code'], 0)
            self.assertEqual(res.json()['info'], "Succeed")

    def test_get_friends(self):
        res = self.post_user('swim11', 'abc12345678')
        self.assertEqual(res.status_code, 200)
        bob_id = res.json()['id']
        res = self.post_user('swim17', 'abc1234567')
        self.assertEqual(res.status_code, 200)
        token = res.json()["token"]
        res = self.get_friends("Bob", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed", 
            "friendList": [
                {
                "group": "Stranger",
                "list": [
                        {
                            "id": bob_id,
                            "nickname": "Bob",
                        }
                    ]
		        },
            ]})
        
        res = self.get_friends("swim11", token)
        
    def test_request_accept_delete_friends(self):
        res = self.post_user('swim11', 'abc12345678')
        self.assertEqual(res.status_code, 200)
        bob_id = res.json()['id']

        res = self.post_user('swim17', 'abc1234567')
        self.assertEqual(res.status_code, 200)
        alice_id = res.json()['id']
        token = res.json()["token"]
        
        res = self.put_friends(bob_id, "RequestTo", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})

        res = self.get_friends("Bob", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed", 
            "friendList": [
                {
                "group": "RequestTo",
                "list": [
                        {
                            "id": bob_id,
                            "nickname": "Bob",
                        }
                    ]
		        },
            ]})
        
        res = self.post_user('swim11', 'abc12345678')
        self.assertEqual(res.status_code, 200)
        token = res.json()["token"]

        res = self.get_friends("Alice", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed", 
            "friendList": [
                {
                "group": "RequestFrom",
                "list": [
                        {
                            "id": alice_id,
                            "nickname": "Alice",
                        }
                    ]
		        },
            ]})

        res = self.put_friends(alice_id, "Default", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})

        res = self.get_friends("swim17", token)
        self.assertEqual(res.status_code, 200)

        res = self.put_friends(alice_id, "MyGroup", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})

        res = self.get_friends("swim17", token)
        self.assertEqual(res.status_code, 200)

        res = self.put_friends(alice_id, "Stranger", token)
        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})
        
        res = self.get_friends("swim17", token)
        self.assertEqual(res.status_code, 200)



    def test_email_send(self):
        
        em_len = random.randint(3, 40)
        email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
        self.get_email_send(email)
        
    def test_email_verify(self):
        email = 'swimchat@sina.com'
        res = self.get_email_send(email)

        self.assertJSONEqual(res.content, {"code": 0, "info": "Succeed"})

        server = zmail.server('swimchat@sina.com', '8fcf93c3471c7b2c')
        time.sleep(6)
        
        latest_mail = server.get_latest()
        content = latest_mail["content_text"]

        veri_code = "".join(list(filter(str.isdigit, list(content[0]))))

        self.get_email_verify(email, veri_code)

    def test_get_profile(self):

        random.seed(7)
        for _ in range(50):
            un_len = random.randint(5, 20)
            pw_len = random.randint(5, 20)
            nn_len = random.randint(1, 10)
            em_len = random.randint(3, 40)
            user_name = ''.join([random.choice("qwertyuiopDGRSCBSFGFDS12345678_") for _ in range(un_len)])
            password = ''.join([random.choice("qwertyuiopDFSBERFB123456789_*") for _ in range(pw_len)])
            nickname = ''.join([random.choice("asdfghFDSCjkl12345678_*") for _ in range(nn_len)])
            email = ''.join([random.choice("asdfghFDSCjkl12345678.@") for _ in range(em_len)])
            sign_up = self.put_user(user_name, password, nickname, email)
            id = sign_up.json()["id"]

            login = self.post_user(user_name, password)

            token = login.json()["token"]
            self.client.cookies["token"] = str(token)

            self.get_profile(id)