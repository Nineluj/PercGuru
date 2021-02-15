from tortoise.models import Model
from tortoise import fields


class Guild(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(unique=True, max_length=20)
    react_message_channel_id = fields.IntField(null=True)
    react_message_id = fields.IntField(null=True)

    whitelisted_channels: fields.ReverseRelation["WhitelistedChannel"]


class WhitelistedChannel(Model):
    channel_id = fields.IntField()
    guild = fields.ForeignKeyField(model_name='models.Guild', related_name="whitelisted_channels")
