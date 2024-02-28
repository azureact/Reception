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

global chrome_options,code_dic,cookies,messages,users_dic,bot
code_dic={} #字典，{discord_id : [wikidot_id,code,time]}
messages=[]
with open("users_dic.pkl", "rb") as file:
    users_dic = pickle.load(file)
intents = discord.Intents.default()
intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)
chrome_options = Options()
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.wikidot.com/default--flow/login__LoginPopupScreen?originSiteId=4716348&openerUri=http://backrooms-wiki-cn.wikidot.com")
driver.find_element(By.XPATH,"//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[1]/div/input").send_keys("")#被自动填写的Wikidot账号
driver.find_element(By.XPATH,"//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[2]/div/input").send_keys("")#被自动填写的Wikidot密码
driver.find_element(By.XPATH,"//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[4]/div/button").click()
cookies=driver.get_cookies()
driver.close()

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
            channel = bot.get_channel(mes_temp[0])
            await channel.send(mes_temp[1])
#验证函数
def verify(ctx, wikidot_id: str):
    discord_id = str(ctx.author.id)
    now=time.time()
    try:
        if now-code_dic[discord_id][2]<60:
            messages.append([ctx.channel.id,'<@'+discord_id+'>已申请验证码，请在1分钟后重试'])
            return None
    except KeyError:
        code_dic[discord_id]=[wikidot_id,'',now,0]
        try:
            messages.append([ctx.channel.id,'<@'+discord_id+'>此账户已绑定*'+users_dic[discord_id]+'*。'])
            del code_dic[discord_id]
            return None
        except KeyError:
            for i in users_dic:
                if users_dic[i]==wikidot_id:
                    messages.append([ctx.channel.id,'<@'+discord_id+'>wikidot账号*'+wikidot_id+'*已被绑定。'])
                    del code_dic[discord_id]
                    return None
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://www.wikidot.com/user:info/" + wikidot_id)
            for cookie in cookies:
                driver.add_cookie(cookie)
            try:
                driver.find_element(By.XPATH, '//*[@id="ui-member-b"]').click()
                try:
                    time.sleep(2)
                    driver.find_element(By.LINK_TEXT, 'The Backrooms中文维基')
                    flag = 0
                except NoSuchElementException:
                    flag = 1
            except NoSuchElementException:
                driver.close()
                messages.append([ctx.channel.id,'<@'+discord_id+'>未找到对应Wikidot账号，请重新输入。'])
                del code_dic[discord_id]
                return None
            driver.get("https://www.wikidot.com/user:info/" + wikidot_id)
            driver.get(driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/a[1]').get_attribute('href'))
            driver.implicitly_wait(3)
            driver.find_element(By.XPATH, '//*[@id="pm-subject"]').send_keys('The Backrooms Wikidot中文官方Discord服务器验证码')
            code = "".join(random.sample(string.digits, 6))
            driver.find_element(By.XPATH, '//*[@id="editor-textarea"]').send_keys('你的验证码是' + code + '，五分钟之内有效。')
            time.sleep(1)
            driver.find_element(By.XPATH, '//*[@id="new-pm-form"]/div[5]/input[3]').click()
            time.sleep(3)
            code_dic[discord_id] = [wikidot_id, code, time.time(), flag]
            driver.close()
            messages.append([ctx.channel.id,'<@'+discord_id+'>验证码已发送，请在五分钟内输入验证码以完成验证。'])

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
    if wikidot_id=='':
        await ctx.reply("缺少wikidot用户名")
    else:
        wikidot_id=ctx.message.content[8:].strip('[]').replace(' ','-')
        print(wikidot_id)
        await ctx.reply("正在向您的Wikidot账户发送验证码，该操作完成的时间可能较长，请耐心等候...")
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
            users_dic[discord_id] = code_dic[discord_id][0]
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
        await ctx.reply('该账号已绑定wikidot账号*'+users_dic[discord_id]+'*。')
    except KeyError:
        await ctx.reply('该账户未绑定，请稍后再试')

threading.Thread(target=dic_clear,args=()).start()
bot.run('')
