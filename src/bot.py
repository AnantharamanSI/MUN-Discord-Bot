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

# intents = discord.Intents.default()
# intents.members = True

#load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

bot = commands.Bot(command_prefix='mun ')
bot.remove_command('help')

# DiscordComponents(bot)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="the United Nations"))

    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_connect():
  print('Bot Connected: '+str(client))

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
        ch = await server.create_text_channel(channel, category = category)
        overwrite = ch.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ch.set_permissions(ctx.guild.default_role, overwrite=overwrite)


      

    # client.
    # channel = await guild.create_text_channel('cool-channel')

# @bot.event
# async def getVC():
	
# @bot.command(name='getvc')
# async def getvc(ctx):
# 	for guild in bot.guilds:
# 		print(guild)
# 		for channel in guild.voice_channels:
# 			print(channel.members)
# 			for member in channel.members:
# 				print(member)

@bot.event
async def on_button_click(interaction):
	await interaction.respond(content=f"you clicked button {interaction.component.custom_id}")

@bot.command(name='say')
async def repeat(ctx, *, arg):
    await ctx.send(arg)

# @bot.command(name='btn')
# async def button(ctx):
# 	await ctx.send(content="Message Here", components=[Button(style=ButtonStyle.URL, label="Example Invite Button", url="https://google.com"), Button(style=ButtonStyle.blue, label="Default Button", custom_id="button")])

@bot.command(name='poll-start')
async def poll_start(ctx, *, text):	
	message = await ctx.send(f"**Poll Started**\n`{text}`")
	for emoji in ('👍', '👎'):
		await message.add_reaction(emoji)
	
	pid = chair.poll_create(message.id, text)
	message = await ctx.fetch_message(message.id)
	await message.edit(content=f"**Poll Started**\n`{text}`\nPoll Id: {str(pid)}")

	# buttons = [Button(label="button 1", custom_id="1"), Button(label="button 2", custom_id="2"), Button(label="button 3", custom_id="3")]

	# await ctx.send("test", components=buttons)
	# await ctx.send("test")

@bot.command(name='btn')
async def btn(ctx):
	button = discord.ui.Button(label="Yes")
	view = discord.ui.View()
	view.add_item(button)

	m = discord.utils.get(ctx.message.guild.channels, name='poll-logs')

	await m.send("yikes")

	await ctx.send("test", view=view)


@bot.command(name='poll-end')
async def poll_stop(ctx, pid):	
	try:
		id = db[pid]
		
		msg = await ctx.fetch_message(int(id))

		y, n = chair.poll_result(pid, {react.emoji: react.count for react in msg.reactions})

		for r in msg.reactions: await msg.clear_reaction(r)
		
		await msg.edit(content=f"{msg.content}\n------------\n**Poll Ended.**\nResults: `Yes: {y}  No: {n}`")

		res = discord.utils.get(ctx.message.guild.channels, name='poll-logs')

		await res.send(content=f"{msg.content}\n------------\n**Poll Ended.**\nResults: `Yes: {y}  No: {n}`")

		
		# await ctx.send("**Poll Ended**")

	except KeyError:
		await ctx.send("Error: You have entered the incorrect Poll Id!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
	    await ctx.send("This is not a command")
	    return
    raise error

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


@bot.command(name="add-chair")
@commands.has_role("admin")
async def add_chair(ctx):
    member = ctx.message.author
    message = await ctx.send(f"`{member}`has been made a **Chair**")
    role = discord.utils.get(ctx.message.guild.roles, name="Chair")
    await member.add_roles(role)

# @bot.event 
# async def on_member_join(member):
#   role = get(member.guild.roles, name="Delegate")
#   await member.add_roles(role)


bot.run(TOKEN)
