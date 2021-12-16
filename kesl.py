#!/usr/bin/python

# The script reconnects the KSC agent to the backup KSC if the main one is unavailable. If the primary KSC is available and the agent is connected to the backup, then it reconnects to the primary.
# Also, the script monitors the availability of the KSC via ICMP and checks if the reconnect command was successful.
#massive - select an array of KSC IP addresses depending on the contour

import os
import socket
import subprocess
import re

#Events are written to the log file /var/log/kasper.log. When the log size reaches 1 GB, it is deleted and recreated.
if not os.path.exists('/var/log/kasper.log'): open("/var/log/kasper.log", "w+")
#If the size of 1 GB is exceeded, the debug.log is deleted and recreated
if not os.path.getsize('/var/log/kasper.log')/(1024*1024*1024)==0: os.remove('/var/log/kasper.log')

def massive(IP=[]):
	if set('01').issubset(socket.gethostname()):
        	IPIZ = ["10.111.15.137", "10.111.16.195"]
                IPVN = ['10.111.23.102', '10.149.25.102']
                IPIN = ['10.111.33.67', '10.111.35.163']
        elif set('02').issubset(socket.gethostname()):
        	IPIZ = ['10.111.16.195', '10.111.15.137']
                IPVN = ['10.149.25.102', '10.111.23.102']
                IPIN = ['10.111.35.163', '10.111.33.67']	
	if set('vn').issubset(socket.gethostname()):
		for i in IPVN:
			IP.append(i)
	elif set('iz').issubset(socket.gethostname()):
                for i in IPIZ:
                        IP.append(i)
	else:
		for i in IPIN:
                        IP.append(i)
	return IP
def networkavailable(var, g):
        mount = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=mount.stdout); mount.wait()
        if int(exit_code.replace("\n","")) == 100:
                if var==1:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server KSC is not available       >> /var/log/backupdb.log')
                        return 1
                else:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server KSC is not available       >> /var/log/backupdb.log')
                        return 1
        else:
                os.system('echo $(date +"%Y%m%d-%H%M%S")   Server KSC is available      >> /var/log/backupdb.log')
                return 0
var=0
my_array=massive()
for g in my_array:
        var += 1
        b=networkavailable(var, g)
        if b==0:
                cmd = "/opt/kaspersky/klnagent64/bin/klnagchk | grep 'Server address' | awk '{print $3}' | head -n 1" 
		pipe = os.popen(cmd)
		a = pipe.read()
		a=a.replace("\n","")
		n=str("'{}'".format(g))
		if a==n:
                        exit()
		else:
			if subprocess.call(["/opt/kaspersky/klnagent64/bin/klmover", "-address", g]) == 0: os.system('echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation Successful >> /var/log/kasper.log'); exit()
			else:
				os.system('echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation Unsuccessful >> /var/log/kasper.log'); exit()
	elif var != len(my_array):
                continue
        else:
                exit()
