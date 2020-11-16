#!/usr/bin/python3
# Version 10
# Collect Shared Storage Pool data from the HMC and generate googlechart/JavaScript graphing webpage
# In collects whole SSP level and VIOS level stats
import hmc_pcm
import nchart
import time
import sys
import json

output_html=False
output_csv=False
output_csvold=False
output_influx=True

# Hard code the HMC/usr/password below
# or
# have them on the command line
# or
# in a file nextract_config.json
#
hostname=""
user=""
password=""

# ony used if output_influx = True and not using a config file
ihost=""
iport=8086
iuser =""
ipassword = ""
idbname = ""

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
        if output_influx:
            ihost=auth['ihost']
            iport=auth['iport']
            iuser = auth['iuser']
            ipassword = auth['ipassword']
            idbname = auth['idbname']
    except:
        print("Problem loading nextract_config.json")
        pass

if len(hostname) == 0:
    print("Usage: %s HMC-hostname HMC-username HMC-password" %(sys.argv[0]))
    sys.exit(1)

#print("HMC hostanme=%s User=%s Password=%s"  %( hostname, user, password))


print("-> Logging on to %s as user %s" % (hostname,user))
hmc = hmc_pcm.HMC(hostname, user, password)

print("-> Get Stripped Preferences") # returns XML text
prefstripped = hmc.get_stripped_preferences_ssp()

print("-> Parse Preferences")
ssplist = hmc.parse_prefs_ssp(prefstripped)  # returns a list of dictionaries one per SSP
all_true = True
enabled = []
for ssp in ssplist:
    if ssp['agg'] == 'false' or ssp['mon'] == 'false':
        good = "BAD "
        all_true = False
    else: 
        good = "GOOD"
        enabled.append(ssp)
    print('-> cluster=%-10s pool=%-10s AggregrateEnabled=%5s Monitoring Enabled=%5s =%s' 
        %(ssp['cluster'], ssp['pool'], ssp['agg'], ssp['mon'], good))
if all_true:
    print("-> Skipping Set Preferences as all SSP's are already enabled")
else:
    print("-> Set Preferences - please wait 10+ minutes for stats to appear!")
    prefset = hmc.set_preferences_ssp(prefstripped) # Switches on ALL Aggregatation &  monitoring flags

