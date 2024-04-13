import string
import random
import time
import asyncio
import threading
import discord
import pickle
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

code_dic={} #字典，{discord_id : [wikidot_id,code,time]}
messages=[]
allowed_user_ids = [953957224076705835, 292596329224470528, 1000762888107081788] #允许执行命令的用户列表
roles_dict = {}
with open("users_dic.pkl", "rb") as file:
    users_dic = pickle.load(file)
intents = discord.Intents.all()
intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)
chrome_options = Options()
#chrome_options.add_argument('--headless') #无头浏览器
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-gpu')
#cookies=[{'domain': 'www.wikidot.com', 'expiry': 1704637498, 'httpOnly': False, 'name': '__utmt_old', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1'}, {'domain': 'www.wikidot.com', 'expiry': 1720404898, 'httpOnly': False, 'name': '__utmz', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1.1704636898.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}, {'domain': 'www.wikidot.com', 'expiry': 1704638698, 'httpOnly': False, 'name': '__utmb', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1.2.10.1704636898'}, {'domain': 'www.wikidot.com', 'expiry': 1739196898, 'httpOnly': False, 'name': '__utma', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1.1345090849.1704636898.1704636898.1704636898.1'}, {'domain': 'www.wikidot.com', 'expiry': 1704637498, 'httpOnly': False, 'name': '__utmt', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1'}, {'domain': 'www.wikidot.com', 'httpOnly': False, 'name': '__utmc', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1'}, {'domain': '.wikidot.com', 'expiry': 1705846496, 'httpOnly': False, 'name': 'wikidot_udsession', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1'}, {'domain': '.wikidot.com', 'expiry': 1714636894, 'httpOnly': False, 'name': 'WIKIDOT_SESSION_ID', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'ea8b5c28dc4f5f0b0eebdf4eb1f90d4e419ae91260719cde66a35a1'}, {'domain': 'www.wikidot.com', 'httpOnly': False, 'name': 'WIKIDOT_SESSION_ID_IE', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'ea8b5c28dc4f5f0b0eebdf4eb1f90d4e419ae91260719cde66a35a1'}, {'domain': 'www.wikidot.com', 'expiry': 1704723291, 'httpOnly': False, 'name': 'wikidot_token7', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '3be7ea94640c6e04fe05727a39546fbc'}]
#获取cookies
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.wikidot.com/default--flow/login__LoginPopupScreen?originSiteId=4716348&openerUri=http://backrooms-wiki-cn.wikidot.com")
driver.find_element(By.XPATH,"//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[1]/div/input").send_keys("")
driver.find_element(By.XPATH,"//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[2]/div/input").send_keys("")
driver.find_element(By.XPATH,"//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[4]/div/button").click()
cookies=driver.get_cookies()
driver.close()


#初始化
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    global messages
    while True:
        if messages==[]:
            await asyncio.sleep(1)
        else:
            mes_temp=messages[0]
            del messages[0]
            channel = bot.get_channel(mes_temp[0].channel.id)
            await channel.send(f'<@{mes_temp[1]}>{mes_temp[2]}')
            if mes_temp[2]=='身份组更新完成':
                guild = mes_temp[0].guild
                await mes_temp[0].author.add_roles(guild.get_role(934286697942908968))
                await mes_temp[0].author.remove_roles(guild.get_role(1193187250553503866))

