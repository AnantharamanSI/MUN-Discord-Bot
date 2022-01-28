import os

import discord
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound, MissingRequiredArgument, MissingRole, MissingPermissions, BadArgument

import chair
from replit import db

import aiohttp
import discord
import datetime
import warnings

intents = discord.Intents.all()
# intents.members = True

#load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

bot = commands.Bot(command_prefix='mun ', intents=intents)
bot.remove_command('help')

warnings.filterwarnings("ignore", category=DeprecationWarning)
bot.session = aiohttp.ClientSession()


# DiscordComponents(bot)
"""
@bot.command(name="add-chair")
@commands.has_role("admin")
async def add_chair(ctx):
    member = ctx.message.author
    message = await ctx.send(f"`{member}` has been made a **Chair**")
    role = discord.utils.get(ctx.message.guild.roles, name="Chair")
    await member.add_roles(role)
"""
@bot.event
async def on_connect():
	print('Bot Connected: '+str(client))

@bot.event
async def on_ready():
  #Bot Watching Status
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the United Nations"))
  print(f'{bot.user} has connected to Discord!')

  db["del_msg_id"] = ""
  db["voting_msg_id"] = ""
  db["hand_msg_id"] = ""


  #Create channels
  req = { "Bot Channels":["announcements","poll-log","roles"], "Bloc Channels":["bloc-announcements"] }
  categories_req = set(list(req.keys()))
  for server in bot.guilds:
    categories_dict = {c.name:c for c in server.categories}
    categories_present = set(categories_dict.keys())
    categories_to_make = categories_req.difference(categories_present)
    for category_name in categories_to_make:
      category = await create_category(server,category_name)
      categories_dict[category_name] = category
    for category_name in req.keys():
      category = categories_dict.get(category_name)
      channels_req = req.get(category.name,[])
      channels_req = set([c.lower() for c in channels_req])
      channels_present = set([c.name for c in category.channels])
      channels_to_make = channels_req.difference(channels_present)
      for channel_name in channels_to_make:
        await create_channel(server, category, channel_name)
        
  #Reaction roles
  
async def create_channel(server, category, name):
  bot_role = discord.utils.get(server.roles, name="Omkar")
  overwrite = {
			server.default_role: discord.PermissionOverwrite(send_messages=False),
			bot_role: discord.PermissionOverwrite(send_messages=True),
      }
  ch = await server.create_text_channel(name, overwrites = overwrite, category = category)
  return ch


async def create_category(server, name):
  category = discord.utils.get(server.categories, name=name)
  if category is None:
    await server.create_category(name)
    category = discord.utils.get(server.categories, name=name)
  return category

@bot.command(name="startup")
async def startup(ctx):
	guild = ctx.guild
	if type(discord.utils.get(ctx.guild.roles, name="Chair")) is type(None):
		await guild.create_role(name="Chair", colour=discord.Colour(0x57F287))
	if type(discord.utils.get(ctx.guild.roles, name="Delegate")) is type(None):
		await guild.create_role(name="Delegate", colour=discord.Colour(0xFEE75C))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
	    await ctx.send("This is not a command.\nSee `mun help` for available commands.")
	    return
    if isinstance(error, MissingRequiredArgument):
	    await ctx.send("Missing arguments in command.\nSee `mun help` for required arguments.")
	    return
    if isinstance(error, MissingRole):
	    await ctx.send("Only Chairs can use commands.")
	    return
    if isinstance(error, MissingPermissions):
	    await ctx.send("Some permissions are missing.")
	    return
    if isinstance(error, BadArgument):
        await ctx.send("Arguments in command are of the incorrect type.\nSee `mun help` for appropriate arguments.")
        return
    
    raise error

@bot.event
async def on_member_join(member):
  role = discord.utils.get(member.guild.roles, name="Delegate")
  await member.add_roles(role)

# @bot.command(name='members')
# async def on_message(ctx):
#     i=[]
#     for guild in bot.guilds:
#       for a in guild.members:
#         i+=a
#     print(i)
#     message = await ctx.send(i)
    # await member.add_roles(role)

    # role = discord.utils.get(member.guild.roles, name="Delegate")
    # await member.add_roles(role)

@bot.command(name='create-bloc')
async def test_bloc(ctx, *, text):
  member = ctx.message.author
  bloc_name = text
  
  chair_role = discord.utils.get(ctx.message.guild.roles, name='Chair')
  category = discord.utils.get(ctx.message.guild.categories, name='Bloc Channels')
  bot_role = discord.utils.get(ctx.message.guild.roles, name='Omkar')

  overwrite = {
    ctx.message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
 	  member: discord.PermissionOverwrite(read_messages=True,send_messages=True),
    chair_role: discord.PermissionOverwrite(read_messages=True),
    bot_role: discord.PermissionOverwrite(read_messages=True,send_messages=True)}
    
  ch = await ctx.message.guild.create_text_channel(bloc_name, overwrites = overwrite, category = category)
  vc = await ctx.message.guild.create_voice_channel(bloc_name, category = category, overwrites = overwrite)

  channel = discord.utils.get(ctx.message.guild.channels, name = 'bloc-announcements')
  msg = await channel.send(str(member) + " has created the " + str(bloc_name) + ".")
  
  pwd = chair.bloc_create(bloc_name)
  msg2 = await ch.send("The password is " + str(pwd))
  await msg2.pin()
  

