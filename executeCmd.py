import json
import sys
import subprocess
import termios

#error define
class MyException(Exception):
    def __init__(self, error, reason=None, caretMove=None):
        self.error=error
        self.reason=reason
        self.caret=caretMove
        super(MyException,self).__init__(error)

AMError=0
INError=1
WRError=2

# spaces define
ADMIN=0
ENABLE=1
CONFIG=2
DEBUG=3
tabspaces='       '

def spaceCheck(space):
	buffersize=2048
	if space==ADMIN: #0
		with open('admin_menu.json','r',buffersize) as menufile:
			menudata=menufile.read()
			menu=json.loads(menudata)
	elif space==ENABLE: #1
		with open('enabl_menu.json','r',buffersize) as menufile:
			menudata=menufile.read()
			menu=json.loads(menudata)
	elif space==CONFIG: #2
		with open('confi_menu.json','r',buffersize) as menufile:
			menudata=menufile.read()
			menu=json.loads(menudata)
	elif space==DEBUG: #3
		with open('debug_menu.json','r',buffersize) as menufile:
			menudata=menufile.read()
			menu=json.loads(menudata)
	return menu

# get char
def getchar(descr):
	sys.stdout.write(descr)
	rawInput=raw_input()
	#yesORno=sys.stdin.read(1)
	if rawInput=='terminal':
		return 0
	return 1

