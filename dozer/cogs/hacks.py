# pylint: skip-file
from discord.ext.commands import has_permissions, bot_has_permissions, BucketType, cooldown
from .. import db
from ._utils import *
import discord
import random

# as the name implies, this cog is hilariously hacky code.
# it's very ftc server specific code, made specifically for its own needs.
# i stuck it in git for maintenance purposes.
# this should be deleted from the plowie tree if found.

FTC_DISCORD_ID = 225450307654647808
VERIFY_CHANNEL_ID = 333612583409942530
JOINED_LOGS_ID = 350482751335432202
class Hacks(Cog):

    async def on_member_join(self, member):
        if member.guild.id == FTC_DISCORD_ID:
            await member.send("""Welcome to the FTC Discord! Please read through #server-rules-info for information on how to access the rest of the server!""")
        logs = self.bot.get_channel(JOINED_LOGS_ID)
        res = f"```New user {member} ({member.id})\nInvite summary:\n"
        for i in await member.guild.invites():
            res += f"{i.code}, {i.uses}\n"
        res += "```"
        await logs.send(res)

                
    async def on_message(self, message):
        member = message.author
        if message.channel.id == VERIFY_CHANNEL_ID and message.content.lower().startswith("i have read the rules and regulations"):
            await member.add_roles(discord.utils.get(message.guild.roles, name="Member"))
            await member.send("""Thank you for reading the rules and regulations. We would like to welcome you to the FIRST® Tech Challenge Discord Server! Please follow the server rules and have fun! Don't hesitate to ping a member of the moderation team if you have any questions! 

_Please set your nickname with `%nick NAME - TEAM#` in #bot-spam to reflect your team number, or your role in FIRST Robotics if you are not affiliated with a team. If you are not a part of or affiliated directly with a FIRST® Tech Challenge team or the program itself, please contact an administrator for further details._""")
            await member.edit(nick=(message.author.display_name[:20] + " | SET TEAM#"))
            return
        if message.guild and message.guild.id == FTC_DISCORD_ID and "🐢" in message.content and message.author.id != self.bot.user.id:
            pass
            #await message.add_reaction("🐢")
            #await message.delete()

    async def on_message_edit(self, before, after):
        message = after
        if message.guild and message.guild.id == FTC_DISCORD_ID and "🐢" in message.content and message.author.id != self.bot.user.id:
            pass
            #await message.add_reaction("🐢")
            #await message.delete()
    
    async def clear_reactions(self, reaction):
        async for user in reaction.users():
            await reaction.message.remove_reaction(reaction, user)
    
    async def on_reaction_add(self, reaction, user):
        #return
        message = reaction.message
        if message.guild and message.guild.id == FTC_DISCORD_ID and reaction.emoji == "🐢":
            await self.clear_reactions(reaction)
        #if message.guild and message.guild.id == FTC_DISCORD_ID and message.content.lower().startswith("no u") and message.author.id != self.bot.user.id:
        #    await message.channel.send("no u")

    
    @has_permissions(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @command()
    async def mkteamrole(self, ctx, team: int, team_name: str, color: discord.Color):
        # find the first team in the descending list that has a larger number than you
        # create a new role in that position+1
        with ctx.typing():
            pos = -1
            for role in sorted(ctx.guild.roles, key=lambda role: role.position, reverse=True):
                print(role.name)
                if role.name == "mkteamrole Stop Role":
                    pos = role.position + 1
                    break
                try:
                    role_team = int(role.name.split(" ", 1)[0])
                    print(role_team)
                    if role_team > team:
                        pos = role.position + 1
                        break
                except ValueError:
                    pass
            new_role = await ctx.guild.create_role(name=f"{team} {team_name}", color=color, reason="%mkteamrole")
            await new_role.edit(position=pos)
            embed = discord.Embed(title="Created role!", description=f"Created role for team **{team} {team_name}** with color **{hex(color.value)}**!", color=color)
            members = ", ".join([i.mention for i in ctx.message.mentions]) or "No initial members"
            embed.add_field(name="Members added to role:", value=members)
            for m in ctx.message.mentions:
                await m.add_roles(new_role)
            
            await ctx.send(embed=embed)

    
    @has_permissions(administrator=True)#move_members=True)
    @bot_has_permissions(manage_channels=True)#, move_members=True)
    @command()
    async def voicekick(self, ctx, member: discord.Member, reason="No reason provided"):
        async with ctx.typing():
            if not member.voice.channel:
                await ctx.send("User is not in a voice channel!")
                return
            vc = await ctx.guild.create_voice_channel("_dozer_voicekick", reason=reason)
            await member.move_to(vc, reason=reason)
            await vc.delete(reason=reason)
            await ctx.send(f"{member} has been kicked from voice chat.")
    
    @has_permissions(manage_roles=True)
    @bot_has_permissions(manage_roles=True)
    @command()
    async def forceundeafen(self, ctx, member: discord.Member):
        with ctx.typing():
            await ctx.bot.cogs["Moderation"].permoverride(user=member, read_messages=None)
        await ctx.send("Overwrote perms for {member}")
        #ctx.bot.cogs["Moderation"].permoverride(user=member
    @has_permissions(add_reactions=True)
    @bot_has_permissions(add_reactions=True)
    @command()
    async def vote(self, ctx):
        await ctx.message.add_reaction('👍')
        await ctx.message.add_reaction('👎')

    
    @cooldown(1, 60, BucketType.user)
    @bot_has_permissions(embed_links=True)
    @command()
    async def sleep(self, ctx, member: discord.Member = None):
        IMG_URL = "https://i.imgur.com/ctzynlC.png"
        await ctx.send(IMG_URL)
        if member:
            await member.send("🛌 **GO TO SLEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEP** 🛌")
    

def setup(bot):
    bot.add_cog(Hacks(bot))
