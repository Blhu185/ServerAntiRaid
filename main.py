"""Server Anti-Raid, developed by ACPlayGames!"""

import json

import discord
from discord.ext import commands


async def get_prefix(bot_, message):
    """Returns the appropriate prefix for the bot."""
    with open('./data/options.json', 'r') as options_file:
        options_dict = json.load(options_file)

    if message.guild and str(message.guild.id) in options_dict:
        prefixes = options_dict[str(message.guild.id)]['prefix']
    else:
        prefixes = '.'

    return commands.when_mentioned_or(*prefixes)(bot_, message)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents
)
bot.remove_command('help')

blue = discord.Color.blue()


@bot.event
async def on_ready():
    """Tells the bot what to do when it is ready."""
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name='your every move...'
        )
    )
    print(
        '\nBot Ready!\n',
        f'\nClient User: {str(bot.user)}',
        f'\nUser ID: {bot.user.id}',
        f'\nDiscord Library Version: {discord.__version__} ' +
        f'{discord.version_info.releaselevel}\n'
    )


@bot.event
async def on_command_error(ctx, error):
    """Handles any errors raised by the commands extension."""
    if not isinstance(error, commands.CommandNotFound):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'Please input a valid **{error.param.name}** argument!'
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('Please use commands in a guild!')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('Sorry, I do not have administrator permission!')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You are not allowed to use this bot! Shoo!')
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = round(error.retry_after, 1)
            await ctx.send(f'Woah, slow down! Please wait `{seconds}` secs!')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('Uh oh! Something went wrong!')
        else:
            await ctx.send(error)


@bot.check
async def global_check(ctx):
    """Bot checks for permissions and the location of the message."""
    # check if command is in DMs
    guild_only = await commands.guild_only().predicate(ctx)

    # check for bot permissions in guild
    bot_perms = await commands.bot_has_guild_permissions(
        administrator=True).predicate(ctx)

    # anyone can use report command
    if ctx.command.name == 'report':
        return bot_perms and guild_only

    # not report command, check for user permissions in guild
    author = ctx.author
    with open('./data/options.json', 'r') as options_file:
        options = json.load(options_file)

    guild_key = str(ctx.guild.id)
    if guild_key not in options:
        mod_role = None
    else:
        mod_role = options[guild_key]['mod_role']
        mod_role = ctx.guild.get_role(mod_role)

    admin_perms = author.guild_permissions.administrator
    mod_only = mod_role in author.roles or admin_perms

    return bot_perms and guild_only and mod_only

bot.load_extension('cogs.lockdown')
bot.load_extension('cogs.logs')
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.options')


@bot.command(name='help')
async def help_(ctx, command=None):
    """More elaborate help command than the default help command."""
    cog_dict = {cog.lower(): bot.cogs[cog] for cog in bot.cogs}
    cmd_dict = {cmd.name.lower(): cmd.help for cmd in bot.commands}

    if not command:
        # General help command, includes list of cogs & commands
        help_title = 'Server Anti-Raid Help'
        help_description = 'Thank you for using the bot!'
    elif command.lower() in cog_dict:
        # Cogs
        help_title = command.upper()
        help_description = cog_dict[command.lower()].description
    elif command.lower() in cmd_dict:
        # Commands
        help_title = command.upper()
        help_description = cmd_dict[command.lower()]
    else:
        await ctx.send('Please input a valid command or cog!')
        return

    help_embed = discord.Embed(
        title=help_title,
        description=help_description,
        color=blue
    )
    help_embed.set_footer(
        text='Do `.help <cog or command>` for more information!'
    )

    if not command:
        help_embed.add_field(
            name='Lockdown',
            value='`lock` `unlock` `lockall` `unlockall` `purge` ' +
            '`slowmode`',
            inline=False
        )
        help_embed.add_field(
            name='Logs',
            value='`check`',
            inline=False
        )
        help_embed.add_field(
            name='Moderation',
            value='`warn` `warnings` `clearwarn` `mute` `unmute` `kick` ' +
            '`ban` `bans` `unban` `report`',
            inline=False
        )
        help_embed.add_field(
            name='Options',
            value='`settings`',
            inline=False
        )
    elif command is not None and command.lower() in cog_dict:
        cmds = cog_dict[command.lower()].get_commands()

        for cmd in cmds:
            help_embed.add_field(
                name=cmd.name.upper(),
                value=cmd.help,
                inline=False
            )

    await ctx.send(embed=help_embed)

bot.run('TOKEN HERE')
