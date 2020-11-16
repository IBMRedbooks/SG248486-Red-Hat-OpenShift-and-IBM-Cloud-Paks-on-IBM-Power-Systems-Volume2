#!/usr/bin/python3
# Version 10
import hmc_pcm as hmc
import time
import sys
import json

# Hard code the HMC/usr/password below
# or
# have them on the command line
# or
# in a file nextract_config.json
#
hostname=""
user=""
password=""

if len(hostname) == 0:
    #print("not hard coded")
    if len(sys.argv) == 4:   # four including the program name entry [0]
        #print("using command line")
        hostname=sys.argv[1]
        user    =sys.argv[2]
        password=sys.argv[3]
    else:
        #print("not three items on the command line")
        pass

if len(hostname) == 0:
    #print("reading config file")
    try:
        with open('nextract_config.json') as auth_file:
            auth = json.load(auth_file)
        #print(auth)
        hostname=auth["hostname"]
        user    =auth["user"]
        password=auth["password"]
    except:
        #print("Problem loading nextract_config.json")
        pass

if len(hostname) == 0:
    print("Usage: %s HMC-hostname HMC-username HMC-password" %(sys.argv[0]))
    sys.exit(1)

#print("HMC hostanme=%s User=%s Password=%s"  %( hostname, user, password))


print("-> Logging on to %s as user %s" % (hostname,user))
hmc = hmc.HMC(hostname, user, password)

#hmc.set_debug(True)

serverlist = hmc.get_server_details_pcm()  # returns a list of dictionaries one per Server

flags_need_setting = 0
for count,server in enumerate(serverlist):
    if server['capable'] == 'false':
        print("-->Server %d %-20s not capable of supplying Energy stats"%(count,server['name']))
        continue
    if server['energy'] == 'false':
        print("-->Server %d %-20s capable of collecting Enegry stats and not enabled"%(count,server['name']))
        continue
    print("-->Server %d %-20s capable of collecting Energy stats but need disabling now"%(count,server['name']))
    hmc.set_energy_flags(server['name'],'false')
    flags_need_setting += 1

if flags_need_setting > 0:
    print("->Sending updated energy preferences to the HMC")
    hmc.set_preferences_pcm()

print("-> Finished")
