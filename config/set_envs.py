#!/usr/bin/python
import sys
import json
import os

envBuffer=128
def envLoad(operation=1,envSetting=None):
    if operation == 1:
        with open('./env_settings_tmp.json','r',envBuffer) as envfile:
            envData=envfile.read()
        env_setting=json.loads(envData)
        return env_setting
    elif operation == 2:
        env_setting=envSetting
        with open('./env_settings_tmp.json','w',envBuffer) as envfile:
            json.dump(env_setting,envfile)
        return(0)

env_set=envLoad()
# 1:hostname
# 2:history
# 3:enable username and password
# 4:set session timeout

	

if int(sys.argv[1])==1:
	if sys.argv[2]:
		argvLen=len(sys.argv[2])
		if argvLen <= 32:
			env_set['hostname']=sys.argv[2]
			envLoad(2,env_set)
		else:
			sys.stderr.write(" * Accept maximum hostname length is 32\n")
			
elif int(sys.argv[1])==2:
	if sys.argv[2]:
		num=int(sys.argv[2])
		if num<= 20 and num>0:
			env_set['historyItems']=num
			envLoad(2,env_set)
		else:
			sys.stderr.write(" * Only accept number,range at <1-20>\n")

elif int(sys.argv[1])==3:
	if sys.argv[2] and sys.argv[3]:
		userLen=len(sys.argv[2])
		passLen=len(sys.argv[3])
		if (userLen <= 32 and userLen>=4) and (passLen<=32 and passLen>=4):
			env_set['enUsername']=sys.argv[2]
			env_set['enPassword']=sys.argv[3]
			envLoad(2,env_set)
		else:
			sys.stderr.write(" * Username and Password minmun length is 4 and maximum length is 32\n")
elif int(sys.argv[1])==4:
	if sys.argv[2]:
		num=int(sys.argv[2])
		if num<= 60 and num>0:
			num=num*60
			env_set['historyItems']=num
			envLoad(2,env_set)
		else:
			sys.stderr.write(" * Only accept number,range at <1-60> minutes\n")


#n_k = o_k = termios.tcgetattr(sys.stdin.fileno())
#n_k[3] = n_k[3] | ~termios.ECHO 
#termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
#hostname=raw_input('hostname:')

#n_k[3] = n_k[3] & ~(termios.ECHO | termios.ICANON)
#termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
#Password=raw_input('Password:')
#if Username and Password:
#	env_set['hostname'
#	main.envLoad(2