def execute(space,cmd,prompLen):
	confchan=0
	itemSpace=space
	argString=''
	pipeString=''
	pipeModifier=''
	cmdList=cmd.split()
	cmdListIndex=0
	cmdListLen=len(cmdList)
	prompLen=int(prompLen)
	
	if not cmdList:
		caretMove=prompLen+len(cmd)
		sys.stdout.write(''.join(['\n',' '*caretMove,'^','\n * "',cmd,'"  Unidentified input detect at above position of marker "^".\n']))
		return space,confchan
	try:
		menu=spaceCheck(space)
	except ValueError as reason:
		sys.stdout.write(' '.join(['\n  *  Fatal error:"',str(reason),'",please contact official supporter and report this, thanks!\n']))	
		return space,confchan
	while True:
		cmdLen=len(cmdList[cmdListIndex])
		ambNum=0
		try:
			for ambItem in menu:
				if cmdList[cmdListIndex]==ambItem['name'][:cmdLen]:
					ambNum+=1	
			if ambNum>1:
				ambComds=' '.join(cmdList[:cmdListIndex+1])
				raise MyException(AMError,ambComds)
			for index,item in enumerate(menu):
				if cmdList[cmdListIndex]==item['name'][:cmdLen]:
					if cmdListIndex+1<cmdListLen:
						if item['sub']==1:
							cmdListIndex+=1
							if cmdListLen==cmdListIndex and item['exe']==0:
								inComds=' '.join(cmdList)
								raise MyException(INError,inComds)
							menu=item[item['name']]
							break

					#if item['sub']==1 and item['exe']==0 and cmdListIndex+1<cmdListLen:
					#	cmdListIndex+=1
					#	#if cmdListLen==cmdListIndex:
					#	#	inComds=' '.join(cmdList)
					#	#	raise MyException(INError,inComds)
					#	menu=item[item['name']]
					#	break
					if item['exe']==1:
						#if item['space']:
						#	itemSpace=item['space']
						confchan=item['env']
						pipeList=cmd.split('|',1)
						pipeListLen=len(pipeList)
						if item['pipe']==1:
							if pipeListLen>1:
								pipeArgList=pipeList[1].split()
								pipeArgListLen=len(pipeArgList)
								if pipeArgListLen==0:
									inComds=' '.join(cmdList)
									raise MyException(INError,inComds)
								else:
									pipeModifier=pipeArgList[0]
									pipeModifierLen=len(pipeArgList[0])
									if pipeModifier=='include'[:pipeModifierLen]:
										pipeModifier='| egrep '
										pipeArgs=' '.join(pipeArgList[1:])
										pipeString=' '.join([pipeModifier,pipeArgs])
										if pipeArgListLen==1:
											inComds=' '.join(cmdList)
											raise MyException(INError,inComds)
									elif pipeModifier== 'exclude'[:pipeModifierLen]:
										pipeModifier='| egrep -v '
										pipeArgs=' '.join(pipeArgList[1:])
										pipeString=' '.join([pipeModifier,pipeArgs])
										if pipeArgListLen==1:
											inComds=' '.join(cmdList)
											raise MyException(INError,inComds)
									elif pipeModifier== 'count'[:pipeModifierLen]:
										pipeModifier='| egrep -c '
										pipeArgs=' '.join(pipeArgList[1:])
										pipeString=' '.join([pipeModifier,pipeArgs])
										if pipeArgListLen==1:
											inComds=' '.join(cmdList)
											raise MyException(INError,inComds)
									else:
										caretMove=prompLen+len(pipeList[0])+len(pipeList[1].split(pipeModifier,1)[0])+1
										raise MyException(WRError,pipeModifier,caretMove)
						else:
							if pipeListLen>1:
								caretMove=cmd.index('|')+prompLen
								raise MyException(WRError,'|',caretMove)
							
						if item['args']>=1:
							cmdArgListLen=cmdListIndex+1+item['args']
							if pipeListLen==1:
								if cmdArgListLen==cmdListLen:
									argString=' '.join(cmdList[cmdListIndex+1:])
								elif cmdArgListLen<cmdListLen:
									caretMove=prompLen+cmd.index(cmdList[cmdArgListLen])
									raise MyException(WRError,cmdList[cmdListIndex+item['args']+1],caretMove)
								else:
									inComds=' '.join(cmdList)
									raise MyException(INError,inComds)
							else:
								#print cmdArgListLen,cmdListLen-1-pipeArgListLen
								pipeCmd=pipeList[0].split()
								if cmdArgListLen==cmdListLen-1-pipeArgListLen:
									argString=' '.join(pipeCmd[cmdListIndex+1:])
								elif cmdArgListLen<cmdListLen-1-pipeArgListLen:
									caretMove=prompLen+cmd.index(pipeCmd[cmdArgListLen])
									raise MyException(WRError,pipeCmd[cmdListIndex+item['args']+1],caretMove)
								else:
									inComds=' '.join(pipeCmd)
									raise MyException(INError,inComds)
						#elif item['args']==0:
						else:
							#if item['pipe']==0:
							if pipeListLen==1:
								if cmdListIndex+1<cmdListLen:
									caretMove=prompLen+cmd.rindex(cmdList[cmdListIndex+1])
									raise MyException(WRError,cmdList[cmdListIndex+1],caretMove)
							else:
								if cmdListIndex+1<cmdListLen-pipeListLen-1:
									caretMove=prompLen+cmd.rindex(cmdList[cmdListIndex+1])
									raise MyException(WRError,cmdList[cmdListIndex+1],caretMove)

						if item['getchar']==1 and item['exe']==1:		
							if cmdListIndex==cmdListLen-1:
								inputAuthPromp=''.join(['\n',item['promp']])
								n_k = o_k = termios.tcgetattr(sys.stdin.fileno())
								n_k[3] = n_k[3]|(termios.ECHO|termios.ICANON)
								termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
								inputAuth=raw_input(inputAuthPromp)
								n_k[3] = n_k[3]&~(termios.ECHO | termios.ICANON)
								termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
								if inputAuth==0:
									return space,confchan
								space=item['space']
							elif cmdListIndex<cmdListLen-1:
								caretMove=prompLen+cmd.index(cmdList[cmdListIndex+1])
								raise MyException(WRError,cmdList[cmdListIndex+item['args']+1],caretMove)
								
								

						space=item['space']
						if item['process']==0:
							processString=' '.join([item['cmd'],argString,pipeString])
							n_k = o_k = termios.tcgetattr(sys.stdin.fileno())
							n_k[3] = n_k[3]|(termios.ECHO|termios.ICANON)
							termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
							sys.stdout.write('\n')
							process=subprocess.Popen(processString,shell=True)

							if processString:
								try:
									process.wait()
									n_k[3] = n_k[3]&~(termios.ECHO | termios.ICANON)
									termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
								except KeyboardInterrupt:
									process.terminate()
									process.kill()
							n_k[3] = n_k[3]&~(termios.ECHO | termios.ICANON)
							termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
						else:
							eval(item['cmd'])	
						return space,confchan
					else:
						if item['sub']==1:
							inComds=' '.join(cmdList)
							raise MyException(INError,inComds)
						else:
							sys.stdout.write('fatal error!')
							return space
							
				elif index==len(menu)-1:
					caretMove=prompLen+len(cmd.split(cmdList[cmdListIndex],1)[0])
					raise MyException(WRError,cmdList[cmdListIndex],caretMove)
		except IndexError as reason:
			return space,confchan
		except MyException as errors:
			if errors.error==0:
				sys.stdout.write(''.join(['\n * Ambiguous command, use "',errors.reason,'?" for help.\n\n']))
			elif errors.error==1:
				sys.stdout.write(''.join(['\n * Incomplete command, use "',errors.reason,' ?" for help.\n\n']))
			elif errors.error==2:
				sys.stdout.write(''.join(['\n',' '*errors.caret,'^','\n * "',errors.reason,'"  Unidentified input detect at above position of marker "^".\n\n']))
			return space,confchan
	return space,confchan




