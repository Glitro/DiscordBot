#! /usr/bin/env python3
# |*****************************************************
# * Copyright         : Copyright (C) 2019
# * Author            : ddc
# * License           : GPL v3
# * Python            : 3.6
# |*****************************************************
# # -*- coding: utf-8 -*-

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from .utils.checks import Checks
from .utils import bot_utils as BotUtils
from .utils import chat_formatting as Formatting
from src.sql.bot.blacklists_sql import BlacklistsSql
from src.sql.bot.mutes_sql import MutesSql
from src.sql.bot.commands_sql import CommandsSql
from src.sql.bot.server_configs_sql import ServerConfigsSql
from src.cogs.bot.utils.cooldowns import CoolDowns


class Admin(commands.Cog):
    """(Admin commands)"""

    def __init__(self, bot):
        self.bot = bot

    ################################################################################
    @commands.command()
    @Checks.check_is_admin()
    @commands.cooldown(1, CoolDowns.AdminCooldown.value, BucketType.user)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """(Kick member from the server)
        
        Example:
        kick member#1234
        kick member#1234 reason
        """

        if member.id == self.bot.owner.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot Owner cannot be kicked.")
            return
        if member.id == self.bot.user.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot itself cannot be kicked.")
            return
        if member.id == ctx.message.author.id:
            await BotUtils.send_error_msg(self, ctx, "You cannot kick yourself.")
            return
        if BotUtils.is_server_owner(ctx, member):
            await BotUtils.send_error_msg(self, ctx, "You cannot kick the Server's Owner.")
            return
        if BotUtils.is_member_admin(member):
            await BotUtils.send_error_msg(self, ctx, "You cannot kick a Server's Admin.")
            return

        try:
            await ctx.guild.kick(member, reason=reason)
        except discord.Forbidden:
            await BotUtils.send_error_msg(self, ctx, "You do not have the proper permissions to kick.")
            return
        except discord.HTTPException:
            await BotUtils.send_error_msg(self, ctx, "Kicking failed.")
            return

        # await BotUtils.delete_last_channel_message(self, ctx)
        kick_author = str(ctx.author)
        try:  # private msg
            private_msg = "You have been KICKED"
            embed_private = discord.Embed(color=discord.Color.red(), description=private_msg)
            embed_private.add_field(name="Server", value=Formatting.inline(ctx.guild), inline=True)
            embed_private.add_field(name="Admin", value=Formatting.inline(kick_author), inline=True)
            if reason is not None:
                embed_private.add_field(name="Reason", value=Formatting.inline(reason), inline=True)
            await member.send(embed=embed_private)
        except discord.HTTPException:
            pass

        kick_author = BotUtils.get_member_name_by_id(self, ctx, ctx.author.id)
        # channel msg
        if member.nick is not None:
            mem_name = BotUtils.get_member_name_by_id(self, ctx, member.id)
            kicked_member = f"{member}\n({mem_name})"
        else:
            kicked_member = str(member)
        channel_msg = "Has been KICKED from the server"
        embed_channel = discord.Embed(color=discord.Color.red(), description=channel_msg)
        embed_channel.add_field(name="Member", value=Formatting.inline(kicked_member), inline=True)
        embed_channel.add_field(name="Admin", value=Formatting.inline(kick_author), inline=True)
        if reason is not None:
            embed_channel.add_field(name="Reason", value=Formatting.inline(reason), inline=True)

        msg_channel = f"{channel_msg}: {kicked_member}"
        await BotUtils.send_embed(self, ctx, embed_channel, False, msg_channel)

    ###############################################################################
    @commands.command()
    @Checks.check_is_admin()
    @commands.cooldown(1, CoolDowns.AdminCooldown.value, BucketType.user)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """(Ban member from the server)

        Example:
        ban member#1234
        ban member#1234 reason
        """

        if member.id == self.bot.owner.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot Owner cannot be banned.")
            return
        if member.id == self.bot.user.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot itself cannot be banned.")
            return
        if member.id == ctx.message.author.id:
            await BotUtils.send_error_msg(self, ctx, "You cannot ban yourself.")
            return
        if BotUtils.is_server_owner(ctx, member):
            await BotUtils.send_error_msg(self, ctx, "You cannot ban the Server's Owner.")
            return
        if BotUtils.is_member_admin(member):
            await BotUtils.send_error_msg(self, ctx, "You cannot ban a Server's Admin.")
            return

        try:
            await ctx.guild.ban(member, reason=reason, delete_message_days=7)
        except discord.Forbidden:
            await BotUtils.send_error_msg(self, ctx, "You do not have the proper permissions to ban.")
            return
        except discord.HTTPException:
            await BotUtils.send_error_msg(self, ctx, "Banning failed")
            return

        # await BotUtils.delete_last_channel_message(self, ctx)
        ban_author = str(ctx.author)
        try:  # private msg
            private_msg = "You have been BANNED"
            embed_private = discord.Embed(color=discord.Color.red(), description=private_msg)
            embed_private.add_field(name="Server", value=Formatting.inline(ctx.guild), inline=True)
            embed_private.add_field(name="Admin", value=Formatting.inline(ban_author), inline=True)
            if reason is not None:
                embed_private.add_field(name="Reason", value=Formatting.inline(reason), inline=True)
            await member.send(embed=embed_private)
        except discord.HTTPException:
            pass

        ban_author = BotUtils.get_member_name_by_id(self, ctx, ctx.author.id)
        # channel msg
        if member.nick is not None:
            mem_name = BotUtils.get_member_name_by_id(self, ctx, member.id)
            banned_member = f"{member}\n({mem_name})"
        else:
            banned_member = str(member)
        channel_msg = "Has been BANNED from the server"
        embed_channel = discord.Embed(color=discord.Color.red(), description=channel_msg)
        embed_channel.add_field(name="Member", value=Formatting.inline(banned_member), inline=True)
        embed_channel.add_field(name="Admin", value=Formatting.inline(ban_author), inline=True)
        if reason is not None:
            embed_channel.add_field(name="Reason", value=Formatting.inline(reason), inline=True)

        msg_channel = f"{channel_msg}: {banned_member}"
        await BotUtils.send_embed(self, ctx, embed_channel, False, msg_channel)

    ###############################################################################
    @commands.command()
    @Checks.check_is_admin()
    @commands.cooldown(1, CoolDowns.AdminCooldown.value, BucketType.user)
    async def unban(self, ctx, *, user: discord.User):
        """(Unban user from the server)

        Example:
        unban member#1234
        """

        banned_list = await ctx.guild.bans()
        if len(banned_list) > 0:
            for banned_user in banned_list:
                if banned_user.user == user:
                    color = self.bot.settings["EmbedColor"]
                    await ctx.guild.unban(banned_user.user)
                    await BotUtils.send_msg(self, ctx, color, f"User `{user}` is no longer banned.")
                else:
                    await BotUtils.send_error_msg(self, ctx, f"User: `{user}` not found.\n"
                                                          "Please use full user name with numbers: user#1234\n"
                                                          f"Display all banned users: `{ctx.prefix}banlist`")
        else:
            await BotUtils.send_error_msg(self, ctx, "There are no banned users in this server.")

    ###############################################################################
    @commands.command()
    @Checks.check_is_admin()
    @commands.cooldown(1, CoolDowns.AdminCooldown.value, BucketType.user)
    async def banlist(self, ctx):
        """(List all members that have been banned from the server)
        
        Example:
        banlist
        """

        position = 1
        bl_members = []
        bl_reason = []
        banned_list = await ctx.guild.bans()
        if len(banned_list) > 0:
            for banned_user in banned_list:
                bl_members.append(str(position) + ") " + str(banned_user.user))
                bl_reason.append(str(banned_user.reason))
                position += 1

            members = '\n'.join(bl_members)
            reason = '\n'.join(bl_reason)

            color = self.bot.settings["EmbedColor"]
            embed = discord.Embed(color=color)
            embed.set_author(name="All banned members:\n\n")
            embed.add_field(name="Member", value=Formatting.inline(members), inline=True)
            embed.add_field(name="Reason", value=Formatting.inline(f"({reason})"), inline=True)

            await BotUtils.send_embed(self, ctx, embed, False)
        else:
            await BotUtils.send_info_msg(self, ctx, "No banned users in this server.")

    ################################################################################
    @commands.group(aliases=["bl"])
    @Checks.check_is_admin()
    async def blacklist(self, ctx):
        """(Add, remove, list users from the blacklist)

        Blacklisted users cannot use any bot commands. 

        blacklist or bl

        Example:
        blacklist add member#1234
        blacklist remove member#1234
        blacklist list
        """

        if ctx.invoked_subcommand is None:
            if ctx.command is not None:
                cmd = ctx.command
            else:
                cmd = self.bot.get_command("blacklist")

            await BotUtils.send_help_msg(self, ctx, cmd)
            return

        ctx.invoked_subcommand

    ################################################################################
    @blacklist.command(name="add")
    @commands.cooldown(1, CoolDowns.BlacklistCooldown.value, BucketType.user)
    async def blacklist_add(self, ctx, member: discord.Member, *, reason=None):
        """(Add user to blacklist)

        Example:
        blacklist add member#1234 reason
        """

        if member.id == self.bot.owner.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot Owner cannot be blacklisted.")
            return
        if member.id == self.bot.user.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot itself cannot be blacklisted.")
            return
        if member.id == ctx.message.author.id:
            await BotUtils.send_error_msg(self, ctx, "You cannot blacklist yourself.")
            return
        if BotUtils.is_server_owner(ctx, member):
            await BotUtils.send_error_msg(self, ctx, "You cannot blacklist the Server's Owner.")
            return

        serverConfigsSql = ServerConfigsSql(self.bot)
        rs = await serverConfigsSql.get_server_configs(ctx.guild.id)
        if BotUtils.is_member_admin(member) and rs[0]["blacklist_admins"] == 'N':
            await BotUtils.send_error_msg(self, ctx, "You cannot blacklist a Server's Admin.")
            return

        if reason is not None and len(reason) > 29:
            await BotUtils.send_error_msg(self, ctx, "Reason has too many characters.")
            return

        blacklistsSql = BlacklistsSql(self.bot)
        rs = await blacklistsSql.get_server_blacklisted_user(member)
        if len(rs) == 0:
            await blacklistsSql.insert_blacklisted_user(member, ctx.message.author, reason)
            msg = f"Successfully added {member} to the blacklist.\n" \
                  "Cannot execute any Bot commands anymore."
            if reason is not None:
                msg += f"\nReason: {reason}"
            color = self.bot.settings["EmbedColor"]
            await BotUtils.send_msg(self, ctx, color, Formatting.inline(msg))
        else:
            msg = f"{member} is already blacklisted."
            if rs[0]["reason"] is not None:
                msg += f"\nReason: {reason}"
            await BotUtils.send_error_msg(self, ctx, msg)

    #################################################################################
    @blacklist.command(name="remove")
    @commands.cooldown(1, CoolDowns.BlacklistCooldown.value, BucketType.user)
    async def blacklist_remove_user(self, ctx, *, member: discord.Member):
        """(Remove blacklisted user)
         
        Example:
        blacklist remove member#1234
        """

        if member is not None:
            blacklistsSql = BlacklistsSql(self.bot)
            rs = await blacklistsSql.get_server_blacklisted_user(member)
            if len(rs) > 0:
                await blacklistsSql.delete_blacklisted_user(member)
                msg = f"Successfully removed {member} from the blacklist."
                color = self.bot.settings["EmbedColor"]
                await BotUtils.send_msg(self, ctx, color, Formatting.inline(msg))
                await ctx.send(f"{member.mention}")
            else:
                msg = f"{member} is not blacklisted."
                await BotUtils.send_error_msg(self, ctx, msg)
        else:
            msg = f"Member {member} not found"
            await BotUtils.send_error_msg(self, ctx, msg)

    #################################################################################
    @blacklist.command(name="removeall")
    @commands.cooldown(1, CoolDowns.BlacklistCooldown.value, BucketType.user)
    async def blacklist_remove_all_users(self, ctx):
        """(Remove all blacklisted users)
         
        Example:
        blacklist removeall
        """

        blacklistsSql = BlacklistsSql(self.bot)
        rs = await blacklistsSql.get_all_server_blacklisted_users(ctx.guild.id)
        if len(rs) > 0:
            color = self.bot.settings["EmbedColor"]
            await blacklistsSql.delete_all_blacklisted_users(ctx.guild.id)
            await BotUtils.send_msg(self, ctx, color, "Successfully removed all members from the blacklist.")
        else:
            await BotUtils.send_error_msg(self, ctx, "There are no blacklisted members in this server.")

    #################################################################################
    @blacklist.command(name="list")
    @commands.cooldown(1, CoolDowns.BlacklistCooldown.value, BucketType.user)
    async def blacklist_list(self, ctx):
        """(List all blacklisted users)
         
        Example:
        blacklist list
        """

        bl_members = []
        bl_reason = []
        bl_author = []
        position = 1

        blacklistsSql = BlacklistsSql(self.bot)
        rs = await blacklistsSql.get_all_server_blacklisted_users(ctx.guild.id)
        if len(rs) > 0:
            for key, value in rs.items():
                member_name = f"{ctx.guild.get_member(value['discord_user_id'])}"
                author_name = BotUtils.get_member_name_by_id(self, ctx, value["discord_author_id"])
                bl_author.append(author_name)
                bl_members.append(f"{position}) {member_name}")
                if value["reason"] is None:
                    bl_reason.append("---")
                else:
                    bl_reason.append(value["reason"])
                position += 1

            members = '\n'.join(bl_members)
            reason = '\n'.join(bl_reason)
            author = '\n'.join(bl_author)

            embed = discord.Embed(description="*`Members that cannot execute any bot commands`*",
                                  color=discord.Color.red())
            embed.set_footer(text=f"For more info: {ctx.prefix}help blacklist")
            embed.set_author(name="Blalcklisted members in this server:\n\n", icon_url=f"{ctx.guild.icon_url}")
            embed.add_field(name="Member", value=Formatting.inline(members), inline=True)
            embed.add_field(name="Added by", value=Formatting.inline(author), inline=True)
            embed.add_field(name="Reason", value=Formatting.inline(reason), inline=True)

            await BotUtils.send_embed(self, ctx, embed, False)
        else:
            await BotUtils.send_error_msg(self, ctx, "There are no blacklisted members in this server.")

    ################################################################################
    @commands.group()
    @Checks.check_is_admin()
    async def mute(self, ctx):
        """(Add, remove, list mute users)

        Muted members cannot type anything.
        They will be noticed with a direct message from bot.

        mute

        Example:
        mute add member#1234 reason
        mute remove member#1234
        mute list
        """

        if ctx.invoked_subcommand is None:
            if ctx.command is not None:
                cmd = ctx.command
            else:
                cmd = self.bot.get_command("mute")

            await BotUtils.send_help_msg(self, ctx, cmd)
            return

        # check if bot has perms (manage messages)
        if ctx.message.guild.me.guild_permissions.manage_messages:
            ctx.invoked_subcommand
        else:
            msg = "Bot does not have permission to delete messages.\n" \
                  "Missing permission: \"Manage Messages\"`"
            embed = discord.Embed(title="", color=discord.Color.red(), description=msg)
            try:
                await ctx.channel.send(embed=embed)
            except discord.HTTPException:
                await ctx.channel.send(f"{msg}")
            return

    ################################################################################
    @mute.command(name="add")
    @commands.cooldown(1, CoolDowns.MuteCooldown.value, BucketType.user)
    async def mute_add(self, ctx, member: discord.Member, *, reason=None):
        """(Mute an user)

        Example:
        mute add member#1234 reason
        """

        if member.id == self.bot.owner.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot Owner cannot be muted.")
            return
        if member.id == self.bot.user.id:
            await BotUtils.send_error_msg(self, ctx, "The Bot itself cannot be muted.")
            return
        if member.id == ctx.message.author.id:
            await BotUtils.send_error_msg(self, ctx, "You cannot mute yourself.")
            return
        if BotUtils.is_server_owner(ctx, member):
            await BotUtils.send_error_msg(self, ctx, "You cannot mute the Server's Owner.")
            return

        serverConfigsSql = ServerConfigsSql(self.bot)
        rs = await serverConfigsSql.get_server_configs(ctx.guild.id)
        if BotUtils.is_member_admin(member) and rs[0]["mute_admins"] == 'N':
            await BotUtils.send_error_msg(self, ctx, "You cannot mute a Server's Admin.")
            return

        if reason is not None and len(reason) > 29:
            await BotUtils.send_error_msg(self, ctx, "Reason has too many characters.")
            return

        mutesSql = MutesSql(self.bot)
        rs = await mutesSql.get_server_mute_user(member)
        if len(rs) == 0:
            await mutesSql.insert_mute_user(member, ctx.message.author, reason)
            msg = f"Successfully muted {member}"
            color = self.bot.settings["EmbedColor"]
            if reason is not None:
                msg += f"\nReason: {reason}"
            await BotUtils.send_msg(self, ctx, color, Formatting.inline(msg))
        else:
            msg = f"{member} is already muted."
            if rs[0]["reason"] is not None:
                msg += f"\nReason: {reason}"
            await BotUtils.send_error_msg(self, ctx, msg)

    #################################################################################
    @mute.command(name="remove")
    @commands.cooldown(1, CoolDowns.MuteCooldown.value, BucketType.user)
    async def mute_remove_user(self, ctx, *, member: discord.Member):
        """(Remove muted user)
         
        Example:
        mute remove member#1234
        """

        if member is not None:
            mutesSql = MutesSql(self.bot)
            rs = await mutesSql.get_server_mute_user(member)
            if len(rs) > 0:
                msg = f"Successfully unmuted {member}."
                color = self.bot.settings["EmbedColor"]
                await mutesSql.delete_mute_user(member)
                await BotUtils.send_msg(self, ctx, color, Formatting.inline(msg))
                await ctx.send(f"{member.mention}")
            else:
                msg = f"{member} is not muted."
                await BotUtils.send_error_msg(self, ctx, msg)
        else:
            msg = f"Member {member} not found"
            await BotUtils.send_error_msg(self, ctx, msg)

    #################################################################################
    @mute.command(name="removeall")
    @commands.cooldown(1, CoolDowns.MuteCooldown.value, BucketType.user)
    async def mute_remove_all_users(self, ctx):
        """(Remove all muted users)
         
        Example:
        mute removeall
        """

        mutesSql = MutesSql(self.bot)
        rs = await mutesSql.get_all_server_mute_users(ctx.guild.id)
        if len(rs) > 0:
            color = self.bot.settings["EmbedColor"]
            await mutesSql.delete_all_mute_users(ctx.guild.id)
            await BotUtils.send_msg(self, ctx, color, "Successfully unmuted all members.")
        else:
            await BotUtils.send_error_msg(self, ctx, "There are no muted members in this server.")

    #################################################################################
    @mute.command(name="list")
    @commands.cooldown(1, CoolDowns.MuteCooldown.value, BucketType.user)
    async def mute_list(self, ctx):
        """(List all muted users)
         
        Example:
        mute list
        """

        bl_members = []
        bl_reason = []
        bl_author = []
        position = 1

        mutesSql = MutesSql(self.bot)
        rs = await mutesSql.get_all_server_mute_users(ctx.guild.id)
        if len(rs) > 0:
            for key, value in rs.items():
                member_name = f"{ctx.guild.get_member(value['discord_user_id'])}"
                author_name = BotUtils.get_member_name_by_id(self, ctx, value["discord_author_id"])
                bl_author.append(author_name)
                bl_members.append(f"{position}) {member_name}")
                if value["reason"] is None:
                    bl_reason.append("---")
                else:
                    bl_reason.append(value["reason"])
                position += 1

            members = '\n'.join(bl_members)
            reason = '\n'.join(bl_reason)
            author = '\n'.join(bl_author)

            embed = discord.Embed(description="*`Members that cannot type anything`*", color=discord.Color.red())
            embed.set_footer(text=f"For more info: {ctx.prefix}help mute")
            embed.set_author(name="Muted members in this server:\n\n", icon_url=f"{ctx.guild.icon_url}")
            embed.add_field(name="Member", value=Formatting.inline(members), inline=True)
            embed.add_field(name="Added by", value=Formatting.inline(author), inline=True)
            embed.add_field(name="Reason", value=Formatting.inline(reason), inline=True)

            await BotUtils.send_embed(self, ctx, embed, False)
        else:
            await BotUtils.send_error_msg(self, ctx, "There are no muted members in this server.")

    ################################################################################
    @commands.group(aliases=["cc"])
    @Checks.check_is_admin()
    async def customcom(self, ctx):
        """(Add, remove, edit, list custom commands)
        
        customcom or cc
        
        Example:
        customcom [add | edit] <command> <text/url>
        customcom remove <command>
        customcom removeall
        customcom list
        """

        if ctx.invoked_subcommand is None:
            if ctx.command is not None:
                cmd = ctx.command
            else:
                cmd = self.bot.get_command("customcom")

            await BotUtils.send_help_msg(self, ctx, cmd)
            return

        ctx.invoked_subcommand

    ################################################################################
    @customcom.command(name="add")
    @commands.cooldown(1, CoolDowns.CustomCmdCooldown.value, BucketType.user)
    async def cc_add(self, ctx, command_name: str, *, text: str):
        """(Adds a custom command)

        customcom or cc
        
        Example:
        customcom add <command> <text/url>
        """

        await BotUtils.delete_last_channel_message(self, ctx)
        server = ctx.guild
        command_name = command_name.lower()
        for cmd in self.bot.commands:
            if str(command_name) == str(cmd.name).lower():
                await BotUtils.send_error_msg(self, ctx, f"`{ctx.prefix}{command_name}` is already a standard command.")
                return

        if len(command_name) > 20:
            await BotUtils.send_error_msg(self, ctx, "Command names cannot exceed 20 characters.\n" \
                                                  "Please try again with another name.")
            return

        commandsSql = CommandsSql(self.bot)
        rs = await commandsSql.get_command(server.id, str(command_name))
        if len(rs) == 0:
            color = self.bot.settings["EmbedColor"]
            await commandsSql.insert_command(ctx.author, str(command_name), str(text))
            await BotUtils.send_msg(self, ctx, color, f"Custom command successfully added:\n`{ctx.prefix}{command_name}`")
        else:
            await BotUtils.send_error_msg(self, ctx,
                                       f"Command already exists: `{ctx.prefix}{command_name}`\n"
                                       f"To edit use: `{ctx.prefix}customcom edit {command_name} <text/url>`")

    ################################################################################
    @customcom.command(name="remove")
    @commands.cooldown(1, CoolDowns.CustomCmdCooldown.value, BucketType.user)
    async def cc_remove(self, ctx, command_name: str):
        """(Removes a custom command)

        customcom or cc
        
        Example:
        customcom remove <command>
        """

        server = ctx.guild
        command_name = command_name.lower()

        commandsSql = CommandsSql(self.bot)
        rs = await commandsSql.get_all_commands(server.id)
        if len(rs) == 0:
            await BotUtils.send_error_msg(self, ctx, "There are no custom commands in this server.")
            return

        rs = await commandsSql.get_command(server.id, str(command_name))
        if len(rs) > 0:
            color = self.bot.settings["EmbedColor"]
            await commandsSql.delete_command(server.id, str(command_name))
            await BotUtils.send_msg(self, ctx, color, f"Custom command successfully removed:\n`{ctx.prefix}{command_name}`")
        else:
            await BotUtils.send_error_msg(self, ctx, "That command doesn't exist.")

    ################################################################################
    @customcom.command(name="edit")
    @commands.cooldown(1, CoolDowns.CustomCmdCooldown.value, BucketType.user)
    async def cc_edit(self, ctx, command_name: str, *, text: str):
        """(Edits a custom command)

        customcom or cc
        
        Example:
        customcom edit <command> <text/url>
        """

        await BotUtils.delete_last_channel_message(self, ctx)
        server = ctx.guild
        command_name = command_name.lower()

        commandsSql = CommandsSql(self.bot)
        rs = await commandsSql.get_all_commands(server.id)
        if len(rs) == 0:
            await BotUtils.send_error_msg(self, ctx, "There are no custom commands in this server.")
            return

        rs = await commandsSql.get_command(server.id, str(command_name))
        if len(rs) > 0:
            color = self.bot.settings["EmbedColor"]
            await commandsSql.update_command(server.id, str(command_name), str(text))
            await BotUtils.send_msg(self, ctx, color, f"Custom command successfully edited:\n`{ctx.prefix}{command_name}`")
        else:
            await BotUtils.send_error_msg(self, ctx,
                                       f"Command doesn't exist in this server:\n`{ctx.prefix}{command_name}`")

    ################################################################################
    @customcom.command(name="removeall")
    @commands.cooldown(1, CoolDowns.CustomCmdCooldown.value, BucketType.user)
    async def cc_remove_all(self, ctx):
        """(Removes all custom commands)

        customcom or cc
        
        Example:
        customcom removeall
        """

        server = ctx.guild
        commandsSql = CommandsSql(self.bot)
        color = self.bot.settings["EmbedColor"]
        rs = await commandsSql.get_all_commands(server.id)
        if len(rs) == 0:
            await BotUtils.send_error_msg(self, ctx, "There are no custom commands in this server.")
            return

        await commandsSql.delete_all_commands(server.id)
        await BotUtils.send_msg(self, ctx, color, "All custom commands successfully removed.")

    ################################################################################
    @customcom.command(name="list")
    @commands.cooldown(1, CoolDowns.CustomCmdCooldown.value, BucketType.user)
    async def cc_list(self, ctx):
        """(Shows custom commands list)

        customcom or cc
        
        Example:
        customcom list
        """

        server = ctx.guild
        commandsSql = CommandsSql(self.bot)
        rs = await commandsSql.get_all_commands(server.id)
        if len(rs) == 0:
            await BotUtils.send_error_msg(self, ctx, "There are no custom commands in this server.")
            return

        command = []
        author = []
        date = []
        position = 1
        for key, value in rs.items():
            author_name = BotUtils.get_member_name_by_id(self, ctx, value["discord_author_id"])
            command.append(f"{position}) {value['command_name']}")
            author.append(str(author_name))
            date.append(str(f"{value['date'].split()[0]}"))
            position += 1

        commands = '\n'.join(command)
        authors = '\n'.join(author)
        dates = '\n'.join(date)

        color = self.bot.settings["EmbedColor"]
        embed = discord.Embed(color=color)
        embed.set_footer(text=f"For more info: {ctx.prefix}help cc")
        embed.set_author(name="Custom commands in this server",
                         icon_url=f"{ctx.guild.icon_url}")
        embed.add_field(name="Command", value=Formatting.inline(commands), inline=True)
        embed.add_field(name="Created by", value=Formatting.inline(authors), inline=True)
        embed.add_field(name="Date Created", value=Formatting.inline(dates), inline=True)

        await BotUtils.send_embed(self, ctx, embed, False)


###############################################################################
def setup(bot):
    bot.add_cog(Admin(bot))
