import discord
from discord.ext.commands import BadArgument, guild_only

from ._utils import *
from .. import db

class Nicknames(Cog):
    @command()
    @guild_only()
    async def savenick(self, ctx, save: bool = None):
        with db.Session() as session:
            nick = session.query(NicknameTable).filter_by(user_id=ctx.author.id, guild_id=ctx.guild.id).one_or_none()
            if nick is None:
                nick = NicknameTable(user_id=ctx.author.id, guild_id=ctx.guild.id, nickname=ctx.author.nick, enabled=save is None or save)
                session.add(nick)
            else:
                if save is not None:
                    nick.enabled = save
            await ctx.send(f"Nickname saving is {'enabled' if nick.enabled else 'disabled'}!")

    async def on_member_join(self, member):
        with db.Session() as session:
            nick = session.query(NicknameTable).filter_by(user_id=member.id, guild_id=member.guild.id).one_or_none()
            if nick is None or not nick.enabled:
                return
            await member.edit(nick=nick.nickname)

    async def on_member_remove(self, member):
        with db.Session() as session:
            nick = session.query(NicknameTable).filter_by(user_id=member.id, guild_id=member.guild.id).one_or_none()
            if nick is None:
                nick = NicknameTable(user_id=member.id, guild_id=member.guild.id, nickname=member.nick, enabled=True)
                session.add(nick)
            else:
                if not nick.enabled:
                    return
                nick.nickname = member.nick


class NicknameTable(db.DatabaseObject):
    __tablename__ = "nicknames"
    user_id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String, nullable=True)
    enabled = db.Column(db.Boolean)

def setup(bot):
    bot.add_cog(Nicknames(bot))