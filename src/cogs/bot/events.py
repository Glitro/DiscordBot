#! /usr/bin/env python3
#|*****************************************************
# * Copyright         : Copyright (C) 2019
# * Author            : ddc
# * License           : GPL v3
# * Python            : 3.6
#|*****************************************************
# # -*- coding: utf-8 -*-

from src.sql.bot.bot_configs_sql import BotConfigsSql
from src.sql.bot.server_configs_sql import ServerConfigsSql
from src.sql.bot.servers_sql import ServersSql
from src.sql.bot.users_sql import UsersSql
from src.cogs.gw2.utils import gw2_utils as gw2Utils
from .utils import bot_utils as utils, constants, bot_utils_events as utilsEvents
from discord.ext import commands
import datetime
import discord
import os
################################################################################
################################################################################
###############################################################################
class Events(commands.Cog):
    """(Bot events)"""
    def __init__(self, bot):
        self.bot = bot
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_command(ctx):
            pass
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_guild_channel_create(channel):
            pass
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_guild_channel_delete(channel):
            pass
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_guild_channel_update(before, after):
            pass
################################################################################
################################################################################
###############################################################################
        @bot.event
        async def on_message(message:discord.Message):
            if len(message.content)==0:return
            ctx = await bot.get_context(message)
            #execute bot messages immediately
            if ctx.author.bot:
                await bot.process_commands(message)
                return
            
            if (isinstance(ctx.channel, discord.DMChannel)):
                await utilsEvents.execute_private_msg(self,ctx)
            else:
                await utilsEvents.execute_server_msg(self,ctx)
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_guild_join(guild:discord.Guild):
            await utilsEvents.insert_default_initial_configs(bot)
            botConfigsSql = BotConfigsSql(self.bot.log)
            configs = await botConfigsSql.get_bot_configs()
            prefix = configs[0]["prefix"]
            games_included = None
            
            if constants.games_included is not None:
                if len(constants.games_included) == 1:
                    games_included = f"{constants.games_included[0]}"
                elif len(constants.games_included) > 1:
                    games_included = ""
                    for games in constants.games_included:
                        games_included += f"({games}) "
            msg = f"Thanks for using *{self.bot.user.name}!*\n"\
                f"To learn more about this bot: `{prefix}about`\n"\
                f"Games included so far: `{games_included}`\n\n"
            
            for rol in guild.me.roles:
                if rol.permissions.value == 8:
                    msg += f"Bot is running in \"Admin\" mode\n"\
                           f"A \"bot-commands\" channel were created for bot commands\n"
            
            msg +=  f"If you are an Admin and wish to list configurations: `{prefix}config list`\n"\
                    f"To get a list of commands: `{prefix}help`"
            embed=discord.Embed(color=discord.Color.green(),description=msg)     
            embed.set_author(name=guild.me.display_name, icon_url=guild.me.avatar_url)
            channel_to_send_msg = await utils.channel_to_send_msg(bot, guild)
            if channel_to_send_msg is not None:
                try:
                    await channel_to_send_msg.send(embed=embed)
                except discord.HTTPException:
                    await channel_to_send_msg.send(msg)
            await utils.create_admin_commands_channel(self, guild)
