import server



import os
import discord
import asyncio
import datetime 

from ast import literal_eval
import random

from replit import db
from discord.ext import commands
# from keep_alive import keep_alive

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents().default()
command_prefix = 'b>'
client = commands.Bot(command_prefix=command_prefix, intents=intents)
# token = os.environ['token']

@client.event
async def on_ready():
  print('以 {0.user} 登入'.format(client))
  print('邀請連結  : ')
  print('https://discordapp.com/oauth2/authorize?client_id=' + str(client.user.id) + '&scope=bot')
  print('指令前輟  : ' + client.command_prefix)
  await list_channel()
  global emoji
  emoji = client.get_emoji(885126061321494529)


@client.command()
async def ping(ctx):
  await ctx.send('Pong! {0}ms'.format(round(client.latency * 1000)))


@client.command()
async def invite(ctx):
  await ctx.send('https://discordapp.com/oauth2/authorize?client_id=' + str(client.user.id) + '&scope=bot')

@client.command()
async def test(ctx):
  # test_bot.runtest()
  pass

@client.command()
@commands.has_role(827219287810244619)
async def clean(ctx, member_id):
  count = 0
  member = None
  for c in ctx.guild.channels:
    if c.type == discord.ChannelType.text:
      permissions_check = get_effective_permissions(c).read_messages &get_effective_permissions(c).manage_messages
      if permissions_check:
        async for m in c.history(around = datetime.datetime.today()):
          if m.author.id == int(member_id):
            await m.delete()
            member = m.author
            count += 1
  if member:
    await ctx.send(f"已刪除 {member.mention} 的 {count} 封訊息")
  else:
    await ctx.send(f"找不到他的任何訊息囉")

@client.command()
@commands.has_role(827219287810244619)
async def changevoice(ctx, *names):
  category = client.get_channel(912755781571608616)
  c_list = category.voice_channels
  if len(c_list) == len(names):
    m = []
    for c, n in zip(c_list, names):
      await c.edit(name=n)
      m.append(c.mention)
    await ctx.reply('名字改好啦！高歌離席\n {0}'.format(' '.join(m)))
  else:
    await ctx.reply('不對喔 數量不對欸')



def get_effective_permissions(channel):
  """returns the effective permissions for the given channel,
     for the current bot user ('me')
     
  Args:
     channel (obj): any type of discord.ChannelType which provides 
                    the method 'overwrites_for'
                    
  Returns:
     discord.Permissions: perm object with the resulting permissions for this channel
  """
  
  me = channel.guild.me

  # overwrites are effective on-top of the guild_permissions
  granted_perms = me.guild_permissions

  # the user specific override has the lowest priority
  # and must be checked first
  role_list = [me] + me.roles

  for role in role_list:
      # role can be a user_obj aswell
      ovr = channel.overwrites_for(role)
      allow, deny = ovr.pair()

      # all values with '1' need to erase the permission bit
      # achieved with (y & (~x))
      granted_perms.value = granted_perms.value & (~deny.value)
      # 'or' to grant permissions by setting the coresponding bit
      granted_perms.value = granted_perms.value | allow.value

  return granted_perms


@client.command()
@commands.has_role(827219287810244619)
async def un(ctx, count):
  db["un"] = str(int(count))
  await ctx.reply(db["un"])

@client.command()
@commands.has_role(827219287810244619)
async def gm(ctx, *, reply):
  try:
    l = db["gm"]
    l = literal_eval(l) # 轉換成list
  except KeyError:
    l = []
  if reply in l:
    kw = "刪除"
    l.remove(reply)
  else:
    kw = "新增 "+str(len(l)+1)
    l.append(reply)
  db["gm"] = str(l)

  embed=discord.Embed(title=kw, description=reply)
  embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
  # embed.set_footer(text=db["gm"])
  await ctx.reply(embed=embed)

  # await ctx.reply('已{0}{1}\n{2}'.format(kw, reply, db["gm"]))


@client.command()
@commands.has_role(827219287810244619)
async def listgm(ctx, index = None):
  if not index:
    l = db["gm"]
    l = literal_eval(l)
    pages = len(l)//9+1

    new_l = []
    for i, r in enumerate(l):
      new_l.append(f'> **{i+1}.** {r}\n')

    cur_page = 1
    # content = f"Page {cur_page}/{pages}:\n{''.join(new_l[cur_page*10-10:cur_page*10])}"
    
    def jointer(l, p):
      result = ''.join(l[p*10-10:p*10])
      return result

    message = await ctx.send(f"Page {cur_page}/{pages}:\n{jointer(new_l, cur_page)}")

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{jointer(new_l, cur_page)}")
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(content=f"Page {cur_page}/{pages}:\n{jointer(new_l, cur_page)}")
                await message.remove_reaction(reaction, user)
            else:
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            # await message.delete()
            break
  else:
    index = int(index)-1
    l = db["gm"]
    l = literal_eval(l)
    reply = l[index]
    msg = await ctx.reply(reply)
    await msg.add_reaction("❌")
    def check(reaction, user):
      return user == ctx.author and str(reaction.emoji) == '❌'
    try:
      reaction,user = await client.wait_for('reaction_add',timeout = (10), check=check)
    except asyncio.TimeoutError:
      pass
    else:
      l.pop(index)
      db["gm"] = str(l)
      embed=discord.Embed(title="刪除", description=reply)
      embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
      # embed.set_footer(text=db["gm"])
      await msg.reply(embed=embed)

