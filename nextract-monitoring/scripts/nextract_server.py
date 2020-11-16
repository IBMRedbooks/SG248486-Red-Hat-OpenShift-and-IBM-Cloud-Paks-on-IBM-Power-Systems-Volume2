#!/usr/bin/python3
# Version 10
import hmc_pcm as hmc
import nchart
import time
import sys
import json

debug=False
output_csv=False
output_html=False
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
        hostname=auth['hostname']
        user    =auth['user']
        password=auth['password']
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

if output_influx:
    from influxdb import InfluxDBClient
    client = InfluxDBClient(ihost, iport, iuser, ipassword, idbname)


print("-> Logging on to %s as user %s" % (hostname,user))
hmc = hmc.HMC(hostname, user, password)

print("-> Get Preferences") # returns XML text
prefstripped = hmc.get_stripped_preferences_pcm()
if debug:
    hmc.save_to_file("server_perferences.xml",prefstripped)

print("-> Parse Preferences")
serverlist = hmc.parse_prefs_pcm(prefstripped)  # returns a list of dictionaries one per Server
perflist = []
all_true = True
print("-> ALL servers:")
for num,server in enumerate(serverlist):
    if server['lterm'] == 'true' and server['agg'] == 'true':
        todo = "- OK"
        perflist.append(server)
    else:
        todo = "- remove"
    print('-> Server name=%-16s agg=%-5s longterm=%-5s %s ' 
        %(server['name'], server['agg'], server['lterm'], todo))

print("-> Servers with Perf Stats")
for count, server in enumerate(perflist,start=1):  # just loop the servers with stats
    print('')

