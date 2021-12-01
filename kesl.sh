#!/bin/bash

# The script reconnects the KSC agent to the backup KSC if the main one is unavailable. If the primary KSC is available and the agent is connected to the backup, then it reconnects to the primary.
# Also, the script monitors the availability of the KSC via ICMP and checks if the reconnect command was successful.

#massive - select an array of KSC IP addresses depending on the contour

#Events are written to the log file /var/log/kasper.log. When the log size reaches 1 GB, it is deleted and recreated.
if [[ ! -f /var/log/kasper.log ]]; then touch /var/log/kasper.log; chmod 666 /var/log/kasper.log; fi
if [[ $(find /var/log/ -name kasper.log -size +1G) ]]; then rm -f /var/log/kasper.log; fi

massive()
{
	#Selecting IP-addresses of the main and backup storages
        local -n IP=$1
        if [[ $(hostname | grep 01) ]]
        then
                IPIZ=(10.111.13.179 10.111.15.180)
        	IPVN=(10.111.23.102 10.149.25.102)
        	IPIN=(10.111.33.67 10.111.35.163)
        elif [[ $(hostname | grep 02) ]]
        then
		 IPIZ=(10.111.15.180 10.111.13.179)
                 IPVN=(10.149.25.102 10.111.23.102)
                 IPIN=(10.111.35.163 10.111.33.67)
        fi
        IP=()
        if [[ $(hostname | grep vp) ]]
        then
                for t in ${IPVN[@]}; do
                        IP+=($t)
                done
        elif [[ $(hostname | grep iz) ]]; then
                for t in ${IPIZ[@]}; do
                        IP+=($t)
                done
        else
                for t in ${IPIN[@]}; do
                        IP+=($t)
                done
        fi
}
var=0
massive my_array
for g in ${my_array[@]};
do
	var=$(($var+1))
	#Checking the availability of hypervisor servers with ICMP backup storages
        cc=$(ping -c4 $g | sed -n '1,/^---/d;s/%.*//;s/.*, //g;p;q')
        if [[ $cc -eq 100 ]]
        then
                if [ $var = 1 ]
                then
			echo $(date +"%Y%m%d-%H%M%S") KSC server of $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) is not available >> /var/log/kasper.log
			continue
		elif [ $var = 2 ]
		then 
			echo $(date +"%Y%m%d-%H%M%S") KSC server of $(if [[ $(hostname | grep 01) ]]; then echo RCOD; elif [[ $(hostname | grep 02) ]]; then echo OCOD; fi) is not available >> /var/log/kasper.log
		 	exit
		fi
	else
		if [ $var = 1 ]
                then
                        echo $(date +"%Y%m%d-%H%M%S")  KSC server of $(if [[ $(hostname | grep 01) ]]; then echo OCOD; elif [[ $(hostname | grep 02) ]]; then echo RCOD; fi) is available >> /var/log/kasper.log
                        #Checking the current KSC server to which the KSC agent is connecting
			if [ "$(/opt/kaspersky/klnagent64/bin/klnagchk | grep "Server address" | awk '{print $3}' | sed "s/'//g")" = "$g" ]
                        then
                                exit
			#Switching a KSC Agent to a Different KSC Server
                        elif [[ $(/opt/kaspersky/klnagent64/bin/klmover -address $g) ]]; then echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation Successful >> /var/log/kasper.log; exit; else echo $(date +"%Y%m%d-%H%M%S")  KSC Server change operation Unsuccessful>> /var/log/kasper.log
                        fi
                elif [ $var = 2 ]
                then
                        echo $(date +"%Y%m%d-%H%M%S")  KSC server of $(if [[ $(hostname | grep 01) ]]; then echo RCOD; elif [[ $(hostname | grep 02) ]]; then echo OCOD; fi) is available >> /var/log/kasper.log
			if [ "$(/opt/kaspersky/klnagent64/bin/klnagchk | grep "Server address" | awk '{print $3}' | sed "s/'//g")" = "$g" ]
                        then
                                exit
                        elif [[ $(/opt/kaspersky/klnagent64/bin/klmover -address $g) ]]; then echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation Successful >> /var/log/kasper.log; exit; else echo $(date +"%Y%m%d-%H%M%S") KSC Server change operation Unsuccessful >> /var/log/kasper.log
                        fi
		fi
	fi
done
