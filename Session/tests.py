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