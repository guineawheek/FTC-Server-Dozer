"""A cog that handles keeping nicknames persistent between member join/leave, as a substitute for setting nicknames by teams."""
import discord
from discord.ext.commands import BadArgument, guild_only

from ._utils import *
from .. import db


class Nicknames(Cog):
    """Preserves nicknames upon member join/leave, similar to roles."""

    @command()
    @guild_only()
    async def savenick(self, ctx, save: bool = None):
        """Sets whether or not a user wants their nickname upon server leave to be saved upon server rejoin."""
        with db.Session() as session:
            nick = session.query(NicknameTable).filter_by(user_id=ctx.author.id, guild_id=ctx.guild.id).one_or_none()
            if nick is None:
                nick = NicknameTable(user_id=ctx.author.id, guild_id=ctx.guild.id, nickname=ctx.author.nick, enabled=save is None or save)
                session.add(nick)
            else:
                if save is not None:
                    nick.enabled = save
            await ctx.send(f"Nickname saving is {'enabled' if nick.enabled else 'disabled'}!")
    savenick.example_usage = """
    `{prefix}savenick False` - disables saving nicknames upon server leave.
    """

    async def on_member_join(self, member):
        """Handles adding the nickname back on server join."""
        with db.Session() as session:
            nick = session.query(NicknameTable).filter_by(user_id=member.id, guild_id=member.guild.id).one_or_none()
            if nick is None or not nick.enabled:
                return
            await member.edit(nick=nick.nickname)

    async def on_member_remove(self, member):
        """Handles saving the nickname on server leave."""
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
    """Maintains a record of saved nicknames for various users."""
    __tablename__ = "nicknames"
    user_id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String, nullable=True)
    enabled = db.Column(db.Boolean)


def setup(bot):
    """cog setup boilerplate"""
    bot.add_cog(Nicknames(bot))
