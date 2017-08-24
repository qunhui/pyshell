#!/usr/bin/python
import random
import termios
import re
import signal
import sys
import tty
import json
import time
import subprocess
from executeCmd import execute
from executeCmd import tabKey
from executeCmd import QuestionKey

    
#spaces define
ADMIN=0
ENABLE=1
CONFIG=2
DEBUG=3

VIF=4



reload(sys)
sys.setdefaultencoding('utf-8')

n_k = o_k = termios.tcgetattr(sys.stdin.fileno())
n_k[3] = n_k[3] & ~(termios.ECHO | termios.ICANON)
termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)


def terminal_size():
    import fcntl, termios, struct
    th, tw, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return th,tw


#error define
class MyException(Exception):
    def __init__(self, error, reason=None):
        self.reason=reason
        self.error=error
        super(MyException,self).__init__(error)

def signalHandlerTimeout(signum, frame):
    raise MyException("timeout","Session timeout quit!")


#def signalHandlerSignalInt(signum, frame):
#    raise MyException("SignalInt","Pass!")

signal.signal(signal.SIGALRM, signalHandlerTimeout)
#signal.signal(signal.SIGINT, signalHandlerSignalInt)

def clearHistory():
    with open('history.log','w+',2) as historylog:
        historylog.write('!\n')

#read env from file
envBuffer=128
def envLoad(operation=1,ENV_FILE='./env_settings.json',envSetting=None):
    if operation == 1:
        with open(ENV_FILE,'r',envBuffer) as envfile:
            envData=envfile.read()
        env_setting=json.loads(envData)
        return env_setting 
    elif operation == 2:
        env_setting=envSetting
        with open(ENV_FILE,'w',envBuffer) as envfile:
            json.dump(env_setting,envfile)
        return(0)

env_setting=envLoad()

promp="> "
def refreshPromp():
    return str(len(env_setting['hostname'])+len(promp))

prompLen=refreshPromp()

#history log operations
history=[]
historyIndex=0
historyLen=len(history)

#jdef enterClear():
#    global cursorsFreese,cursorsMove,cursorsModify,cursors,line,lineLen,hintLines
cursors=0
line=''
lineLen=0
cursorsModify=''
cursorsMove=0
cursorsFreese=0
hintLines=0

#enterClear()
space=0
#save function

#initial values
tailSpace=0
def input():
        ch = sys.stdin.read(1)
        return ch

def signalControlZ(signum,frame):
    global space,promp,prompLen
    if space>1:
        space=1
        promp="# "
        sys.stdout.write(u'\nPress enter to return to enable space> ')
    
signal.signal(signal.SIGTSTP,signalControlZ)
#signal.signal(signal.SIGTSTP,signal.SIG_IGN)
#
#import subprocess
#welcome banner
upTime=subprocess.check_output('uptime',shell=True)
#upTime.terminate()

runVersion=''
faces=[':)', '_(._.)_', "('_')", ':]', ':3', ':>', ':o)', ':c)', ':o', ';)', '*-)', ':/', ':$', 'O:)', '0:)','(>_<)', "(';')", '(-_-)zzz', '(^_-)', '(^_^)/', '(^O^)', '(^o^)', '_(_^_)_','(._.)','^m^','>^_^<','<^!^>', '^/^', '(*^_^*)', '(^<^)', '(*^_^*)', '(^_^.)', '(*^^)v', ' !(^^)!', '(^_^)v', '(^^)v', '(~_~)',  '(-"-)']

DeviceUptime=subprocess.check_output("uptime|awk -F',' '{print $1}'",shell=True)

DeviceModel='xxxx'
DeviceVersion='20170619'
DeviceMAC='AA:BB:CC:DD:EE:FF'
DeviceCloud='Established'
DeviceNanny='Power cycle'

sys.stdout.write(''.join(['\n\n ',random.choice(faces),' Welcome to xxx !\n\n']))
sys.stdout.write('  * Document:http://www.xxx.com\n')
sys.stdout.write('  * Email:support@xxx.com\n\n')
sys.stdout.write('%-8s %-25s %-10s %s\n'%('Model:',DeviceModel,'MAC Addr:',DeviceMAC))
sys.stdout.write('%-8s %-25s %-10s %s'%('Version:',DeviceVersion,'Uptime:',DeviceUptime))
sys.stdout.write('%-8s %-25s %-10s %s\n'%('Cloud:',DeviceCloud,'Nanny:',DeviceNanny))

#
sys.stdout.write('\n')