def tabKey(space,cmd,row,prompLen,cursor):
	oriCmd=cmd
	cmdRemain=cmd[cursor:]
	cmd=cmd[:cursor]
	cmdList=cmd.split()
	cmdListIndex=0
	cmdListLen=len(cmdList)

	try:
		menu=spaceCheck(space)
	except ValueError as reason:
		sys.stdout.write(' '.join(['\n  *  Fatal error:"',str(reason),'",please contact official supporter and report this, thanks!\n']))	
		return oriCmd,None,None,cursor

	if not cmdList:
		noCmdHints=''
		cmdFill=''
		for noCmdItem in menu:
			noCmdHints=''.join([noCmdHints,noCmdItem['name'],tabspaces])
		return oriCmd,noCmdHints,cmdFill,cursor
	#confchan=0
	whitespace=cmd[-1].isspace()
	itemSpace=space
	argString=''
	pipeString=''
	pipeModifier=''
	line=cmd
	
	while True:
		cmdFill=''
		#print cmdList,cmdListIndex,cmdListLen
		cmdLen=len(cmdList[cmdListIndex])
		pipeList=cmd.split('|',1)
		pipeListLen=len(pipeList)
		ambNum=0
		cmdHint=''
		ambList=[]
		cmdFill=''
		for ambItems in menu:
			if cmdList[cmdListIndex]==ambItems['name'][:cmdLen]:
				ambNum+=1
				ambList.append(ambItems['name'])
		for index,item in enumerate(menu):
			if cmdList[cmdListIndex]==item['name'][:cmdLen]:
					if ambNum==1:
						if cmdListIndex+1==cmdListLen:
							if whitespace:
								for hintItems in item[item['name']]:
									cmdHint=''.join([cmdHint,hintItems['name'],tabspaces])
							elif not whitespace:
								cmdFill=''.join([item['name'][cmdLen:],' '])
								line=''.join([cmd,cmdFill,cmdRemain])
								cursor=cursor+len(cmdFill)
						elif cmdListIndex+1<cmdListLen:
							if item['sub']==1:
								menu=item[item['name']]
								cmdListIndex+=1
								break
							elif item['pipe']==1 and pipeListLen>1:
								menu=pipeTabMenus
								if item['args']==0:
									cmdListIndex+=1
									break
								else:
									cmdListIndex=cmdListIndex+item['args']+1
									break
						return line,cmdHint,cmdFill,cursor
					elif ambNum>1:
						if cmdListIndex+1==cmdListLen:
							for hintItems in ambList:
								cmdHint=''.join([cmdHint,hintItems,tabspaces])
						return oriCmd,cmdHint,cmdFill,cursor
			elif index==len(menu)-1:
				return oriCmd,cmdHint,cmdFill,cursor
	