#   if server['name'] == 'server_with_no_VIOS':
#      print("Skipping server %s as it has no VIOS" % (server['name']))
#      continue

    print('--> Server=%d Getting filenames for %s' %(count,server['name']))
    starttime = time.time()
    filelist = hmc.get_filenames_server(server['atomid'],server['name']) # returns XML of filename(s)
    endtime = time.time()
    print("---> Received %d file(s) in %.2f seconds" % (len(filelist), endtime - starttime))

    for num,file in enumerate(filelist,start=1): # loop around the files
        filename=file['filename']
        url=file['url']
        print('---> Server=%s File=%d %s' %(server['name'], num,filename))


    for num,file in enumerate(filelist,start=1): # loop around the files
        filename=file['filename']
        url=file['url']
        data = hmc.get_stats(url,filename, server['name']) # returns JSON stats

        if filename[:13] == "ManagedSystem": # start of the filename tells you if server or LPAR
            filename2 = filename.replace('.json','.JSON')
            print('\n\nManagedSystem\n---> Save readable JSON File=%d bytes=%d name=%s' %(num,len(data),filename2))
            if debug:
                hmc.save_json_txt_to_file(filename2,data)

            info = hmc.extract_server_info(data)
            print("----> ServerInfo name=%s mtms=%s type=%s frequency=%s seconds\n----> ServerInfo Date=%s start=%s end=%s" %( info['name'], info['mtms'], info['mtype'], info['freq'], info['stime'][:10], info['stime'][11:19], info['etime'][11:19]))

            header, stats, errors, lines = hmc.extract_server_stats(data)
            print("----> Records=%d Errors=%d" % (lines,errors))
            if errors > 0:
                print("Stopping processing of this server %s due to errors"%(info['name']))
                break

            if output_html:                                              # Create .html file that graphs the stats
                filename = "Server-" + info['name'] + ".html"          # Using googlechart
                n = nchart.nchart_open()
                n.nchart_server(filename, info, stats)
                print("Saved webpage to %s" % (filename))

            if output_influx:  # Create InfluxDB measurements and pump them in
                print("Server stats: %s)"%(info['name']))
                entry=[]
                count=0
                for line in stats:
                    data = { 'measurement': 'Server', 
                    'time': line['time'],
                    'tags': { 'lpar': info['name'] },
                    'fields': { 
                        'cpu_avail':         line['cpu_avail'], 
                        'cpu_conf':          line['cpu_conf'], 
                        'cpu_total':         line['cpu_total'], 
                        'cpu_used':          line['cpu_used'], 
                        'mem_avail':         line['mem_avail'], 
                        'mem_conf':          line['mem_conf'], 
                        'mem_total':         line['mem_total'], 
                        'mem_inVM':          line['mem_inVM'],
                        'vios_cpu_vp':       line['vios_cpu_vp'], 
                        'vios_cpu_entitled': line['vios_cpu_entitled'], 
                        'vios_cpu_used':     line['vios_cpu_used'],
                        'vios_mem_conf':     line['vios_mem_conf'], 
                        'vios_mem_used':     line['vios_mem_used'], 
                        'vios_net_rbytes':   line['vios_net_rbytes'], 
                        'vios_net_wbytes':   line['vios_net_wbytes'], 
                        'vios_net_reads':    line['vios_net_reads'], 
                        'vios_net_writes':   line['vios_net_writes'],
                        'vios_fc_rbytes':    line['vios_fc_rbytes'], 
                        'vios_fc_wbytes':    line['vios_fc_wbytes'], 
                        'vios_fc_reads':     line['vios_fc_reads'], 
                        'vios_fc_writes':    line['vios_fc_writes'] } }
                    count = count +1
                    entry.append(data)
                client.write_points(entry)
                print("Influx added %d records Server=%s"%(count,info['name']))

            if output_csv:                                               # Create comma separated vaules file
                filename = "Server-" + info['name'] + ".csv"
                f = open(filename,"a")
                f.write("%s\n" %(header))
                for line in stats:
                    f.write("%s, %.2f,%.2f,%.2f,%.2f, %d,%d,%d,%d, %.2f,%.2f,%.2f, %.1f,%.1f, %.1f,%.1f,%.1f,%.1f, %.1f,%.1f,%.1f,%.1f\n" %( line['time'], 
                        line['cpu_avail'], line['cpu_conf'], line['cpu_total'], line['cpu_used'], 
                        line['mem_avail'], line['mem_conf'], line['mem_total'], line['mem_inVM'],
                        line['vios_cpu_vp'], line['vios_cpu_entitled'], line['vios_cpu_used'],
                        line['vios_mem_conf'], line['vios_mem_used'], 
                        line['vios_net_rbytes'], line['vios_net_wbytes'], line['vios_net_reads'], line['vios_net_writes'],
                        line['vios_fc_rbytes'], line['vios_fc_wbytes'], line['vios_fc_reads'], line['vios_fc_writes'] ))
                f.close()
                print("Saved comma separated values to %s" % (filename))

            if debug:
                print("-----> Header=%s" % (header))
                for lines,line in enumerate(stats):
                    print("%s, %.2f,%.2f,%.2f,%.2f, %d,%d,%d,%d, %.2f,%.2f,%.2f, %.1f,%.1f, %.1f,%.1f,%.1f,%.1f, %.1f,%.1f,%.1f,%.1f" %( line['time'], 
                        line['cpu_avail'], line['cpu_conf'], line['cpu_total'], line['cpu_used'], 
                        line['mem_avail'], line['mem_conf'], line['mem_total'], line['mem_inVM'],
                        line['vios_cpu_vp'], line['vios_cpu_entitled'], line['vios_cpu_used'],
                        line['vios_mem_conf'], line['vios_mem_used'], 
                        line['vios_net_rbytes'], line['vios_net_wbytes'], line['vios_net_reads'], line['vios_net_writes'],
                        line['vios_fc_rbytes'], line['vios_fc_wbytes'], line['vios_fc_reads'], line['vios_fc_writes'] ))
                    if lines >3:
                        break
 
        if filename[:16] == "LogicalPartition":
            # print("\n\n----> LPAR level stats .xml (missing the .xml extension) of JSON filenames giving")
            if debug:
                filename2 = filename + ".xml"
                print('\n----> Server=%s Filenames XML File=%d bytes%d name=%s' %(server['name'],num,len(data),filename2))
                hmc.save_to_file(filename2,data)
            else:
                print('\n----> Server=%s Filenames XML File=%d bytes%d' %(server['name'],num,len(data)))

            filename3, url = hmc.get_filename_from_xml(data)
            LPARstats = hmc.get_stats(url, filename3, "LPARstats")

            if debug:
                filename3 = filename3.replace('.json','.JSON')
                print('---> Save readable JSON File=%d bytes=%d name=%s' %(num,len(LPARstats),filename3))
                hmc.save_json_txt_to_file(filename3,LPARstats)

            info = hmc.extract_lpar_info(LPARstats)
            if debug:
                print("----> LPAR")
                print(info)

            header, stats, errors, lines = hmc.extract_lpar_stats(LPARstats)
            if debug:
                print("----> LPAR Records=%d Errors=%d" % (lines,errors))
                print("----> LPAR Header=%s" % (header))
                for lineno,line in enumerate(stats):
                    print("LPAR Line %d" % (lineno))
                    print(line)
                    if lines >3:
                        break

            if output_html:                                              # Create .html file that graphs the stats
                filename = "LPAR-" + info['lparname'] + ".html"          # Using googlechart
                n = nchart.nchart_open()
                n.nchart_lpar(filename, info, stats)
                print("Created webpage %s" % (filename))

            if output_csv:                                               # Create comma separated vaules file
                filename = "LPAR-" + info['lparname'] + ".csv"
                f = open(filename,"a")
                f.write("%s\n" %(header))
                for line in stats:
                    f.write("%s, %.2f,%.2f,%.2f, %.1f, %.1f,%.1f,%.1f,%.1f, %.1f,%.1f,%.1f,%.1f\n" % (line['time'], line['cpu_vp'], line['cpu_entitled'], line['cpu_used'], line['mem_conf'], line['net_rbytes'], line['net_wbytes'], line['net_reads'], line['net_writes'], line['disk_rbytes'], line['disk_wbytes'], line['disk_reads'], line['disk_writes'] ))
                f.close()
                print("Saved comma separated values to %s" % (filename))

            if output_influx:  # Create InfluxDB measurements and pump them in
                print("LPAR stats: %s)"%(info['lparname']))
                entry=[]
                count=0
                for line in stats:
                    data = { 'measurement': 'LPAR', 
                    'time': line['time'],
                    'tags': { 'lpar': info['lparname'] },
                    'fields': { 
                      'cpu_vp':       line['cpu_vp'], 
                      'cpu_entitled': line['cpu_entitled'], 
                      'cpu_used':     line['cpu_used'], 
                      'mem_conf':     line['mem_conf'], 
                      'net_rbytes':   line['net_rbytes'], 
                      'net_wbytes':   line['net_wbytes'], 
                      'net_reads':    line['net_reads'], 
                      'net_writes':   line['net_writes'], 
                      'disk_rbytes':  line['disk_rbytes'], 
                      'disk_wbytes':  line['disk_wbytes'], 
                      'disk_reads':   line['disk_reads'], 
                      'disk_writes':  line['disk_writes'] } }
                    count = count +1
                    entry.append(data)
                client.write_points(entry)
                print("Influx added %d records LPAR=%s"%(count,info['lparname']))

print("Logging off the HMC")
hmc.logoff()
