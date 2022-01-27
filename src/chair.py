from replit import db
from random import randint

polls = {}
blocs = {}

# def poll_create(msgid, content):
# 	current_poll = randint(100, 999)

# 	poll = {'y':0, 'n':0}
# 	poll['content'] = content
# 	polls[str(current_poll)] = poll

# 	db[current_poll] = msgid

# 	return current_poll

def poll_create(msgid, content, guild_id):

	poll = {'y':0, 'n':0}
	poll['content'] = content
	polls[guild_id] = poll

	db[str(guild_id)] = msgid

	print(polls)

def poll_result(guild_id, result):
	y = result['👍']-1
	n = result['👎']-1
	polls[guild_id]['y'] = y
	polls[guild_id]['n'] = n
	# del db[str(guild_id)]
	
	return y, n


def bloc_create(channel_name):
    pwd = randint(100, 999)
    while pwd in blocs.keys():
        pwd = randint(100, 999)
    blocs[channel_name] = pwd

    return pwd


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