sys.stdout.write(''.join([env_setting['hostname'],promp]))
while True:
    tHigh,tWidth=terminal_size()
    signal.alarm(env_setting['timeout'])
    lineLen=len(line)
    try:
        ch=input()
        if lineLen<=128 and ch:
            line+=ch

        if ord(ch) == 1:
            line=line[:-1]
            sys.stdout.write(''.join(['\r','\033[',prompLen,'C']))
            cursorsModify=''
            cursors=0
            cursorsFreese=0
            cursorsMove=-lineLen
        elif ord(ch) == 3:
            line=line[:-1]
            print 'control c'
        elif ord(ch) == 4:
            line=line[:-1]
            sys.stdout.write(''.join(['\n',env_setting['hostname'],promp,line]))
            cursors=lineLen
            cursorsMove=0
            cursorsModify=''
        elif ord(ch) == 5:
            line=line[:-1]
            sys.stdout.write(''.join(['\r','\033[',prompLen,'C','\033[K',line]))
            cursors=lineLen
            cursorsMove=0
            cursorsModify=''
        elif ord(ch) == 9: #tab key
            line=line[:-1]
            prompLen=refreshPromp()
            if hintLines>0:
                for eraseLine in range(hintLines):
                    sys.stdout.write(''.join(['\033[1B','\r','\033[K']))
                sys.stdout.write(''.join(['\033[',str(hintLines),'A','\033[',str(int(prompLen)+cursors+1),'C']))        
                hintLines=0
            line,hints,fills,cursor=tabKey(space,line,terminal_size,prompLen,cursors)
            cursorsModify=''
            cursorsFreese=cursor
            cursors=cursor
            if fills:
                sys.stdout.write('\r'+'\033['+prompLen+'C'+'\033[K'+line+'\b'*len(line[cursors:]))
                #sys.stdout.write(fills+remains+'\b'*len(remains))
