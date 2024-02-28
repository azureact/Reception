import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = 
offline_user_id = 
subscribed_channels = set()
reconnection_flag = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_presence_update(before, after):
    global reconnection_flag
    if after.id == offline_user_id and before.status != after.status and after.status == discord.Status.offline:
        warning_message = ":warning: **Reception 离线，请检查服务状态！**@everyone"
        for channel_id in subscribed_channels:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(warning_message)
        reconnection_flag = True
    elif after.id == offline_user_id and before.status != after.status and after.status == discord.Status.online and reconnection_flag:
        reconnection_message = ":white_check_mark: **Reception 已重新连接！**"
        for channel_id in subscribed_channels:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(reconnection_message)
        reconnection_flag = False

@bot.command(name='wn-channel')
async def warn_channel(ctx):
    subscribed_channels.add(ctx.channel.id)
    await ctx.send('Done')

bot.run('')
