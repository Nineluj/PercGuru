from tortoise.models import Model
from tortoise import fields


class Fight(Model):
    # Use the discord message ID for this
    id = fields.IntField(pk=True)
    recorded = fields.DatetimeField()
    victory = fields.BooleanField(default=False)
    participants: fields.ManyToManyRelation["Player"] = fields.ManyToManyField(
        'models.Player', related_name='fights', through='fight_participant'
    )


class Team(Model):
    server = fields.ForeignKeyField('models.Guild', related_name='teams')
    id = fields.IntField(pk=True)
    name = fields.CharField(unique=True, max_length=20)
    members: fields.ReverseRelation["Player"]


class Player(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    guild = fields.ForeignKeyField('models.Team', related_name='members')
    fights: fields.ManyToManyRelation[Fight]


