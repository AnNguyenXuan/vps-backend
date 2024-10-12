from tortoise import fields
from tortoise.models import Model

class Order(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='orders')
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2)
    status = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class OrderDetail(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField('models.Order', related_name='order_details')
    product = fields.ForeignKeyField('models.Product', related_name='order_details')
    quantity = fields.IntField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
