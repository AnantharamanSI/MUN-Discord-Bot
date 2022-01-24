from replit import db
from random import randint

polls = {}

def poll_create(msgid, content):
	current_poll = randint(100, 999)

	poll = {'y':0, 'n':0}
	poll['content'] = content
	polls[str(current_poll)] = poll

	db[current_poll] = msgid

	return current_poll

def poll_result(pid, result):
	y = result['👍']-1
	n = result['👎']-1
	polls[pid]['y'] = y
	polls[pid]['n'] = n
	del db[pid]
	
	return y, n
