# Extra features compared to upstream

### Extra commands:
```
%afk - set an AFK message to respond with if pinged
%stats - display bot and host stats
%clearreactions - clear reactions on a message either in the current channel or a specified one
%bulkclearreactiosn - clear reactions on the last X messages in a channel
%slowmode - set the slowmode message delay for a channel
%rolecolor - display or change the color of a role by hexcodes (handy on mobile)

%tba eventsfor - display events for a team in a given year
%tba media - display a carousel of team media for a given year
%tba awards - display the awards for a team for a given year
%weather - display the current weather for an FRC or FTC team

%starboard - commands to configure a starboard/hall of fame
```

### FTC Server Dozer specific commands:
```
%voicekick - remove a member from voicechat. Mostly useful if they will not be able to rejoin.
%mkteamrole - used to create new colored team roles on the FTC server
%forceundeafen - forcefully undeafens a user, a relic of when deafens were not reliable on Dozer.
%vote - adds thumbsup/thumbsdown reactions to the message. Typically used in the fashion of `%vote yes or no`
%sleep - DMs people to tell them they must go to bed.
```

### Backend changes:
 * Switched to `uvloop` for asyncio event loops for supposedly increased performance.
 * Fixed some bugs in Dozer here and there, and made certain code style edits.
 * Team associations auto-setting nicknames upon server entry has been disabled. Instead, 
 the `nicknames` cog saves and restores nicknames on server leave/reentry, similar to how roles
 are restored. This functionality can be disabled on a per-user basis with `%savenick False`.
 * `%timezone` was partially rewritten to use `strftime`, and can be configured to not use the 
 Google Maps API (which now requires a credit card)
 * `%timezone` has its arguments changed slightly to support FTC teams as well. The command's 
 arguments are now `%timezone <program> <teamnumber>`
 
 * `%tba` uses `aiotba`, a properly asynchronous TBA library
 * `%tba` and `%toa` embeds have been tweaked to have the title be a link
 * `%tba` also include the district (if any) and home championship of teams.
 
 * `%toa` can be configured not to query TOA but instead query a mirror of FIRST registration data
 * `%toa` can display the registration data of FTC teams per year. This can be useful for recalling
 the past names of teams who change them on a yearly basis. For example, `%toa 7486 2015` and 
 `%toa 7486 2016` yield different results. 
 * `%toa` when displaying past registration entries will display a registered motto, if present.
 * Output from the `discord` logger is included in logged output. Loglevels can also be specified in
  the config file.
 
