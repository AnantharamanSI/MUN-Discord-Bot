import os

import discord
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
# from discord.ui import Button, View
# from discord_components import DiscordComponents, Button, ButtonStyle 

import chair
from replit import db

intents = discord.Intents.default()
intents.members = True

#load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

bot = commands.Bot(command_prefix='mun ')
bot.remove_command('help')

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
async def on_ready():
	await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="the United Nations"))
	print(f'{bot.user} has connected to Discord!')



@bot.command(name="startup")
async def startup(ctx):
	guild = ctx.guild
	if type(discord.utils.get(ctx.guild.roles, name="Chair")) is type(None):
		await guild.create_role(name="Chair", colour=discord.Colour(0x57F287))
	if type(discord.utils.get(ctx.guild.roles, name="Delegate")) is type(None):
		await guild.create_role(name="Delegate", colour=discord.Colour(0xFEE75C))

@bot.event
async def on_connect():
	print('Bot Connected: '+str(client))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
	    await ctx.send("This is not a command")
	    return
    raise error
	
#@discord.member.on_member_join()
#async def add_delegate():
#  print("a")

@bot.event
async def on_member_join(ctx, member):
  role = discord.utils.get(ctx.message.guild.roles, name="Delegate")
  await member.add_roles(role)

@bot.command(name='members')
async def on_message(ctx):
    i=[]
    for guild in bot.guilds:
      for a in guild.members:
        i+=a
    print(i)
    message = await ctx.send(i)
    #await member.add_roles(role)

    #role = discord.utils.get(member.guild.roles, name="Delegate")
    #await member.add_roles(role)

@bot.command(name='test_channels')
async def well(ctx):
  channels_req =("announcements","poll-log")
  channels_req = set([c.lower() for c in channels_req])
  for server in bot.guilds:
    channels_present = set()
    for channel in server.channels:
      channels_present.add(channel.name)
    channels_to_make = channels_req.difference(channels_present)
    category = discord.utils.get(server.categories, name='Bot Channels')
    if category is None:
      await server.create_category('Bot Channels')
      category = discord.utils.get(server.categories, name='Bot Channels')
    for channel in channels_to_make:
      bot_role = discord.utils.get(user.server.roles, name="Omkar")
      overwrite = {
        server.default_role: discord.PermissionOverwrite(send_messages=False),
        bot_role: discord.PermissionOverwrite(send_messages=True)}
      ch = await server.create_text_channel(channel, overwrites = overwrite, category = category)

@bot.event
async def on_button_click(interaction):
	await interaction.respond(content=f"you clicked button {interaction.component.custom_id}")

@bot.command(name='say')
async def repeat(ctx, *, arg):
    await ctx.send(arg)
	


@bot.command(name='poll-start')
async def poll_start(ctx, *, text):	
	message = await ctx.send(f"**Poll Started**\n`{text}`")
	for emoji in ('👍', '👎'):
		await message.add_reaction(emoji)
	
	# pid = chair.poll_create(message.id, text)
	guild_id = ctx.message.guild.id
	chair.poll_create(message.id, text, guild_id)

	message = await ctx.fetch_message(message.id)
	# await message.edit(content=f"**Poll Started**\n`{text}`\nPoll Id: {str(pid)}")

	await message.edit(content=f"**Poll**\n`{text}`")


@bot.command(name='poll-end')
async def poll_stop(ctx):	
	try:
		guild_id = ctx.message.guild.id

		id = db[str(guild_id)]
		
		msg = await ctx.fetch_message(int(id))

		y, n = chair.poll_result(guild_id, {react.emoji: react.count for react in msg.reactions})


		for r in msg.reactions:
			async for user in r.users():
				dn = ctx.message.guild.get_member(user.id)
				# print(dn.display_name)
				print(dn.nick, r.emoji)
		
		for r in msg.reactions: await msg.clear_reaction(r)
		
		await msg.edit(content=f"{msg.content}\n------------\n**Results:** `Yes: {y}  No: {n}`")

		res = discord.utils.get(ctx.message.guild.channels, name='poll-log')

		await res.send(content=f"{msg.content}")

	except KeyError:
		await ctx.send("Error: Backend has messed up")


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

    embedVar.add_field(name=p + "prefix [new prefix]",
                       value="Change the bot's prefix (Chairs only).",
                       inline=True)

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





"""
@bot.command(name="add-chair")
@commands.has_role("admin")
async def add_chair(ctx, user):
	#userid = user.strip("<>@!")
	u = ctx.message.guild.get_member(user)
	message = await ctx.send(f"`{u}` has been made a **Chair**")
	role = discord.utils.get(ctx.message.guild.roles, name="Chair")
	await u.add_roles(role)

@bot.command(name="role")
@commands.has_permissions(administrator=True) #permissions
async def role(ctx, user : discord.Member, *, role : discord.Role):
  if role.position > ctx.author.top_role.position: #if the role is above users top role it sends error
    return await ctx.send('**:x: | That role is above your top role!**') 
  if role in user.roles:
      await user.remove_roles(role) #removes the role if user already has
      await ctx.send(f"Removed {role} from {user.mention}")
  else:
      await user.add_roles(role) #adds role if not already has it
      await ctx.send(f"Added {role} to {user.mention}") 


@bot.event 
async def on_member_join(member):
  role = discord.utils.get(member.guild.roles, name="Delegate")
  await member.add_roles(role)
"""

bot.run(TOKEN)