def QuestionKey(space,cmd,row):
	cmdList=cmd.split()
	cmdListIndex=0
	cmdListLen=len(cmdList)
	hintLineNum=0
	try:
		menu=spaceCheck(space)
	except ValueError as reason:
		sys.stdout.write(' '.join(['\n  *  Fatal error:"',str(reason),'",please contact official supporter and report this, thanks!\n']))	
		return cmd,cursor
	if not cmdList:
		noCmdHints=''
		cmdFill=''
		for noCmdItem in menu:
			helps=noCmdItem['descr'].split('=')
			sys.stdout.write("%-20s %s\n" % tuple(noCmdItem['descr'].split('=')))
			hintLineNum+=1
			#print hintLineNum,row
			if hintLineNum>row-3:
				hintLineNum=0
				sys.stdout.write('--more--\n')
				ch=sys.stdin.read(1)
				if ch=='q':
					break
				continue
		return 0
	whitespace=cmd[-1].isspace()
	itemSpace=space
	line=cmd
	while True:
		cmdFill=''
		cmdLen=len(cmdList[cmdListIndex])
		pipeList=cmd.split('|',1)
		pipeListLen=len(pipeList)
		ambNum=0
		cmdHint=''
		ambList=[]
		hintLineNum=0
		multiArgs=0
		for ambItems in menu:
			if cmdList[cmdListIndex]==ambItems['name'][:cmdLen]:
				ambNum+=1
				ambList.append(ambItems['name'])
		for index,item in enumerate(menu):
			if cmdList[cmdListIndex]==item['name'][:cmdLen]:
				if cmdListIndex==cmdListLen-1:
					if not whitespace:
						sys.stdout.write("%-20s %s\n" % tuple(item['descr'].split('=')))
					else:
						if item['sub']==1:
							
							for subItems in item[item['name']]:
								sys.stdout.write("%-20s %s\n" % tuple(subItems['descr'].split('=')))
								hintLineNum+=1
								#print rowNum,row
								if hintLineNum>row-4:
									hintLineNum=0
									sys.stdout.write(' --more--\n')
									ch=sys.stdin.read(1)
									sys.stdout.write('\033[1A\r\033[K')
									if ch=='q':
										break
									continue
						if item['exe']==1 and item['args']==0:
							sys.stdout.write("%s\n" % ('<cr>'))
						if item['pipe']==1 and item['args']==0 and pipeListLen==1:
							sys.stdout.write("%-20s %s\n" % ('|','Line selector'))
						if item['args']>=1 and multiArgs==0:
							sys.stdout.write("%-20s %s\n" % tuple(item['argDescr'].split('=')))
				else:
					if ambNum==1 and item['sub']==1:
						menu=item[item['name']]
						cmdListIndex+=1
						break
					if item['args']>=1:
						if cmdListLen-1==cmdListIndex+item['args']:
							sys.stdout.write("%s\n" % ('<cr>'))
							if item['pipe']==1 and pipeListLen==1:
								sys.stdout.write("%-20s %s\n" % ('|','Line selector'))
						elif cmdListLen-1<cmdListIndex+item['args']:
							#argNo=item['args']-(cmdListIndex+item['args']-cmdListLen+1)
							argNo=cmdListLen-cmdListIndex-1
							argNoStr=''.join(['argDescr',str(argNo)])
							sys.stdout.write("%-20s %s\n" % tuple(item[argNoStr].split('=')))
					if item['pipe']==1 and pipeListLen>1:
						menu=pipeTabMenus
						cmdListIndex+=1
						if item['args']>=1:
							cmdListIndex=cmdListIndex+item['args']
						break
				if index==len(menu)-1:
					return 0
			elif index==len(menu)-1:
				return 0


pipeTabMenus=[{"name":"|","descr":"|=Line selector","sub":1,"args":0,"exe":0,"env":0,"cmd":"","pipe":1,"space":0,"getchar":0,"promp":"","|":[{"name":"include","descr":"include=Line selector for matched","sub":0,"args":1,"argDescr":"WORD=Selected lines that contains this string","exe":0,"env":0,"cmd":"","pipe":0,"space":0,"getchar":0,"promp":"","include":""},{"name":"exclude","descr":"exclude=Line selector for unmatched","sub":0,"args":1,"argDescr":"WORD=Selected lines that not contains this string","exe":0,"env":0,"cmd":"","pipe":0,"space":0,"getchar":0,"promp":"","exclude":""},{"name":"count","descr":"count=Counter of selected lines","sub":0,"args":1,"argDescr":"WORD=count lines which contains this string","exe":0,"env":0,"cmd":"","pipe":0,"space":0,"getchar":0,"promp":"","count":""}]}]
