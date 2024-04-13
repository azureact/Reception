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

# 初始化 bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents, proxy="sock5://127.0.0.1:25575")

# 全局变量
code_dic = {}  # 字典，{discord_id : [wikidot_id,code,time]}
messages = []
allowed_user_ids = []  # 允许执行命令的用户列表
roles_dict = {}
users_dic = {}

# 读取用户字典
try:
    with open("users_dic.pkl", "rb") as file:
        users_dic = pickle.load(file)
except FileNotFoundError:
    pass

# 初始化 Selenium WebDriver
chrome_options = Options()
# chrome_options.add_argument('--headless') #无头浏览器
chrome_options.add_argument("blink-settings=imagesEnabled=false")
chrome_options.add_argument("--disable-gpu")
# 获取 cookies
driver = webdriver.Chrome(options=chrome_options)
driver.get("")
driver.find_element(By.XPATH, "//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[1]/div/input").send_keys("")
driver.find_element(By.XPATH, "//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[2]/div/input").send_keys("")
driver.find_element(By.XPATH, "//*[@id='html-body']/div[2]/div[2]/div/div[1]/div[1]/form/div[4]/div/button").click()
cookies = driver.get_cookies()
driver.close()

# 清理过期验证码
async def dic_clear():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(60)
        now = time.time()
        del_list = [discord_id for discord_id, data in code_dic.items() if now - data[2] >= 300]
        for discord_id in del_list:
            del code_dic[discord_id]
            with open("users_dic.pkl", "wb") as file:
                pickle.dump(users_dic, file)

# 验证函数
async def verify(ctx, wikidot_id: str):
    discord_id = str(ctx.author.id)
    now = time.time()
    flag2 = 0
    try:
        if now - code_dic[discord_id][2] < 60:
            await ctx.send("已申请验证，请在1分钟后重试")
            return
    except KeyError:
        pass
    
    try:
        if users_dic[discord_id]:
            await ctx.send(f"此账户已绑定*{users_dic[discord_id]}*。")
            wikidot_id = users_dic[discord_id]
            flag2 = 1
    except KeyError:
        pass

    for i in users_dic:
        if i[0] == wikidot_id:
            await ctx.send(f"wikidot账号*{wikidot_id}*已被绑定。")
            return

    code_dic[discord_id] = [wikidot_id, "", now, 0]

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.wikidot.com/user:info/" + wikidot_id)
    for cookie in cookies:
        driver.add_cookie(cookie)
    try:
        driver.find_element(By.XPATH, '//*[@id="ui-member-b"]').click()
        try:
            time.sleep(2)
            driver.find_element(By.LINK_TEXT, "")  # wikidot网站名称
            flag = 0
        except NoSuchElementException:
            flag = 1
    except NoSuchElementException:
        driver.close()
        await ctx.send("未找到对应Wikidot账号，请重新输入。")
        del code_dic[discord_id]
        return
    
    if flag2:
        driver.close()
        del code_dic[discord_id]
        return
    
    if wikidot_id == "":
        driver.close()
        del code_dic[discord_id]
        await ctx.send("参数不足：缺少wikidot用户名")
        return
    
    driver.refresh()
    driver.get(driver.find_element(By.XPATH, '//*[@id="page-content"]/div[2]/a[1]').get_attribute("href"))
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, '//*[@id="pm-subject"]').send_keys("xxxDiscord服务器验证码")
    code = "".join(random.sample(string.digits, 6))
    driver.find_element(By.XPATH, '//*[@id="editor-textarea"]').send_keys(f"你的验证码是{code}，五分钟之内有效。")
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="new-pm-form"]/div[5]/input[3]').click()
    time.sleep(3)
    code_dic[discord_id] = [wikidot_id, code, time.time(), flag]
    driver.close()
    await ctx.send("验证码已发送，请在五分钟内输入验证码以完成验证。")
@bot.command(name='verify', description='创建一个认证')
async def verify_command(ctx, wikidot_id: str):
    await verify(ctx, wikidot_id)

@bot.command(name='code', description='使用BRbot向你Wikidot收件箱发送的验证码')
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
                await ctx.send("验证成功，已分配至身份组“未入站-UNVERIFIED”")
            else:
                await ctx.send("验证成功，已分配至身份组“站内成员-MEMBERS”")
            discord_name = ctx.author.nick
            users_dic[discord_id] = code_dic[discord_id][0]
            if users_dic[discord_id] not in discord_name:
                await ctx.author.edit(nick=f"{discord_name}/{code_dic[discord_id][0]}")
            del code_dic[discord_id]
        else:
            await ctx.send("验证码错误")
    except KeyError:
        await ctx.send("没有申请验证码或验证码已过期")

# 启动 bot
bot.loop.create_task(dic_clear())
bot.run("")
