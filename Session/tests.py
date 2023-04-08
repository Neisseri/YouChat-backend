from django.test import TestCase
import random
from Session.models import Session, UserAndSession, Message
from User.models import User

# Create your tests here.
class SessionTests(TestCase):
    
    # Initializer
    def setUp(self):
        alice = User.objects.create(name = "swim17", password = "abc1234567", 
                                    nickname = "Alice", email = "17@swim.com")
        
        bob = User.objects.create(name = "swim11", password = "abc12345678", 
                                    nickname = "Bob", email = "11@swim.com")
        
    # Utility Functions
    def get_image(self, user_id):
        return self.client.get(f"/session/image/{user_id}", content_type="application/json")
    
    def put_image(self, user_id):
        return self.client.put(f"/session/image/{user_id}", content_type="application/json")
    
    def get_message(self, user_id):
        return self.client.get(f"session/message/{user_id}", content_type="application/json")
    
    def put_chatroom(self, user_name, session_name):
        payload = {
            "userName": user_name,
            "sessionName": session_name
        }
        return self.client.put("session/chatroom", data=payload, content_type="application/json")

    def post_chatroom(self, user_name, session_name, session_id):
        payload = {
            "userName": user_name,
            "sessionName": session_name,
            "sessionId": session_id
        }
        return self.client.post("session/chatroom", data=payload, content_type="application/json")
    
    def delete_chatroom(self, user_name, session_id):
        payload = {
            "userName": user_name,
            "sessionId": session_id
        }
        return self.client.delete("session/chatroom", data=payload, content_type="application/json")

    def put_chatroom_admin(self, user_name, session_id, applicant_name):
        payload = {
            "userName": user_name,
            "sessionId": session_id,
            "applicantName": applicant_name
        }
        return self.client.post("session/chatroom/Admin", data=payload, content_type="application/json")
    
    # Now start testcases

    # get head portrait
    def test_get_portrait(self):

        random.seed(1)

    # upload head portrait
    def test_upload_portrait(seld):

        random.seed(2)

    # fetch messages for sidbar rendering
    def test_get_messages(self):

        random.seed(3)
        alice = User.objects.filter(name="swim17").first()
        res = self.get_message(alice.user_id)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], "Succeed")
                           