from django.test import TestCase
import random
from Session.models import Session
from User.models import User

# Create your tests here.
class SessionTests(TestCase):
    
    # Initializer
    def setUp(self):
        # alice
        User.objects.create(name = 'swim17', password = 'abc1234567', 
                                    nickname = 'Alice', email = '17@swim.com')
        
        # bob
        User.objects.create(name = 'swim11', password = 'abc12345678', 
                                    nickname = 'Bob', email = '11@swim.com')
        
    # Utility Functions
    def get_image(self, user_id):
        return self.client.get(f'/session/image/{user_id}')
    
    def put_image(self, user_id):
        return self.client.put(f'/session/image/{user_id}')
    
    def get_message(self, user_id):
        return self.client.get(f'/session/message/{user_id}', content_type='application/json')
    
    def put_chatroom(self, user_id, session_name):
        payload = {
            'userId': user_id,
            'sessionName': session_name
        }
        return self.client.put('/session/chatroom', data=payload, content_type='application/json')

    def post_chatroom(self, user_id, session_name, session_id):
        payload = {
            'userId': user_id,
            'sessionName': session_name,
            'sessionId': session_id
        }
        return self.client.post('/session/chatroom', data=payload, content_type='application/json')
    
    def delete_chatroom(self, user_id, session_id):
        payload = {
            'userId': user_id,
            'sessionId': session_id
        }
        return self.client.delete('/session/chatroom', data=payload, content_type='application/json')

    def put_chatroom_admin(self, user_id, session_id, applicant_id):
        payload = {
            'userId': user_id,
            'sessionId': session_id,
            'applicantId': applicant_id
        }
        return self.client.put('/session/chatroom/Admin', data=payload, content_type='application/json')
    
    # Now start testcases

    # get head portrait
    def test_get_portrait(self):

        random.seed(1)

    # upload head portrait
    def test_upload_portrait(seld):

        random.seed(2)

    # create chatroom
    def test_put_chatroom(self):

        random.seed(5)
        alice = User.objects.filter(name='swim17').first()
        res = self.put_chatroom(alice.user_id, 'chatroom')

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    # create chatroom for unexisted user
    def test_put_chatroom_user_unexisted(self):

        random.seed(6)
        res = self.put_chatroom('abaaba', 'chatroom')

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'User Not Existed')

    # add user to a specific chatroom
    def test_post_chatroom(self):

        random.seed(7)
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        bob = User.objects.filter(name='swim11').first()
        res = self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    # add user to a specific chatroom with unexisted user
    def test_post_chatroom_user_unexisted(self):

        random.seed(8)
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        res = self.post_chatroom(10086, chatroom.name, chatroom.session_id)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User Not Existed')

    # add user to a specific chatroom with unexisted session
    def test_post_chatroom_session_unexisted(self):

        random.seed(9)
        alice = User.objects.filter(name='swim17').first()
        res = self.post_chatroom(alice.user_id, 'abaababa', '100000')

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'Session Not Existed')

    # quit from a chatroom
    def test_delete_chatroom(self):

        random.seed(10)
        # Alice create chatroom
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        # Bob join chatroom
        bob = User.objects.filter(name='swim11').first()
        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        # Bob quit from the chatroom
        res = self.delete_chatroom(bob.user_id, chatroom.session_id)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    # quit from a chatroom with unexisted user
    def test_delete_chatroom_user_unexisted(self):

        random.seed(11)
        # Alice create chatroom
        alice = User.objects.filter(name='swim17').first()
        self.put_chatroom(alice.user_id, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        res = self.delete_chatroom('abaaba', chatroom.session_id)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User Not Existed')

    # quit from a chatroom with unexisted session
    def test_delete_chatroom_session_unexisted(self):

        random.seed(12)
        bob = User.objects.filter(name='swim11').first()
        res = self.delete_chatroom(bob.user_id, 100000)

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'Session Not Existed')

    # agree application for joining chatroom
    def test_put_chatroom_admin(self):

        random.seed(13)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.user_id, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(alice.user_id, chatroom.session_id, bob.user_id)

        self.assertEqual(res.json()['code'], 0)
        self.assertEqual(res.json()['info'], 'Succeed')

    # agree application for joining chatroom with Not-Admin
    def test_put_chatroom_admin_not_admin(self):

        random.seed(14)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.name, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(bob.user_id, chatroom.session_id, bob.user_id)

        self.assertEqual(res.json()['code'], 1)
        self.assertEqual(res.json()['info'], 'User Not Existed or Permission Denied')

    # agree application for joining chatroom with unexisted session
    def test_put_chatroom_admin_session_unexisted(self):

        random.seed(15)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.name, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(alice.user_id, 1000000, bob.user_id)

        self.assertEqual(res.json()['code'], 2)
        self.assertEqual(res.json()['info'], 'Session Not Existed')

    # agree application for joining chatroom with unexisted applicant
    def test_put_chatroom_admin_applicant_unexisted(self):

        random.seed(16)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.name, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        res = self.put_chatroom_admin(alice.user_id, chatroom.session_id, 'abaaba')

        self.assertEqual(res.json()['code'], 3)
        self.assertEqual(res.json()['info'], 'Applicant Not Existed')

    # agree application for joining chatroom with applicant already in session
    def test_put_chatroom_admin_applicant_in_session(self):

        random.seed(17)
        alice = User.objects.filter(name='swim17').first()
        bob = User.objects.filter(name='swim11').first()
        self.put_chatroom(alice.user_id, 'chatroom')
        chatroom = Session.objects.filter(name='chatroom').first()

        self.post_chatroom(bob.user_id, chatroom.name, chatroom.session_id)

        self.put_chatroom_admin(alice.user_id, chatroom.session_id, bob.user_id)
        res = self.put_chatroom_admin(alice.user_id, chatroom.session_id, bob.user_id)

        self.assertEqual(res.json()['code'], 4)
        self.assertEqual(res.json()['info'], 'Already In Session')