async def list_channel():
  global server
  server = client.get_guild(826838482054807622)

  backup_watch_channel_id_list = [641578854623870977, 885907700947505233, 885228233208000534, 890280857628213269]
  global backup_watch_channel_list
  backup_watch_channel_list = channel_setup(backup_watch_channel_id_list)
  
  backup_channel_id_list = [896031931291025428, 898487542406598716]
  global backup_channel_list
  backup_channel_list = channel_setup(backup_channel_id_list)

  highlight_channel_id_list = [897871366894796851]
  global highlight_channel_list
  highlight_channel_list = channel_setup(highlight_channel_id_list)

  gay_channel_id_list = [903355627181588480]
  global gay_channel_list
  gay_channel_list = channel_setup(gay_channel_id_list)

  gay_backup_channel_id_list = [903355627181588480]
  global gay_backup_channel_list
  gay_backup_channel_list = channel_setup(gay_backup_channel_id_list)

  voice_type_channel_id_list = [889897559101931550]
  global voice_type_channel_list
  voice_type_channel_list = channel_setup(voice_type_channel_id_list)

  global highlight_backup_blacklist
  highlight_backup_blacklist = [666604880965795860]
  # user.id

  global gay_backup_whitelist
  gay_backup_whitelist = [429371576849268738]
  # user.id

  global non_voice_whitelist 
  #non_voice_whitelist = [827219287810244619]
  non_voice_whitelist = server.get_role(827219287810244619)


def channel_setup(id):
  channel_id_list = id
  # channel_id_list = [641578854623870977]  # 測試用
  channel_list = []
  for channel_id in channel_id_list:
    channel_list.append(discord.utils.get(client.get_all_channels(), id=channel_id))
  for channel in channel_list:
    # print (channel.name)
    pass
  return channel_list


@client.event
async def on_message(message):
  if not message.author.bot:
    if message.channel.id == 827222221382090762:
      if "ㄩㄇ" in message.content:
        db["un"] = str(int(db["un"])+1)
        if message.author.mention == db["last_un"]:
          await message.reply('你是第{0}個說要ㄩㄉ，怎麼樓上也是你==可憐哪'.format(db["un"]))
        else:
          await message.reply('你是第{0}個說要ㄩㄉ，幫你標樓上{1}'.format(db["un"], db["last_un"]))
        db["last_un"] = message.author.mention
        await message.channel.edit(topic='本頻道已經ㄩ了{0}次'.format(db["un"]))
    if message.content == "早安":
      l = db["gm"]
      l = literal_eval(l)
      reply = random.choice(l)
      await message.reply(reply)
    # if await client.is_owner(message.author):
    if '冷靜' in message.content and len(message.content) < 5:
      await message.channel.send('大家冷靜')
    if '召喚' == message.content:
      await message.channel.send('<@&925347622909280267>')
    if message.channel in voice_type_channel_list:
      if message.author.voice is None and message.author.bot is False:
        if non_voice_whitelist not in message.author.roles:
          await message.reply('你好像不在語音頻道裡欸，這裡是{0}'.format(message.channel.mention), delete_after = 3)
    if message.attachments:
      if message.author.id in gay_backup_whitelist:
        for f in message.attachments:
          for backup_channel in gay_backup_channel_list:
            file_ = await f.to_file()
            content = '{0}\n{1}\n{2}'
            content = content.format(message.author.mention, message.channel.mention, message.jump_url)
            await backup_channel.send(content = content, file = file_)
      if message.channel in backup_watch_channel_list:
        if message.author.id not in highlight_backup_blacklist:
          await message.add_reaction(emoji)
        '''
        try:
          await message.pin()
        except discord.errors.Forbidden:
          pass
        '''
        for f in message.attachments:
          for backup_channel in backup_channel_list:
            file_ = await f.to_file()
            content = '{0}\n{1}\n{2}'
            content = content.format(message.author.mention, message.channel.mention, message.jump_url)
            await backup_channel.send(content = content, file = file_)

  await client.process_commands(message)


@client.event
async def on_reaction_add(reaction, user):
  if reaction.emoji == emoji and reaction.count > 20:
    users = await reaction.users().flatten()
    if client.user in users:
      message = reaction.message
      await message.remove_reaction(emoji, client.user)
      if message.attachments:
        for f in message.attachments:
            pass
            # file_ = await f.to_file(spoiler=False)
        for highlight_channel in highlight_channel_list:
          content = '{0}\n{1}\n{2}'
          content = content.format(message.author.mention, message.channel.mention, message.jump_url)
          # await highlight_channel.send(content = content, file = file_)
      

server.server()
client.run(TOKEN)
