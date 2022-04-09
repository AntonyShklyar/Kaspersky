#!/usr/bin/python

# The script reconnects the KSC agent to the backup KSC if the main one is unavailable. If the primary KSC is available and the agent is connected to the backup, then it reconnects to the primary.
# Also, the script monitors the availability of the KSC via ICMP and checks if the reconnect command was successful.
#massive - select an array of KSC IP addresses depending on the contour

import os
import socket
import subprocess
import re

def logs():
	'''Creating a session log and a log with a description of all sessions'''
	#If the size of 1 GB is exceeded, the kasper.log is deleted and recreated
	if not os.path.exists('/var/log/kasper.log'): f=open('/var/log/kasper.log', "w+"); f.close()
	if not os.path.getsize('/var/log/kasper.log')/(1024*1024*1024)==0: os.system(r' >/var/log/kasper.log')
	#The function returns 0
def networkavailable(var, g):
	'''Determining the network availability of KSC server'''
        mount = subprocess.Popen(("ping", "-c4", g), stdout=subprocess.PIPE); exit_code = subprocess.check_output(("sed", "-n", '1,/^---/d;s/%.*//;s/.*, //g;p;q'), stdin=mount.stdout); mount.wait()
        if int(exit_code.replace("\n","")) == 100:
                if var==1:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server KSC is not available       >> /var/log/kasper.log')
                        return 1
                else:
                        os.system('echo $(date +"%Y%m%d-%H%M%S")     Server KSC is not available       >> /var/log/kasper.log')
                        return 1
        else:
                os.system('echo $(date +"%Y%m%d-%H%M%S")   Server KSC is available      >> /var/log/kasper.log')
                return 0
	'''
	Return data type - number.
	If the function returns 0 - KSC server is available
	If the function returns 1 - KSC server isn't available
	'''
'''
Editable parameters:
--domain
The data type is a dictionary.
Data - domain: list of IP addresses of domain stores
''''
domain={'ac.com':['10.111.15.55', '10.111.15.64', '10.111.15.76'],'vp.com':['10.111.16.55', '10.111.16.64', '10.111.16.76'],'in.com':['10.111.17.54', '10.111.17.64', '10.111.17.76']}
IP=[]
logs()
for x, y in domain.items():
	if x in a:
		IP.append(y)
for var, g in enumerate(IP, 1):
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
			if subprocess.call(["/opt/kaspersky/klnagent64/bin/klmover", "-address", g]) == 0: os.system('echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation on'+g+' Successful >> /var/log/kasper.log'); exit()
			else:
				os.system('echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation on'+g+' Unsuccessful >> /var/log/kasper.log'); exit()
	elif var != len(IP):
                continue
        else:
                exit()