@bot.command(name="join-bloc")
async def join_bloc(ctx, bloc_name, pwd):
  member = ctx.message.author
  # print(bloc_name, pwd)
  if bloc_name not in chair.blocs:
      await ctx.send("This bloc doesn't exist yet.")
      return
#   print(chair.blocs[bloc_name])
  if chair.blocs[bloc_name] == int(pwd):
    #print("PWD is correct")
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = True
    overwrite.read_messages = True
    channel = discord.utils.get(ctx.message.guild.channels, name = bloc_name)
    await channel.set_permissions(member, overwrite=overwrite)
    
    overwrite.stream = True
    overwrite.view_channel = True
    vchannel = discord.utils.get(ctx.guild.voice_channels, name = bloc_name)
    # vc_list = ctx.guild.voice_channels
    # print(vc_list)
    await vchannel.set_permissions(member, overwrite=overwrite)
  else:
    await ctx.send("The password is incorrect.")
        
@commands.has_role("Chair")
@bot.command(name='mute')
async def vcmute(ctx):
    vc = ctx.author.voice.channel
    role = discord.utils.get(ctx.message.guild.roles, name='Chair')
    for member in vc.members:
      if role not in member.roles:
        await member.edit(mute=True)
        
@commands.has_role("Chair")
@bot.command(name='unmute')
async def vcunmute(ctx):
    vc = ctx.author.voice.channel
    role = discord.utils.get(ctx.message.guild.roles, name='Chair')
    for member in vc.members:
      if role not in member.roles:
        await member.edit(mute=False)

@bot.event
async def on_reaction_add(reaction, user):
    cc = db["voting_msg_id"]
    dc = db["del_msg_id"]
    hr = db["hand_msg_id"]
    if reaction.message.id == cc:
        msg = reaction.message
        if user.display_name in msg.content or user.display_name == bot.user.name:
            return
        if reaction.emoji not in ('🗳️','☑️'):
            return
            
        s = msg.content
        s = f"{s[:-3]}\n{user.display_name} - {reaction.emoji} ```"
        await msg.edit(content=f"{s}")

    elif reaction.message.id == dc:
        role = discord.utils.get(user.guild.roles, name="Delegate")
        await user.add_roles(role)
    
    elif reaction.message.id == hr:
        msg = reaction.message
        if user.display_name in msg.content or user.display_name == bot.user.name:
            return
        if reaction.emoji != '🤚':
            return
        s = msg.content
        s = f"{s[:-3]}\n{user.display_name} ```"
        await msg.edit(content=f"{s}")
        
    return

@bot.event
async def on_reaction_remove(reaction, user):

    cc = db["voting_msg_id"]
    hr = db["hand_msg_id"]
    if reaction.message.id == cc:
        msg = reaction.message
        if user.display_name not in msg.content:
	        return

        s = msg.content
        ind = s.index(user.display_name)

        s = s[:ind-1]+s[ind + len(user.display_name)+4:]

        await msg.edit(content=f"{s}")


    elif reaction.message.id == hr:
        msg = reaction.message
        if user.display_name not in msg.content:
            return
        s = msg.content
        ind = s.index(user.display_name)

        s = s[:ind-1]+s[ind + len(user.display_name):]
        await msg.edit(content=f"{s}")

    return

@commands.has_role("Chair")
@bot.command(name='say')
async def repeat(ctx, *, arg):
    await ctx.send(arg)

@commands.has_role("Chair")
@bot.command(name='raise-hand')
async def raise_hand(ctx):
    c = discord.utils.get(ctx.message.guild.channels, name='announcements')
    msg = await c.send("Click the reaction to raise your hand.\n```Raised Hands:```")
    await msg.add_reaction('🤚')

    db["hand_msg_id"] = msg.id

###################################
async def timeout_user(*, user_id: int, guild_id: int, until):
    headers = {"Authorization": f"Bot {bot.http.token}"}
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    async with bot.session.patch(url, json=json, headers=headers) as session:
        if session.status in range(200, 299):
           return True
        return False

@commands.has_role("Chair")
@bot.command(name='gag')
async def gag(ctx: commands.Context, member: discord.Member, until: int):
    if until > 60:
        await ctx.send("Max. gag limit is 60 minutes.")
        return
    handshake = await timeout_user(user_id=member.id, guild_id=ctx.guild.id, until=until)
    # print(handshake)
    if handshake:
         return await ctx.send(f"Successfully timed out user for {until} minutes.")
    await ctx.send("Gag a delegate and not your colleagues.")

###################################

@commands.has_role("Chair")
@bot.command(name='set-del')
async def set_del(ctx):
    c = discord.utils.get(ctx.message.guild.channels, name='roles')
    msg = await c.send("Click the reaction to set yourself as delegate.")
    await msg.add_reaction('✅')
    # await msg.pin()

    db["del_msg_id"] = msg.id

