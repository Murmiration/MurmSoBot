from discord.ext import commands
import discord.utils
import json
import os


class No_Owner(commands.CommandError):
    pass


class No_Perms(commands.CommandError):
    pass


class No_Role(commands.CommandError):
    pass


class No_Admin(commands.CommandError):
    pass


class No_Mod(commands.CommandError):
    pass


class No_Sup(commands.CommandError):
    pass


class No_GuildandPerm(commands.CommandError):
    pass


class Nsfw(commands.CommandError):
    pass


owner_id = 386735585563246592


def is_owner_check(message):
    if message.author.id == owner_id:
        return True
    raise No_Owner()


def is_owner():
    return commands.check((lambda ctx: is_owner_check(ctx.message)))


def check_permissions(ctx, perms):
    msg = ctx.message
    if msg.author.id == owner_id:
        return True
    ch = msg.channel
    author = msg.author
    resolved = ch.permissions_for(author)
    if all((getattr(resolved, name, None) == value for (name, value) in perms.items())):
        return True
    return False


def role_or_perm(t, ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True
    ch = ctx.channel
    author = ctx.author
    if ch.is_private:
        return False
    role = discord.utils.find(check, author.roles)
    if role is not None:
        return True
    if t:
        return False
    else:
        raise No_Role()


admin_perms = ['administrator', 'manage_server']
mod_perms = ['manage_messages', 'ban_members', 'kick_members']
mod_roles = ('mod', 'moderator')


def mod_or_perm(**perms):
    def predicate(ctx):
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        if role_or_perm(True, ctx, (lambda r: (r.name.lower() in mod_roles)), **perms):
            return True
        for role in ctx.author.roles:
            role_perms = []
            for s in role.permissions:
                role_perms.append(s)
            for s in role_perms:
                for x in mod_perms:
                    if (s[0] == x) and (s[1] == True):
                        return True
                for x in admin_perms:
                    if (s[0] == x) and (s[1] == True):
                        return True
        raise No_Mod()

    return commands.check(predicate)


admin_roles = ('admin', 'administrator', 'mod', 'moderator', 'owner', 'god', 'manager', 'boss')


def admin_or_perm(**perms):
    def predicate(ctx):
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        if role_or_perm(True, ctx, (lambda r: (r.name.lower() in admin_roles)), **perms):
            return True
        for role in ctx.author.roles:
            role_perms = []
            for s in role.permissions:
                role_perms.append(s)
            for s in role_perms:
                for x in admin_perms:
                    if (s[0] == x) and (s[1] == True):
                        return True
        raise No_Admin()

    return commands.check(predicate)


def is_in_servers(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return commands.check(predicate)


def server_and_perm(ctx, *guild_ids, **perms):
    if isinstance(ctx.channel, discord.abc.PrivateChannel):
        return False
    guild = ctx.guild
    if guild is None:
        return False
    if guild.id in guild_ids:
        if check_permissions(ctx, perms):
            return True
        return False
    raise No_GuildandPerm()


def sup(ctx):
    guild = ctx.guild
    if guild.id == 197938366530977793:
        return True
    raise No_Sup()


def nsfw():
    def predicate(ctx):
        channel = ctx.channel
        if isinstance(channel, discord.abc.PrivateChannel):
            return True
        if channel.is_nsfw():
            return True
        raise Nsfw()

    return commands.check(predicate)
