from django.db import models
from utils import utils_time

from constants.user import MAX_CHAR_LENGTH

# Create your models here.
    
class Friend(models.Model):
    friendList = []
    newFriendList = []

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    nickname = models.CharField(max_length=MAX_CHAR_LENGTH, unique=False)
    password = models.CharField(max_length=MAX_CHAR_LENGTH, unique= False)
    register_time = models.FloatField(default=utils_time.get_timestamp)
    login_time = models.FloatField(default=utils_time.get_timestamp)
    email = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    friend = Friend()

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
