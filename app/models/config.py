from tortoise.models import Model
from tortoise import fields


class Server(Model):
    name = fields.CharField(unique=True, max_length=20)


class WhitelistedChannel(Model):
    channel_id = fields.IntField(unique=True)
    server = fields.ForeignKeyField(model_name='models.Server')


class GuildReactMessage(Model):
    server = fields.ForeignKeyField(model_name="models.Server")
    message_id = fields.IntField(unique=True)
