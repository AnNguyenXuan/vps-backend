from tortoise import fields
from tortoise.models import Model

class Shipment(Model):
    id = fields.IntField(pk=True)
    order = fields.ForeignKeyField('models.Order', related_name='shipments')
    shipment_status = fields.CharField(max_length=50)
    carrier = fields.CharField(max_length=50)
    tracking_number = fields.CharField(max_length=100, null=True)
    shipped_at = fields.DatetimeField(null=True)
    delivered_at = fields.DatetimeField(null=True)
