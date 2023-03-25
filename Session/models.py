from django.db import models
from utils import utils_time

from constants.session import MAX_CHAR_LENGTH
from constants.session import MAX_MESSAGE_LENGTH

# Create your models here.

class Session(models.Model):
    session_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=MAX_CHAR_LENGTH, unique=False)

    class Meta:
        indexes = [models.Index(fields=["name"])]

    def __str__(self) -> str:
        return self.name
    
class Message(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    text = models.CharField(max_length=MAX_MESSAGE_LENGTH, unique=True)
    time = models.FloatField(default=utils_time.get_timestamp)

    class Meta:
        indexes = [models.Index(fields=["time"])]

    def __str__(self) -> str:
        return self.text