@commands.has_role("Chair")	
@bot.command(name='voting-stance')
async def voting_stance(ctx):	
	c = discord.utils.get(ctx.message.guild.channels, name='announcements')
	msg = await c.send("Voting Stance\n```Delegates:```")

	for emoji in ('🗳️','☑️'):
		await msg.add_reaction(emoji)

	await c.send("`Voting` `Present`")

	db["voting_msg_id"]	= msg.id
	print(db["voting_msg_id"])

@commands.has_role("Chair")
@bot.command(name='voting-end')
async def voting_end(ctx):	

	c = discord.utils.get(ctx.message.guild.channels, name='announcements')
	id = db["voting_msg_id"]
	msg = await c.fetch_message(int(id))
	
	for r in msg.reactions: await msg.clear_reaction(r)

# db["voting_msg_id"] = 

@commands.has_role("Chair")
@bot.command(name='poll')
async def poll_start(ctx, *, text):	

	c = discord.utils.get(ctx.message.guild.channels, name='announcements')

	message = await c.send(f"**Poll**\n`{text}`")
	for emoji in ('👍', '👎'):
		await message.add_reaction(emoji)
	
	# pid = chair.poll_create(message.id, text)
	guild_id = ctx.message.guild.id
	chair.poll_create(message.id, text, guild_id)

@commands.has_role("Chair")
@bot.command(name='poll-end')
async def poll_stop(ctx):	
	try:
		c = discord.utils.get(ctx.message.guild.channels, name='announcements')

		guild_id = ctx.message.guild.id
		id = db[str(guild_id)]
		msg = await c.fetch_message(int(id))

		y, n = chair.poll_result(guild_id, {react.emoji: react.count for react in msg.reactions})

		voters = ""
		for r in msg.reactions:
			if r.emoji in ('👍', '👎'):
				async for user in r.users():
					dn = ctx.guild.get_member(user.id)
					if dn.name != bot.user.name:
						voters += str(dn.display_name)+" - "+str(r.emoji)+"\n"
			
		# for r in msg.reactions: await msg.clear_reaction(r)
		
		await msg.edit(content=f"{msg.content}\n------------\n> **Results:** Yes: *{y}*  No: *{n}*")

		res = discord.utils.get(ctx.message.guild.channels, name='poll-log')

		await res.send(content=f"{msg.content}\n```{voters}```")

		await msg.delete()

	except KeyError:
		await ctx.send("Error: Backend has messed up")


@commands.has_role("Chair")
@bot.command(pass_content=True)
async def help(ctx):
    # if prefixTable.find({"_id":ctx.guild.id}).count() > 0:
    #     preftag=prefixTable.find_one({"_id":ctx.guild.id})
    #     p=preftag.get("prefix")
    p = 'mun '

    embedVar = discord.Embed(title="MUN Help",
                             description="List of commands.",
                             color=discord.Color.from_rgb(78, 134, 219))

    embedVar.set_thumbnail(
        url=
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/UN_flag.png/1024px-UN_flag.png"
    )

    embedVar.add_field(name="Current Prefix",
                       value="Current prefix is set to: " + p,
                       inline=False)

    # embedVar.add_field(name=p + "prefix [new prefix]",
    #                    value="Change the bot's prefix (Chairs only).",
    #                    inline=True)

    embedVar.add_field(
        name="Chair Commands",
        value="These commands can only be used by the Chair role.",
        inline=False)

    embedVar.add_field(
        name=p + "startSession",
        value=
        "Enables all commands for a session and invites bot to voice channel.",
        inline=True)

    embedVar.add_field(
        name=p + "register [delegate] [status]",
        value="Status can be present (p),present and voting(pv) or absent (a)",
        inline=True)

    embedVar.add_field(name=p + "resume",
                       value="Resume a paused caucus.",
                       inline=True)

    embedVar.add_field(name="Delegate Commands",
                       value="These commands can be used by anyone.",
                       inline=False)

    embedVar.add_field(name=p + "addGS",
                       value="Adds your name to the general speakers list.",
                       inline=True)

    embedVar2 = discord.Embed(title="Support Omkar",
                              description="Useful links for using Omkar.",
                              color=discord.Color.from_rgb(78, 134, 219))
    # embedVar2.add_field(name="Invite", value="[Add me!](https://discord.com/oauth2/authorize?client_id=767330479757197323&permissions=0&scope=bot)", inline=True)
    # embedVar2.add_field(name="Support Server", value='[Join!](https://discord.gg/94ShKfuqrk)', inline=True)
    # embedVar2.add_field(name="Vote", value='[Rate me!](https://top.gg/bot/767330479757197323/vote)', inline=True)
    embedVar2.add_field(
        name="Source Code",
        value='[View!](https://replit.com/@Anantharaman_SS/MUN-Bot#src/bot.py)',
        inline=True)

    await ctx.channel.send(embed=embedVar)
    await ctx.channel.send(embed=embedVar2)

bot.run(TOKEN)