################################################################################
################################################################################
################################################################################  
        @bot.event
        async def on_guild_remove(guild:discord.Guild):
            serversSql = ServersSql(self.bot.log)
            await serversSql.delete_server(guild.id)
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_member_join(member:discord.Member):
            usersSql = UsersSql(self.bot.log)
            serverConfigsSql = ServerConfigsSql(self.bot.log)
            await usersSql.insert_user(member)
            rs = await serverConfigsSql.get_server_configs(member.guild.id)
            if len(rs) > 0 and rs[0]["msg_on_join"] == "Y":
                now = datetime.datetime.now()
                embed=discord.Embed(color=discord.Color.green(), description=str(member))
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name="Joined the Server")
                embed.set_footer(text=f"{now.strftime('%c')}")
                channel_to_send_msg = await utils.channel_to_send_msg(bot, member.guild)
                if channel_to_send_msg is not None:
                    try:
                        await channel_to_send_msg.send(embed=embed)
                    except discord.HTTPException:
                        await channel_to_send_msg.send(f"{member.name} Joined the Server\n{now.strftime('%c')}")
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_member_remove(member:discord.Member):
            if bot.user.id == member.id: return
            usersSql = UsersSql(self.bot.log)
            serverConfigsSql = ServerConfigsSql(self.bot.log)
            await usersSql.delete_user(member)
            rs = await serverConfigsSql.get_server_configs(member.guild.id)
            if len(rs) > 0 and rs[0]["msg_on_leave"] == "Y":
                now = datetime.datetime.now()
                embed=discord.Embed(color=discord.Color.red(), description=str(member))
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name="Left the Server")
                embed.set_footer(text=f"{now.strftime('%c')}")
                channel_to_send_msg = await utils.channel_to_send_msg(bot, member.guild)
                if channel_to_send_msg is not None:
                    try:
                        await channel_to_send_msg.send(embed=embed)
                    except discord.HTTPException:
                        await channel_to_send_msg.send(f"{member.name} Left the Server\n{now.strftime('%c')}")
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_guild_update(before:discord.Guild, after:discord.Guild):
            serversSql = ServersSql(self.bot.log)
            serverConfigsSql = ServerConfigsSql(self.bot.log)
            await serversSql.update_server_changes(before, after)
            rs = await serverConfigsSql.get_server_configs(after.id)
            if len(rs) > 0 and rs[0]["msg_on_server_update"] == "Y":
                msg="New Server Settings:\n"
                now = datetime.datetime.now()
                color = utils.get_color_settings(constants.settings_filename, "EmbedColors", "EmbedColor")
                embed = discord.Embed(color=color,description="New Server Settings")
                embed.set_footer(text=f"{now.strftime('%c')}")
                
                if str(before.name) != str(after.name):
                    if before.name is not None:
                        embed.add_field(name="Previous Name", value=str(before.name))
                    embed.add_field(name="New Name", value=str(after.name))
                    msg+=f"New Name: `{after.name}`\n"
                    
                if str(before.region) != str(after.region):
                    before_flag = utils.get_region_flag(str(before.region))
                    after_flag = utils.get_region_flag(str(after.region))
                    if before.region is not None:
                        embed.add_field(name="Previous Region", value=before_flag+" "+str(before.region))
                    embed.add_field(name="New Region", value=f"{after_flag} {after.region}")
                    msg+=f"New Region: {after_flag} `{after.region}`\n"
                    
                if str(before.icon_url) != str(after.icon_url):
                    embed.set_thumbnail(url=after.icon_url)
                    embed.add_field(name="New Icon", value="-->", inline=True)
                    msg+=f"New Icon: \n{after.icon_url}\n"

                if str(before.owner_id) != str(after.owner_id):
                    embed.set_thumbnail(url=after.icon_url)
                    if before.owner_id is not None:
                        embed.add_field(name="Previous Server Owner", value=str(before.owner))                    
                    embed.add_field(name="New Server Owner", value=str(after.owner), inline=True)
                    msg+=f"New Server Owner: `{after.owner}`\n"
    
                if len(embed.fields) > 0:
                    channel_to_send_msg = await utils.channel_to_send_msg(bot, after)
                    if channel_to_send_msg is not None:
                        try:
                            await channel_to_send_msg.send(embed=embed)
                        except discord.HTTPException:
                            await channel_to_send_msg.send(msg)
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_member_update(before:discord.Guild, after:discord.Guild):
            if after.bot:
                return

            if before.activity != after.activity:
                if after.activity is not None and after.activity.type == discord.ActivityType.playing:
                    await gw2Utils.last_session_gw2_event_after(bot, after)
                elif before.activity is not None and before.activity.type == discord.ActivityType.playing:
                    await gw2Utils.last_session_gw2_event_before(bot, before)
            
            #do nothing if changed status
            if str(before.status) != str(after.status):
                return
            
            usersSql = UsersSql(self.bot.log)
            serverConfigsSql = ServerConfigsSql(self.bot.log)
            await usersSql.update_user_changes(before, after)
            rs_sc = await serverConfigsSql.get_server_configs(after.guild.id)
            if len(rs_sc) > 0 and rs_sc[0]["msg_on_member_update"] == "Y":
                msg="Profile Changes:\n\n"
                now = datetime.datetime.now()
                color = utils.get_color_settings(constants.settings_filename, "EmbedColors", "EmbedColor")
                embed = discord.Embed(color=color)
                embed.set_author(name=after.display_name, icon_url=after.avatar_url)
                embed.set_footer(text=f"{now.strftime('%c')}")

                if str(before.name) != str(after.name):
                    if before.name is not None:
                        embed.add_field(name="Previous Name", value=str(before.name))
                    embed.add_field(name="New Name", value=str(after.name))
                    msg+=f"New Name: `{after.name}`\n"
                                        
                if str(before.nick) != str(after.nick):
                    if before.nick is not None and after.nick is None:
                        embed.add_field(name="Previous Nickname", value=str(before.nick))                
                    elif before.nick is not None:
                        embed.add_field(name="Previous Nickname", value=str(before.nick))
                    embed.add_field(name="New Nickname", value=str(after.nick))
                    msg+=f"New Nickname: `{after.nick}`\n"
                    
                if str(before.avatar_url) != str(after.avatar_url):
                    embed.set_thumbnail(url=after.avatar_url)
                    embed.add_field(name="New Avatar", value="-->", inline=True)
                    msg+=f"New Avatar: \n{after.avatar_url}\n"
                
                if len(embed.fields) > 0:
                    channel_to_send_msg = await utils.channel_to_send_msg(bot, after.guild)
                    if channel_to_send_msg is not None:
                        try:
                            await channel_to_send_msg.send(embed=embed)
                        except discord.HTTPException:
                            await channel_to_send_msg.send(msg)
################################################################################
################################################################################
################################################################################
        @bot.event
        async def on_ready():
            now = datetime.datetime.now()
            dbname = await utils.get_full_dbname()
            await utilsEvents.insert_default_initial_configs(bot)
            await utilsEvents.set_bot_configs(bot, dbname, now)
            await utilsEvents.set_others_sql_configs(bot)
            await utilsEvents.run_bg_tasks(bot)
            utils.clear_screen()
            
            #executing all sql files inside dir data/sql
            if (utils.get_settings("ExecuteSqlFilesOnBoot", "ExecuteSqlFilesOnBoot").lower() == "yes"):
                await utils.execute_all_sql_files(self)

            bot_stats = utils.get_bot_stats(bot)
            servers = bot_stats["servers"]
            users = bot_stats["users"]
            channels = bot_stats["channels"]
            
            conn_msg = "====> Bot is online and connected to Discord <===="
            print(f"{constants.INTRO}")
            print("Python v{}.{}.{}".format(*os.sys.version_info[:3]))
            print(f"Discord API v{discord.__version__}")
            print(f"{dbname}")
            print("--------------------")
            print(f"{bot.user} (id:{bot.user.id})")
            print(f"Servers: {servers}")
            print(f"Users: {users}")
            print(f"Channels: {channels}")
            print("--------------------")
            print(f"{now.strftime('%c')}")
            bot.log.info(conn_msg)
################################################################################
################################################################################
################################################################################
def setup(bot):
    bot.add_cog(Events(bot))
    