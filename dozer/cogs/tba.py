"""A series of commands that talk to The Blue Alliance."""
import datetime
from datetime import timedelta
from pprint import pformat

import discord
from discord.ext.commands import BadArgument
import googlemaps
#import tbapi
import aiotba
from geopy.geocoders import Nominatim

from ._utils import *

blurple = discord.Color.blurple()


class TBA(Cog):
    """Commands that talk to The Blue Alliance"""
    def __init__(self, bot):
        super().__init__(bot)
        tba_config = bot.config['tba']
        self.gmaps_key = bot.config['gmaps_key']
        self.session = aiotba.TBASession(tba_config['key'], self.bot.http._session)
        #self.parser = tbapi.TBAParser(tba_config['key'], cache=False)

    @group(invoke_without_command=True)
    async def tba(self, ctx, team_num: int):
        """
        Get FRC-related information from The Blue Alliance.
        If no subcommand is specified, the `team` subcommand is inferred, and the argument is taken as a team number.
        """
        await self.team.callback(self, ctx, team_num)

    tba.example_usage = """
    `{prefix}tba 5052` - show information on team 5052, the RoboLobos
    """

    @tba.command()
    @bot_has_permissions(embed_links=True)
    async def team(self, ctx, team_num: int):
        """Get information on an FRC team by number."""
        try:
            team_data = await self.session.team(team_num)
            e = discord.Embed(color=blurple)
            e.set_author(name='FIRST® Robotics Competition Team {}'.format(team_num),
                         url='https://www.thebluealliance.com/team/{}'.format(team_num),
                         icon_url='https://frcavatars.herokuapp.com/get_image?team={}'.format(team_num))
            e.add_field(name='Name', value=team_data.nickname)
            e.add_field(name='Rookie Year', value=team_data.rookie_year)
            e.add_field(name='Location',
                        value='{0.city}, {0.state_prov} {0.postal_code}, {0.country}'.format(team_data))
            e.add_field(name='Website', value=team_data.website)
            e.add_field(name='TBA Link', value='https://www.thebluealliance.com/team/{}'.format(team_num))
            e.set_footer(text='Triggered by ' + ctx.author.display_name)
            await ctx.send(embed=e)
        except aiotba.http.AioTBAError:
            raise BadArgument("Couldn't find data for team {}".format(team_num))

    team.example_usage = """
    `{prefix}tba team 4131` - show information on team 4131, the Iron Patriots
    """

    @tba.command()
    @bot_has_permissions(embed_links=True)
    async def media(self, ctx, team_num: int, year: int=None):
        if year is None:
            year = datetime.datetime.today().year
        try:
            team_media = await self.session.team_media(team_num, year)
            if not team_media:
                await ctx.send(f"Unfortunately, there doesn't seem to be any media for team {team_num} in {year}...")
                return

            pages = []
            base = f"FRC Team {team_num} {year} Media: "
            for media in team_media:
                if media.type == "cdphotothread":
                    page = discord.Embed(title=base + "Chief Delphi",
                                         url=f"https://www.chiefdelphi.com/media/photos/{media.foreign_key}")
                    page.set_image(url=f"https://www.chiefdelphi.com/media/img/{media.details['image_partial']}")
                elif media.type == "imgur":
                    page = discord.Embed(title=base + "Imgur",
                                         url=f"https://imgur.com/{media.foreign_key}")
                    page.set_image(url=f"https://i.imgur.com/{media.foreign_key}.png")
                elif media.type == "instagram-image":
                    page = discord.Embed(title=base + "Instagram",
                                         url=f"https://www.instagram.com/p/{media.foreign_key}")
                    page.set_image(url=f"https://www.instagram.com/p/{media.foreign_key}/media")
                elif media.type == "youtube":
                    page = f"**{base} YouTube** \nhttps://youtu.be/{media.foreign_key}"
                elif media.type == "grabcad":
                    page = discord.Embed(title=base + "GrabCAD",
                                         url=f"https://grabcad.com/library/{media.foreign_key}")
                    page.set_image(url=media.details['model_image'])
                else:
                    continue
                pages.append(page)
            await paginate(ctx, pages)

        except aiotba.http.AioTBAError:
            raise BadArgument("Couldn't find data for team {}".format(team_num))
    @tba.command()
    async def raw(self, ctx, team_num: int):
        """
        Get raw TBA API output for a team.
        This command is really only useful for development.
        """
        try:
            team_data = await self.session.team(team_num)
            e = discord.Embed(color=blurple)
            e.set_author(name='FIRST® Robotics Competition Team {}'.format(team_num),
                         url='https://www.thebluealliance.com/team/{}'.format(team_num),
                         icon_url='https://frcavatars.herokuapp.com/get_image?team={}'.format(team_num))
            e.add_field(name='Raw Data', value=pformat(team_data.__dict__))
            e.set_footer(text='Triggered by ' + ctx.author.display_name)
            await ctx.send(embed=e)
        except aiotba.http.AioTBAError:
            raise BadArgument('Team {} does not exist.'.format(team_num))

    raw.example_usage = """
    `{prefix}tba raw 4150` - show raw information on team 4150, FRobotics
    """

    @command()
    async def timezone(self, ctx, team_num: int):
        """
        Get the timezone of a team based on the team number.
        """

        try:
            team_data = await self.session.team(team_num)
            location = '{0.city}, {0.state_prov} {0.country}'.format(team_data)
            gmaps = googlemaps.Client(key=self.gmaps_key)
            geolocator = Nominatim()
            geolocation = geolocator.geocode(location)
            timezone = gmaps.timezone(location="{}, {}".format(geolocation.latitude, geolocation.longitude),
                                      language="json")
            utc_offset = int(timezone["rawOffset"]) / 3600
            if timezone["dstOffset"] == 3600:
                utc_offset += 1
            utc_timedelta = timedelta(hours=utc_offset)
            currentUTCTime = datetime.datetime.utcnow()
            currentTime = currentUTCTime + utc_timedelta
            current_hour = currentTime.hour
            current_hour_original = current_hour
            dayTime = "AM"
            if current_hour > 12:
                current_hour -= 12
                dayTime = "PM"
            elif current_hour == 12:
                dayTime = "PM"
            elif current_hour == 0:
                current_hour = 12
                dayTime = "AM"
            current_minute = currentTime.minute
            if current_minute < 10:
                current_minute = "0{}".format(current_minute)
            current_second = currentTime.second
            if current_second < 10:
                current_second = "0{}".format(current_second)
            await ctx.send(
                "Timezone: {0} UTC{1:+g} \nCurrent Time: {2}:{3}:{4} {5} ({6}:{3}:{4})".format(
                    timezone["timeZoneName"], utc_offset, current_hour, current_minute, current_second, dayTime, current_hour_original))
        except aiotba.http.AioTBAError:
            raise BadArgument('Team {} does not exist.'.format(team_num))

    timezone.example_usage = """
    `{prefix}timezone 3572` - show the local time of team 3572, Wavelength
    """


def setup(bot):
    """Adds the TBA cog to the bot"""
    bot.add_cog(TBA(bot))
