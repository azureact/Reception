import string
import random
import time
import asyncio
import threading
import discord
import pickle
import yaml
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import os

code_dic = {}  # 字典，{discord_id : [wikidot_id,code,time]}
messages = []
allowed_user_ids = [953957224076705835, 292596329224470528, 1000762888107081788]  # 允许执行命令的用户列表
roles_dict = {}

# 读取配置文件
if os.path.exists("config.yml"):
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
else:
    config = {
        "WikidotAccount": "",
        "WikidotPassword": "",
        "DiscordToken": ""
    }
    with open("config.yml", "w") as file:
        yaml.dump(config, file)

# 初始化
if os.path.exists("users_dic.pkl"):
    with open("users_dic.pkl", "rb") as file:
        users_dic = pickle.load(file)
else:
    users_dic = {}

intents = discord.Intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)
chrome_options = Options()
# chrome_options.add_argument('--headless') #无头浏览器
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-gpu')

# 获取配置信息
wikidot_account = config.get("WikidotAccount", "")
wikidot_password = config.get("WikidotPassword", "")
discord_token = config.get("DiscordToken", "")

# 初始化webdriver并登录
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.wikidot.com/default--flow/login__LoginPopupScreen?originSiteId=4716348&openerUri=http://backrooms-wiki-cn.wikidot.com")
driver.find_element(By.XPATH, "//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[1]/div/input").send_keys(wikidot_account)
driver.find_element(By.XPATH, "//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[2]/div/input").send_keys(wikidot_password)
driver.find_element(By.XPATH, "//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[4]/div/button").click()
cookies = driver.get_cookies()
driver.close()

# 验证函数
def verify(ctx, wikidot_id: str):
    discord_id = str(ctx.author.id)
    now = time.time()
    flag2 = 0
    try:
        if now - code_dic[discord_id][2] < 60:
            messages.append([ctx, discord_id, '已申请验证，请在1分钟后重试'])
    except KeyError:
        try:
            messages.append([ctx, discord_id, f'此账户已绑定*{users_dic[discord_id]}*。'])
            wikidot_id = users_dic[discord_id]
            flag2 = 1
        except KeyError:
            for i in users_dic:
                if i[0] == wikidot_id:
                    messages.append([ctx, discord_id, f'wikidot账号*{wikidot_id}*已被绑定。'])
                    return None
        code_dic[discord_id] = [wikidot_id, '', now, 0]
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
        if wikidot_id == '':
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

# 清理过期验证码
def dic_clear():
    while True:
        with open("users_dic.pkl", "wb") as file:
            pickle.dump(users_dic, file)
        now = time.time()
        del_list = []
        for i in code_dic:
            if now - code_dic[i][2] >= 300:
                del_list.append(i)
        for i in del_list:
            del code_dic[i]
        time.sleep(60)

# 命令处理
@bot.command(name='verify')
async def verify_command(ctx, wikidot_id=''):
    wikidot_id = ctx.message.content[8:].strip('[]').replace(' ', '-')
    print(wikidot_id)
    await ctx.reply("正在验证您的Wikidot账户，该操作完成的时间可能较长，请耐心等候...")
    t1 = threading.Thread(target=verify, args=(ctx, wikidot_id))
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
            discord_name = ctx.author.nick
            print(discord_name)
            users_dic[discord_id] = code_dic[discord_id][0]
            # if users_dic[discord_id] not in discord_name:
            # await ctx.author.edit(nick=f'{discord_name}/{code_dic[discord_id][0]}')
            del code_dic[discord_id]
        else:
            await ctx.reply('验证码错误')
    except KeyError:
        await ctx.reply('没有申请验证码或验证码已过期')

@bot.command(name='check')
async def check_command(ctx, discord_id=''):
    if discord_id == '':
        discord_id = str(ctx.author.id)
    else:
        discord_id = discord_id.strip('[]<>@')
    try:
        await ctx.reply(f'该账号已绑定wikidot账号*{users_dic[discord_id]}*。')
    except KeyError:
        await ctx.reply('该账户未绑定，请稍后再试')

@bot.command(name='roleedit')
async def role_edit(ctx, action, user_id, role_id):
    if ctx.message.author.id not in allowed_user_ids:
        await ctx.send("在权限检查时出现错误：权限不足")
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

# 启动清理线程
threading.Thread(target=dic_clear, args=()).start()

# 运行bot
bot.run(discord_token)