#验证函数
def verify(ctx, wikidot_id: str):
    discord_id = str(ctx.author.id)
    now=time.time()
    flag2=0
    try:
        if now-code_dic[discord_id][2]<60:
            messages.append([ctx, discord_id, '已申请验证，请在1分钟后重试'])
    except KeyError:
        try:
            messages.append([ctx, discord_id, f'此账户已绑定*{users_dic[discord_id]}*。'])
            wikidot_id=users_dic[discord_id]
            flag2=1
        except KeyError:
            for i in users_dic:
                if i[0]==wikidot_id:
                    messages.append([ctx, discord_id, f'wikidot账号*{wikidot_id}*已被绑定。'])
                    return None
        code_dic[discord_id]=[wikidot_id,'',now,0]
        print(time.time())
        driver = webdriver.Chrome(options=chrome_options)
        print(time.time())
        driver.get("https://www.wikidot.com/user:info/" + wikidot_id)
        for cookie in cookies:
            driver.add_cookie(cookie)
        try:
            driver.find_element(By.XPATH, '//*[@id="ui-member-b"]').click()
            try:
                time.sleep(2)
                driver.find_element(By.LINK_TEXT, 'The Backrooms中文维基')
                flag = 0
                if ctx.guild.get_role(1193187250553503866) in ctx.author.roles:
                    messages.append([ctx, discord_id, '身份组更新完成'])
            except NoSuchElementException:
                flag = 1
        except NoSuchElementException:
            driver.close()
            messages.append([ctx, discord_id, '未找到对应Wikidot账号，请重新输入。'])
            del code_dic[discord_id]
            return None
        if flag2:
            del code_dic[discord_id]
            return None
        if wikidot_id=='':
            del code_dic[discord_id]
            messages.append([ctx, discord_id, '缺少wikidot用户名'])
            return None
        driver.refresh()
        driver.get(driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/a[1]').get_attribute('href'))
        driver.implicitly_wait(3)
        driver.find_element(By.XPATH, '//*[@id="pm-subject"]').send_keys('The Backrooms Wikidot中文官方Discord服务器验证码')
        code = "".join(random.sample(string.digits, 6))
        driver.find_element(By.XPATH, '//*[@id="editor-textarea"]').send_keys(f'你的验证码是{code}，五分钟之内有效。')
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="new-pm-form"]/div[5]/input[3]').click()
        time.sleep(3)
        code_dic[discord_id] = [wikidot_id, code, time.time(), flag]
        driver.close()
        messages.append([ctx, discord_id, '验证码已发送，请在五分钟内输入验证码以完成验证。'])

#清理过期验证码
def dic_clear():
    while True:
        with open("users_dic.pkl", "wb") as file:
            pickle.dump(users_dic, file)
        now = time.time()
        del_list=[]
        for i in code_dic:
            if now - code_dic[i][2] >= 300:
                del_list.append(i)
        for i in del_list:
            del code_dic[i]
        time.sleep(60)

#命令处理
@bot.command(name='verify')
async def verify_command(ctx, wikidot_id=''):
    wikidot_id=ctx.message.content[8:].strip('[]').replace(' ','-')
    print(wikidot_id)
    await ctx.reply("正在验证您的Wikidot账户，该操作完成的时间可能较长，请耐心等候...")
    t1=threading.Thread(target=verify,args=(ctx,wikidot_id))
    t1.start()

@bot.command(name='code')
async def code_command(ctx, code: str):
    discord_id = str(ctx.author.id)
    try:
        if code_dic[discord_id][1] == code:
            role_id = 1193187250553503866 if code_dic[discord_id][3] else 934286697942908968
            guild = ctx.guild
            role = guild.get_role(role_id)
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role)
                await ctx.author.remove_roles(guild.get_role(946371453622829057))
                await ctx.reply('验证成功，身份组分配完成')
            else:
                await ctx.reply('验证成功')
            discord_name=ctx.author.nick
            print(discord_name)
            users_dic[discord_id] = code_dic[discord_id][0]
            #if users_dic[discord_id] not in discord_name:
                #await ctx.author.edit(nick=f'{discord_name}/{code_dic[discord_id][0]}')
            del code_dic[discord_id]
        else:
            await ctx.reply('验证码错误')
    except KeyError:
        await ctx.reply('没有申请验证码或验证码已过期')

@bot.command(name='check')
async def check_command(ctx, discord_id=''):
    if discord_id=='':
        discord_id=str(ctx.author.id)
    else:
        discord_id=discord_id.strip('[]<>@')
    try:
        await ctx.reply(f'该账号已绑定wikidot账号*{users_dic[discord_id]}*。')
    except KeyError:
        await ctx.reply('该账户未绑定，请稍后再试')

@bot.command(name='roleedit')
async def role_edit(ctx, action, user_id, role_id):
    if ctx.message.author.id not in allowed_user_ids:
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


threading.Thread(target=dic_clear,args=()).start()
bot.run('')
