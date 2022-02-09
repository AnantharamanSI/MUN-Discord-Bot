from replit import db
from random import randint

polls = {}
blocs = {}


"""
Instantiates new poll (yes/no key-value pairs) in polls. Stores poll message-id in replit database.
"""
def poll_create(msgid, content, guild_id):

	poll = {'y':0, 'n':0}
	poll['content'] = content
	polls[guild_id] = poll

	db[str(guild_id)] = msgid

	print(polls)


"""
Updates poll (yes/no key-value pairs) in polls with the results from the reactions dictionary passed from poll_stop.
"""
def poll_result(guild_id, result):

	y = result['👍']-1
	n = result['👎']-1
	polls[guild_id]['y'] = y
	polls[guild_id]['n'] = n
	# del db[str(guild_id)]
	
	return y, n


"""
Creates a unique random number between 100 and 999 to serve as a password for a newly created bloc. Updates blocs to store the bloc name and password.
"""
def bloc_pwd_create(channel_name):
    
    pwd = randint(100, 999)
    while pwd in blocs.keys():
        pwd = randint(100, 999)
    blocs[channel_name] = pwd

    return pwd