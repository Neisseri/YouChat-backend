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
    
    