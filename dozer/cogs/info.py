"""Provides commands for pulling certain information."""
import time
import re
import datetime
import resource

import discord
from discord.ext.commands import cooldown, BucketType, guild_only

from ._utils import *
from .. import db

blurple = discord.Color.blurple()
datetime_format = '%Y-%m-%d %I:%M %p'
startup_time = time.time()

try:
    with open("/etc/os-release") as f:
        os_name = re.findall(r'PRETTY_NAME=\"(.+?)\"', f.read())[0]
except Exception:
    os_name = "Windows probably"

class Info(Cog):
    """Commands for getting information about people and things on Discord."""

    def __init__(self, bot):
        super().__init__(bot)
        self.afk_map = {}

    @guild_only()
    @cooldown(1, 10, BucketType.channel)
    @command(aliases=['user', 'userinfo', 'memberinfo'])
    async def member(self, ctx, member: discord.Member = None):
        """
        Retrieve information about a member of the guild.
        If no arguments are passed, information about the author is used.
        **This command works without mentions.** Remove the '@' before your mention so you don't ping the person unnecessarily.
        You can pick a member by:
        - Username (`cooldude`)
        - Username and discriminator (`cooldude#1234`)
        - ID (`326749693969301506`)
        - Nickname - must be exact and is case-sensitive (`"Mr. Cool Dude III | Team 1234"`)
        - Mention (not recommended) (`@Mr Cool Dude III | Team 1234`)
        """
        async with ctx.typing():
            member = member or ctx.author
            icon_url = member.avatar_url_as(static_format='png')
            activity_name = member.activity.type.name.replace("listening", "listening to") if member.activity else None

            e = discord.Embed(color=member.color)
            e.set_thumbnail(url=icon_url)
            e.add_field(name='Name', value=str(member))
            e.add_field(name='ID', value=member.id)
            e.add_field(name='Nickname', value=member.nick, inline=member.nick is None)
            e.add_field(name='Bot Created' if member.bot else 'User Joined Discord',
                        value=member.created_at.strftime(datetime_format))
            e.add_field(name='Joined Guild', value=member.joined_at.strftime(datetime_format))
            e.add_field(name='Color', value=str(member.color).upper())

            e.add_field(name='Status and Game', value=f'{member.status}, '.title() + (
                f'{activity_name}' + f' {member.activity.name}' if member.activity else 'no game playing'), inline=False)
            roles = sorted(member.roles, reverse=True)[:-1]  # Remove @everyone
            e.add_field(name='Roles', value=', '.join(role.name for role in roles) or "No roles", inline=False)
            e.add_field(name='Icon URL', value=icon_url, inline=False)
        await ctx.send(embed=e)

    member.example_usage = """
    `{prefix}member` - get information about yourself
    `{prefix}member cooldude#1234` - get information about cooldude
    """

    @guild_only()
    @cooldown(1, 10, BucketType.channel)
    @command(aliases=['server', 'guildinfo', 'serverinfo'])
    async def guild(self, ctx):
        """Retrieve information about this guild."""
        guild = ctx.guild
        e = discord.Embed(color=blurple)
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name='Name', value=guild.name)
        e.add_field(name='ID', value=guild.id)
        e.add_field(name='Created at', value=guild.created_at.strftime(datetime_format))
        e.add_field(name='Owner', value=guild.owner)
        e.add_field(name='Members', value=guild.member_count)
        e.add_field(name='Channels', value=len(guild.channels))
        e.add_field(name='Roles', value=len(guild.role_hierarchy) - 1)  # Remove @everyone
        e.add_field(name='Emoji', value=len(guild.emojis))
        e.add_field(name='Region', value=guild.region.name)
        e.add_field(name='Icon URL', value=guild.icon_url or 'This guild has no icon.')
        await ctx.send(embed=e)

    guild.example_usage = """
    `{prefix}guild` - get information about this guild
    """

    @command()
    async def stats(self, ctx):
        info = await ctx.bot.application_info()

        #e = discord.Embed(title=info.name + " Stats", color=discord.Color.blue())
        frame = "\n".join(map(lambda x: f"{str(x[0]):<24}{str(x[1])}", { #e.add_field(name=x[0], value=x[1], inline=False), {
            "{:=^48}".format(f" Stats for {info.name} "): "",
            "Bot owner:": info.owner,
            "Users:": len(ctx.bot.users),
            "Channels:": len(list(ctx.bot.get_all_channels())),
            "Servers:": len(ctx.bot.guilds),
            "":"",
            f"{' Host stats ':=^48}": "",
            "Operating system:": os_name,
            "Process memory usage:": f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}K",
            "Process uptime": str(datetime.timedelta(seconds=round(time.time() - startup_time)))
        }.items()))
        await ctx.send(f"```\n{frame}\n```")#embed=e)


    @command()
    async def afk(self, ctx, *, reason : str = "Not specified"):
        """Set yourself to AFK so that if you are pinged, the bot can explain your absence."""
        if len(ctx.message.mentions):
            await ctx.send("Please don't mention anyone in your AFK message!")
            return

        afk_status = self.afk_map.get(ctx.author.id)
        if not afk_status is None:
            afk_status.reason = reason
        else:
            afk_status = AFKStatus(user_id=ctx.author.id, reason=reason)
            self.afk_map[ctx.author.id] = afk_status

        await ctx.send(embed=discord.Embed(description=f"**{ctx.author.name}** is AFK: **{reason}**"))
    afk.example_usage = """
    `{prefix}afk robot building` - set yourself to AFK for reason "reason"
    """

    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if message.content.strip().startswith(f"{ctx.prefix}afk"):
            return

        for member in message.mentions:
            if member.id in self.afk_map:
                await ctx.send(embed=discord.Embed(description=f"**{member.name}** is AFK: **{self.afk_map[member.id].reason}**"))

        afk_status = self.afk_map.get(ctx.author.id)
        if afk_status is not None:
            await ctx.send(f"**{ctx.author.name}** is no longer AFK!")
            del self.afk_map[ctx.author.id]

class AFKStatus(db.DatabaseObject):
    __tablename__ = "afk_status"
    user_id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String)

def setup(bot):
    """Adds the info cog to the bot"""
    bot.add_cog(Info(bot))