print("-> Processing SSP")
for count, ssp in enumerate(enabled,start=1):
    print('--> SSP=%d Getting filenames for cluster=%s pool=%s' %(count,ssp['cluster'], ssp['pool']))
    print("---> Requesting %s as monitoring enabled" %(ssp['pool']))
    starttime = time.time()
    JSONfiles = hmc.get_filenames_ssp(ssp['uuid'],ssp['pool']) # returns XML of filename(s)
    endtime = time.time()
    print("---> Received %d file(s) in %.2f seconds" % (len(JSONfiles), endtime - starttime))
    for num,JSONfile in enumerate(JSONfiles,start=1):
        print('---> File=%d Getting stats from %s' %(num,JSONfile['filename']))
        JSONdata = hmc.get_stats(JSONfile['url'],JSONfile['filename'], ssp['pool']) # returns JSON stats
        info = hmc.extract_ssp_info(JSONdata)
        #print("info")
        #print(info)
        sspstats = hmc.extract_ssp_totals(JSONdata)
        if len(sspstats) == 0:
            print("No SSP level stats - bailing out on this SSP")
            continue # Do not attempt to create an empty graph
        
        header, viosstats = hmc.extract_ssp_vios(JSONdata)
        if len(viosstats) == 0:
            print("No data returned from extract_ssp_vios()")
            continue # Do not attempt to create an empty graph
        #print(header)
        #print(viosstats)
        print("---> Processing JSON data size=%d bytes" % (len(JSONdata)))

        if output_csv:
            filename="SSP-totals-" + info["cluster"] + "-" + info["ssp"] + ".csv"
            f = open(filename,"w")
            f.write("time, size, free, readBytes, writeBytes, readServiceTime-ms, writeServiceTime-ms\n")
            for s in sspstats:
                 buffer="%s, %d,%d, %d,%d, %.3f,%.3f\n" % (s['time'],
                        s['size'],           s['free'], 
                        s['readBytes'],      s['writeBytes'], 
                        s['readServiceTime'],s['writeServiceTime'])
                 f.write(buffer)
            f.close()
            print("Saved SSP Totals comma separated values to %s" % (filename))

            filename="SSP-VIOS-" + info["cluster"] + "-" + info["ssp"] + ".csv"
            f = open(filename,"w")
            f.write("time")
            for viosname in header:
                 f.write("," + viosname)
            f.write("\n")
            for row in viosstats:
                 f.write("%s" % (row["time"]))
                 for readkb in row['readKB']:
                     f.write(",%.3f" % (readkb))
                 for writekb in row['writeKB']:
                     f.write(",%.3f" % (writekb))
                 f.write("\n")
            f.close()
            print("Saved SSP VIOS comma separated values to %s" % (filename))

        if output_csvold:
            filename="SSP_total_io.csv"
            f = open(filename,"a")  # append 
            #f.write("sspname, time, size, free, readBytes, writeBytes, readServiceTime-ms, writeServiceTime-ms\n")
            for s in sspstats:
                 buffer="%s,%s, %d,%d, %d,%d, %.3f,%.3f\n" % (info["ssp"], s['time'],
                        s['size'],           s['free'], 
                        s['readBytes'],      s['writeBytes'], 
                        s['readServiceTime'],s['writeServiceTime'])
                 f.write(buffer)
            f.close()
            print("Saved SSP Totals comma separated values to %s old format" % (filename))

            filename="SSP_vios_io.csv"
            f = open(filename,"a")  # append 
            f.write("%s,Header" % (info["ssp"]))
            for viosname in header:
                 f.write("," + viosname)
            f.write("\n")
            for row in viosstats:
                 f.write("%s" % (row["time"]))
                 for readkb in row['readKB']:
                     f.write(",%.3f" % (readkb))
                 for writekb in row['writeKB']:
                     f.write(",%.3f" % (-writekb))
                 f.write("\n")
            f.close()
            print("Saved SSP VIOS comma separated values to %s old format" % (filename))

        if output_html:                                              # Create .html file that graphs the stats
            filename = "SSP-" + info['ssp'] + ".html"          # Using googlechart
            print("-->File=%s Length: info=%d sspstats=%d header=%d viosstats=%d" %(filename,len(info),len(sspstats),len(header),len(viosstats)))
            #print(sspstats[0])
            n = nchart.nchart_open()
            n.nchart_ssp(filename, info, sspstats, header, viosstats)
            print("Saved webpage to %s" % (filename))

        if output_influx:     # push in to InfluxDB

            from influxdb import InfluxDBClient
            client = InfluxDBClient(ihost, iport, iuser, ipassword, idbname)

            print("SSP for Influx (Pool:%s Cluster:%s)"%(info['ssp'],info['cluster']))
            entry=[]
            count=0
            #print(info)
                #{'ssp': 'spiral', 'end': '2019-07-03T15:30:00+0000', 'cluster': 'spiral', 'start': '2019-07-02T14:00:00+0000', 'frequency': 300}
            #print('sspstats')
                #{'writeServiceTime': 0.0, 'free': 247812.0, 'size': 523776.0, 'numOfWrites': 0.0, 'readBytes': 0.0, 'time': '2019-07-02T14:00:00', 'readServiceTime': 0.0, 'numOfReads': 0.0, 'writeBytes': 0.0}
            #print(sspstats)
            #print('viosstats')
            #print(viosstats)
                #['rubyvios3-Read-KBs', 'rubyvios4-Read-KBs', 'yellowvios1-Read-KBs', 'yellowvios2-Read-KBs', 'rubyvios3-Write-KBs', 'rubyvios4-Write-KBs', 'yellowvios1-Write-KBs', 'yellowvios2-Write-KBs']
            #print('header')
            #print(header)
                #{'writeKB': [0.0, 0.0, 0.0, 0.0], 'time': '2019-07-02T14:00:00', 'readKB': [0.0, 0.0, 0.0, 0.0]}
            for sam in sspstats:
                data = { 'measurement': 'SSP', 'tags': { 'pool': info['ssp'], 'cluster': info['cluster'] }, 'time': sam['time'] }
                #print(data)
                data['fields'] = { "free": sam['free'],
                "size": sam['size'],
                "readBytes": sam['readBytes'],
                "writeBytes": sam['writeBytes'],
                "numOfWrites": sam['numOfWrites'],
                "numOfReads": sam['numOfReads'],
                "readServiceTime": sam['readServiceTime'],
                "writeServiceTime": sam['writeServiceTime'] }
                #print(data)
                count = count +1
                entry.append(data)
            #print("entry count=%d"%(count))
            client.write_points(entry)

            half = len(header) / 2
            for sam in viosstats:
                for count,vios in enumerate(header):
                    if count >= half:
                        break
                    name=header[count]
                    name=name[0:-8]
                    if name[-1:] == '-':
                       name=name[0:-1]
                    data = { 'measurement': 'SSPVIOS', 'tags': { 'pool': info['ssp'], 'cluster': info['cluster'], 'vios': name}, 'time': sam['time'] }
                    #print(data)
                    data['fields'] = { "readKB": sam['readKB'][count], "writeKB": sam['writeKB'][count] }
                    #print(data)
                    count = count +1
                    entry.append(data)
                #print("entry count=%d"%(count))
                client.write_points(entry)

print("Logging off the HMC")
hmc.logoff()
