from replit import db
from random import randint

polls = {}

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
	del db[str(guild_id)]
	
	return y, n
