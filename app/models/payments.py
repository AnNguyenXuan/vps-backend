from tortoise import fields
from tortoise.models import Model

class Payment(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField('models.Order', related_name='payments')
    payment_method = fields.CharField(max_length=50)
    payment_status = fields.CharField(max_length=50)
    paid_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    created_at = fields.DatetimeField(auto_now_add=True)
