from django.db import models
from utils import utils_time
from User.models import User

from constants.session import MAX_CHAR_LENGTH
from constants.session import MAX_MESSAGE_LENGTH

# Create your models here.

class Session(models.Model):
    session_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    isTop = models.BooleanField()
    isMute = models.BooleanField()

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
    
class UserAndSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    permission = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    
    class Meta:
        indexes = [models.Index(fields=["user"]), models.Index(fields=["session"])]
        unique_together = ("user", "session")

class Message(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    text = models.CharField(max_length=MAX_MESSAGE_LENGTH, unique=True)
    time = models.FloatField(default=utils_time.get_timestamp)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField()


    class Meta:
        indexes = [models.Index(fields=["time"])]

    def __str__(self) -> str:
        return self.text