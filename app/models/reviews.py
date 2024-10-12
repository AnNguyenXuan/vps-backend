from tortoise import fields
from tortoise.models import Model

class Review(Model):
    id = fields.IntField(pk=True)
    product = fields.ForeignKeyField('models.Product', related_name='reviews')
    user = fields.ForeignKeyField('models.User', related_name='reviews')
    rating = fields.IntField()
    comment = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
