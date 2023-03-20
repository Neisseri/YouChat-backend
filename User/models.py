from django.db import models
from utils import utils_time

from constants.user import MAX_CHAR_LENGTH

# Create your models here.

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    nickname = models.CharField(max_length=MAX_CHAR_LENGTH, unique=False)
    password = models.CharField(max_length=MAX_CHAR_LENGTH, unique= False)
    register_time = models.FloatField(default=utils_time.get_timestamp)
    login_time = models.FloatField(default=utils_time.get_timestamp)
    email = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    friends = models.ManyToManyField('self',  through='Contacts')
    friend_requests = models.ManyToManyField('self',  through='FriendRequests', symmetrical=False)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
    
class Group(models.Model):
    group_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    members = models.ManyToManyField(User, through='Membership')

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
    
class Contacts(models.Model):
    user = models.ForeignKey(User, related_name='friend_backward', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend', on_delete=models.CASCADE)
    update_time = models.FloatField(default=utils_time.get_timestamp)

    class Meta:
        unique_together = ['user', 'friend']

    def __str__(self) -> str:
        return f'{self.user} and {self.friend} are friends'

class FriendRequests(models.Model):
    sendee = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    update_time = models.FloatField(default=utils_time.get_timestamp)

    class Meta:
        unique_together = ['sender', 'sendee']

    def __str__(self) -> str:
        return f'{self.sender} sent a request to {self.sendee}'
    
class Membership(models.Model):
    group = models.ForeignKey(Group, related_name = 'groups', on_delete=models.CASCADE)
    member = models.ForeignKey(User, related_name = 'members', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.member} belongs to {self.group}'

