import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

allowed_user_ids = [] #允许执行命令的用户列表

roles_dict = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='roleedit')
async def role_edit(ctx, action, user_id, role_id):
    if ctx.message。author.id not in allowed_user_ids:
        await ctx.send("在权限检查时出现错误：权限不足")
        return

    if action not in ['add', 'del']:
        await ctx.send("在使用命令时出现错误：无效的参数")
        return

    user = bot.get_user(int(user_id))
    member = ctx.guild.get_member(int(user_id))

    role = discord.utils.get(ctx.guild.roles, id=int(role_id))

    if user is None or member is None or role is None:
        await ctx.send("在执行命令时出现错误：无效的用户ID、成员或身份组ID")
        return

    if action == 'add':
        await member.add_roles(role)
        roles_dict.setdefault(str(user.id), []).append(str(role.id))
        await ctx.send(f"已添加*{user.name}*到*{role.name}*身份组")
    elif action == 'del':
        if str(role.id) in roles_dict.get(str(user.id), []):
            await member.remove_roles(role)
            roles_dict[str(user.id)].remove(str(role.id))
            await ctx.send(f"已从*{user.name}*移除*{role.name}*身份组")
        else:
            await ctx.send(f"错误：*{user.name}*不在*{role.name}*身份组中")

bot.run('')