#                print '('+fills+'|'+remains+str(len(fills))+')'
#                line=line+fills+remains
            elif hints:
                #fix input at a line when there are hints
                sys.stdout.write('\n')
                sys.stdout.write(hints)
                hintLen=len(hints)
                if hintLen>tWidth:
                    hintLines=(hintLen/tWidth)+1
                else:
                    hintLines=1
                sys.stdout.write(''.join(['\033[',str(hintLines),'A','\r','\033[',str(int(prompLen)+cursors),'C']))
            line=line.encode()
        elif ord(ch)==10: #enter key
            if hintLines>0:
                for eraseLine in range(hintLines):
                    sys.stdout.write(''.join(['\033[1B','\r','\033[K']))
                sys.stdout.write(''.join(['\033[',str(hintLines),'A','\033[',str(int(prompLen)+cursors),'C']))        
                hintLines=0
            line=re.sub(ur'[\u4e00-\u9fff\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uffef]+|(\\x1b[\[aABbcCdD])*','',unicode(line[:-1],errors='ignore'))
            #line=line[:-1]
            if line:
                reSpace,confchan=execute(space,line,prompLen)
                if reSpace!=space:
                    if reSpace==ADMIN: #0
                        space=ADMIN
                        promp='> '
                        #env_setting=envLoad(1,'env_settings_tmp.json')
                        prompLen=refreshPromp()
                    elif reSpace==ENABLE: #1
                        if space==0:
                            for seq in range(3):
                                n_k[3] = n_k[3] |(termios.ECHO|termios.ICANON)
                                termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
                                enUsername=raw_input('Username:')
                                n_k[3] = n_k[3] & ~(termios.ECHO | termios.ICANON)
                                termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
                                enPassword=raw_input('Password:')
                                if enUsername==env_setting['enUsername'] and enPassword==env_setting['enPassword']:
                                    space=ENABLE
                                    promp='# '
                                    #env_setting=envLoad(1,'env_settings_tmp.json')
                                    prompLen=refreshPromp()
                                    break
                                else:
                                    sys.stdout.write('\n * Wrong username or password!\n')
                                time.sleep(0.5)
                            sys.stdout.write('\n')
                        else:
                                space=ENABLE
                                promp='# '
                                #env_setting=envLoad(1,'env_settings_tmp.json')
                                prompLen=refreshPromp()
                            
                    elif reSpace==CONFIG: #2
                        space=CONFIG
                        promp='(config)# '
                        #env_setting=envLoad(1,'env_settings_tmp.json')
                        prompLen=refreshPromp()
                    elif reSpace==DEBUG: #3
                        space=DEBUG
                        promp='(debug)$ '
                        #env_setting=envLoad(1,'env_settings_tmp.json')
                        prompLen=refreshPromp()

                if confchan==1:
                    env_setting=envLoad(1,'env_settings_tmp.json')
                    prompLen=refreshPromp()
                    
            if line and historyLen<env_setting['historyItems']:
                history.append(line)
                historyLen=len(history)
            elif line and historyLen>=env_setting['historyItems']:
                history=history[1:]
                history.append(line)
                historyLen=env_setting['historyItems']
            historyIndex=0
            if line:
                sys.stdout.write(''.join([env_setting['hostname'],promp]))
            else:
                sys.stdout.write(''.join(['\n',env_setting['hostname'],promp]))
            sys.stdout.flush()
            #enterClear()
            cursors=0
            line=''
            lineLen=0
            cursorsModify=''
            cursorsMove=0
            cursorsFreese=0
            hintLines=0
        elif ord(ch)==12: #clear screen
            line=line[:-1]
            sys.stdout.write(''.join(['\033[0,0f\033[2J',env_setting['hostname'],promp]))    
        elif ord(ch)==23:
            line=line[:-1]
            if cursorsMove==0 and cursors>0:
                Ctrl_W_Fields=line.rsplit(' ',1)
                Ctrl_W_FieldLen=len(Ctrl_W_Fields)
                firstField=Ctrl_W_Fields[0].rstrip(' ')
                firstFieldLen=len(firstField)
                sys.stdout.write(''.join(['\r','\033[',prompLen,'C','\033[K',firstField*(Ctrl_W_FieldLen-1)]))
                line=firstField*(Ctrl_W_FieldLen-1)
                cursors=firstFieldLen*(Ctrl_W_FieldLen-1)
            elif cursorsMove<0 and cursors>0:
                Ctrl_W_saveField=line[cursorsMove:]
                Ctrl_W_Fields=line[:cursorsMove].rsplit(' ',1)
                Ctrl_W_FieldLen=len(Ctrl_W_Fields)
                firstField=Ctrl_W_Fields[0].rstrip(' ')
                firstFieldLen=len(firstField)
                line=''.join([firstField*(Ctrl_W_FieldLen-1),Ctrl_W_saveField])
                sys.stdout.write(''.join(['\r','\033[',prompLen,'C','\033[K',line,'\b'*(-cursorsMove)]))
                cursors=firstFieldLen*(Ctrl_W_FieldLen-1)
            elif cursors==0:
                sys.stdout.write(''.join([line,'\b'*(-cursorsMove)]))
            cursorsFreese=cursors
            cursorsModify=''
        elif ord(ch)==27:
            line=line[:-1]
            arrow=sys.stdin.read(2)
            if ord(arrow[1])==65:
                #'up arrow'
                if historyLen>0 and historyIndex<=0 and historyLen>-historyIndex:
                    historyIndex-=1
                    line=history[historyIndex].encode()
                sys.stdout.write(''.join(['\r','\033[',prompLen,'C','\033[K',line]))
                cursors=len(line)
            elif ord(arrow[1])==66:
                #'down arrow'
                if historyLen>0 and historyIndex<historyLen and historyIndex<-1:
                    historyIndex+=1
                    line=history[historyIndex].encode()
                sys.stdout.write(''.join(['\r','\033[',prompLen,'C','\033[K',line]))
                cursors=len(line)
            elif ord(arrow[1])==67:
                if cursors<lineLen:
                    cursors+=1
                    cursorsMove+=1
                    sys.stdout.write('\033[1C')
                    cursorsModify=''
                    cursorsFreese=cursors
            elif ord(arrow[1])==68:
                if cursors>0:
                    cursors-=1
                    cursorsMove-=1
                    sys.stdout.write('\b')
                    cursorsModify=''
                    cursorsFreese=cursors
        elif ord(ch)==63:
            line=line[:-1]
            if hintLines>0:
                for eraseLine in range(hintLines):
                    sys.stdout.write(''.join(['\033[1B','\r','\033[K']))
                sys.stdout.write(''.join(['\033[',str(hintLines),'A','\033[',str(int(prompLen)+cursors),'C']))        
                hintLines=0
            sys.stdout.write('\n')
            QuestionKey(space,line,tHigh)
            sys.stdout.write(''.join(['\n',env_setting['hostname'],promp,line]))
        elif ord(ch)==127:
            line=line[:-1]
            if cursorsMove<0 and cursors>0:
                sys.stdout.write(''.join(['\b \b',line[cursorsMove:],' ','\b'*(-cursorsMove+1)]))
                line=''.join([line[:cursors-1],line[cursorsMove:]])
            elif cursorsMove==0 and cursors>0:
                sys.stdout.write('\b \b')
                line=line[:-1]
            if cursors>0:
                cursors-=1
            cursorsFreese=cursors
            cursorsModify=''
        elif lineLen<=128:
            if cursorsMove<0:
                line=line[:-1]
                cursorsModify=''.join([cursorsModify,ch])
                line=''.join([line[:cursorsFreese],cursorsModify,line[cursorsMove:]])
                sys.stdout.write(''.join(['\r','\033[',prompLen,'C']))
                sys.stdout.write(''.join([line,'\b'*(-cursorsMove)]))
            else:
                sys.stdout.write(unicode(ch,errors='ignore'))
            if cursors<=lineLen:
                cursors+=1
            sys.stdout.flush()
    #except TypeError as reason:
    #    print 'abc'
    #    print reason
    except KeyboardInterrupt:
        n_k[3] = n_k[3] | termios.ECHO
        termios.tcsetattr(sys.stdin.fileno(),termios.TCSADRAIN,n_k)
        exit()
        #pass
    except MyException as errors:
        if errors.error == 'timeout':
            sys.stdout.write(''.join(['\n',errors.reason,'\n']))
            exit()
        elif errors.error == 'CtrlZ':
            print 'a'
            pass
