from tortoise.models import Model
from tortoise import fields


class Fight(Model):
    # Use the discord message ID for this
    recorded = fields.DatetimeField()
    victory = fields.BooleanField(default=False)
    participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField(
        'models.Team', related_name='fights', through='fight_team_participation'
    )


class Team(Model):
    server = fields.ForeignKeyField('models.Guild', related_name='teams')
    name = fields.CharField(max_length=20)
    fights: fields.ManyToManyRelation[Fight]
