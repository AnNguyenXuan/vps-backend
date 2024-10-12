from tortoise import fields
from tortoise.models import Model

class users(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)


    def __str__(self):
        return self.username
