from replit import db
from random import randint

polls = {}
blocs = {}

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
