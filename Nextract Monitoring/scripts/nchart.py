#!/usr/bin/python3
# Version 10
import os

class nchart_open(object):
    def __init__(self):
        '''Class initialisation to start a chart '''
        self.chartnum = 1 
        self.debug = False
        self.web = 1

    def output_start(self, file, title):
        ''' Head of the HTML webpage'''
        if self.debug:
            print("output_start(resource=%s, name=%s)"%(title))
        file.write('<html>' + '\n')
        file.write('<head>' + '\n')
        file.write('\t<title>' + title + '</title>\n')
        file.write('\t<script type="text/javascript" src="https://www.google.com/jsapi"></script>\n')
        file.write('\t<script type="text/javascript">\n')
        file.write('\tgoogle.load("visualization", "1.1", {packages:["corechart"]});\n')
        file.write('\tgoogle.setOnLoadCallback(setupCharts);\n')
        file.write('\tfunction setupCharts() {\n')
        file.write('\tvar chart = null;\n')
    

    def output_top(self, file, graphnum, units1 = '', units2 = '', units3 = '', units4 = '', units5 = '', units6 = '', units7 = '', units8 = '', units9 = '', units10 = '', units11 = '', units12 = '', units13 = '', units14 = '', units15 = '', units16 = ''):
        ''' Before the graph data with datetime + 2 columns of data '''
        if self.debug:
            print("output_top(graphnum=%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,$s)"
                %(graphnum,units1,units2,units3,units4,units5,units6,units7,units8,units9,units10,units11,units12,units13,units14,units15,units16))
        file.write('\tvar data_' + str(graphnum) +  ' = google.visualization.arrayToDataTable([\n')
        # opposite use of ' and " as we need to d single quotes in the  output
        file.write("[{type: 'datetime', label: 'Datetime'}")
        if units1 != '':
            file.write(",'" + units1 + "'")
        if units2 != '':
            file.write(",'" + units2 + "'")
        if units3 != '':
            file.write(",'" + units3 + "'")
        if units4 != '':
            file.write(",'" + units4 + "'")
        if units5 != '':
            file.write(",'" + units5 + "'")
        if units6 != '':
            file.write(",'" + units6 + "'")
        if units7 != '':
            file.write(",'" + units7 + "'")
        if units8 != '':
            file.write(",'" + units8 + "'")
        if units9 != '':
            file.write(",'" + units9 + "'")
        if units10 != '':
            file.write(",'" + units10 + "'")
        if units11 != '':
            file.write(",'" + units11 + "'")
        if units12 != '':
            file.write(",'" + units12 + "'")
        if units13 != '':
            file.write(",'" + units13 + "'")
        if units14 != '':
            file.write(",'" + units14 + "'")
        if units15 != '':
            file.write(",'" + units15 + "'")
        if units16 != '':
            file.write(",'" + units16 + "'")
        file.write("]\n")
    

    def output_top_unitstring(self, file, graphnum, unitstring):
        ''' Before the graph data with datetime + multiple columns of data '''
        if self.debug:
            print("output_top_unitstring(grapghnum=%d, unitstring=%s)"%(graphnum, unitstring))
        file.write('\tvar data_' + str(graphnum) +  ' = google.visualization.arrayToDataTable([\n')
        # opposite use of ' and " as e need to out '
        file.write("[{type: 'datetime', label: 'Datetime'}," + unitstring  + "]\n")
    
    def output_top_no_units(self, file, graphnum):
        ''' Before the graph data but the called will add the datetime + multiple columns of data line'''
        if self.debug:
            print("output_top_no_units(grapghnum=%d)"%(graphnum))
        file.write('var data_' + str(graphnum) + ' = google.visualization.arrayToDataTable([\n')
    
    def output_bot(self, file, graphnum, graphtitle):
        ''' After the JavaSctipt graph data is output, the data is terminated and the graph options set'''
        if self.debug:
            print("output_bot(resource=%s, graphnum=%d, name=%s, desc=%s)"%(resource, graphnum, name, description))
        file.write('\t]);\n')
        file.write('\tvar options_'+ str(graphnum) + ' = {\n')
        file.write('\t\tchartArea: {left: "5%", width: "85%", top: "10%", height: "80%"},\n')
        file.write('\t\ttitle: "' + graphtitle + '",\n')
        file.write('\t\tfocusTarget: "category",\n')
        file.write('\t\thAxis: { gridlines: { color: "lightgrey", count: 30 } },\n')
        file.write('\t\tvAxis: { gridlines: { color: "lightgrey", count: 11 } },\n')
        file.write('\t\texplorer: { actions: ["dragToZoom", "rightClickToReset"],\n')
        file.write('\t\taxis: "horizontal", keepInBounds: true, maxZoomIn: 20.0 },\n')
        file.write('\t\tisStacked:  0\n')
        file.write('\t};\n')
        file.write('\tdocument.getElementById("draw_'+ str(graphnum) + '").addEventListener("click", function() {\n')
        file.write('\tif (chart && chart.clearChart) chart.clearChart();\n')
        file.write('\tchart = new google.visualization.AreaChart(document.getElementById("chart_master"));\n')
        file.write('\tchart.draw( data_'+ str(graphnum) + ', options_'+ str(graphnum) + ');\n')
        file.write('\t});\n')
    
    def output_end2(self, file, name, button1, button2):
        ''' Finish off the web page '''
        if self.debug:
            print("output_end(name=%s)"%(name))
        file.write('\t}\n')
        file.write('\t</script>\n')
        file.write('\t</head>\n')
        file.write('\t<body bgcolor="#EEEEFF">\n')
        file.write('\t<b>Server: ' + name + ': </b>\n')
        file.write('\t<button id="draw_1" style="color:red;"><b>'+ button1 + '</b></button>\n')
        file.write('\t<button id="draw_2" style="color:blue;"><b>'+ button2 + '</b></button>\n')
        file.write('\t<div id="chart_master" style="width:100%; height:85%;">\n')
        file.write('\t<h2 style="color:blue">Click on a Graph button above, to display that graph</h2>\n')
        file.write('\t</div>\n')
        file.write('\n')
        file.write('Author: Nigel Griffiths @mr_nmon generated from HMC REST API using Python\n')
        file.write('Now with Zoom = Left-click and drag. To Reset = Right-click.\n')
        file.write('</body>\n')
        file.write('</html>\n')
    
    def output_end_ssp(self, file, name, button1, button2, button3 ,button4):
        ''' Specific version for Shared Storage Pool graphs - Finish off the web page '''
        if self.debug:
            print("output_end(name=%s)"%(name))
        file.write('\t}\n')
        file.write('\t</script>\n')
        file.write('\t</head>\n')
        file.write('\t<body bgcolor="#EEEEFF">\n')
        file.write('\t<b>Server: ' + name + ': </b>\n')
        file.write('\t<button id="draw_1" style="color:red;"><b>'+ button1 + '</b></button>\n')
        file.write('\t<button id="draw_2" style="color:blue;"><b>'+ button2 + '</b></button>\n')
        file.write('\t<button id="draw_3" style="color:green;"><b>'+ button3 + '</b></button>\n')
        file.write('\t<button id="draw_4" style="color:purple;"><b>'+ button4 + '</b></button>\n')
        file.write('\t<div id="chart_master" style="width:100%; height:85%;">\n')
        file.write('\t<h2 style="color:blue">Click on a Graph button above, to display that graph</h2>\n')
        file.write('\t</div>\n')
        file.write('\n')
        file.write('Author: Nigel Griffiths @mr_nmon generated from HMC REST API using Python\n')
        file.write('Now with Zoom = Left-click and drag. To Reset = Right-click.\n')
        file.write('</body>\n')
        file.write('</html>\n')

    def output_end_server(self, file, name, button1, button2, button3 ,button4, button5, button6, button7, button8, button9, button10):
        ''' Specific version for Server graphs - Finish off the web page '''
        if self.debug:
            print("output_end(name=%s)"%(name))
        file.write('\t}\n')
        file.write('\t</script>\n')
        file.write('\t</head>\n')
        file.write('\t<body bgcolor="#EEEEFF">\n')
        file.write('\t<b>Server: ' + name + ': </b>\n')
        file.write('\t<button id="draw_1" style="color:red;"><b>'+ button1 + '</b></button>\n')
        file.write('\t<button id="draw_2" style="color:red;"><b>'+ button2 + '</b></button>\n')
        file.write('\t<button id="draw_3" style="color:blue;"><b>'+ button3 + '</b></button>\n')
        file.write('\t<button id="draw_4" style="color:blue;"><b>'+ button4 + '</b></button>\n')
        file.write('\t<button id="draw_5" style="color:purple;"><b>'+ button5 + '</b></button>\n')
        file.write('\t<button id="draw_6" style="color:purple;"><b>'+ button6 + '</b></button>\n')
        file.write('\t<button id="draw_7" style="color:green;"><b>'+ button7 + '</b></button>\n')
        file.write('\t<button id="draw_8" style="color:green;"><b>'+ button8 + '</b></button>\n')
        file.write('\t<button id="draw_9" style="color:brown;"><b>'+ button9 + '</b></button>\n')
        file.write('\t<button id="draw_10" style="color:brown;"><b>'+ button10 + '</b></button>\n')
        file.write('\t<div id="chart_master" style="width:100%; height:85%;">\n')
        file.write('\t<h2 style="color:blue">Click on a Graph button above, to display that graph</h2>\n')
        file.write('\t</div>\n')
        file.write('\n')
        file.write('Author: Nigel Griffiths @mr_nmon generated from HMC REST API using Python\n')
        file.write('Now with Zoom = Left-click and drag. To Reset = Right-click.\n')
        file.write('</body>\n')
        file.write('</html>\n')

    def output_end_all(self, file, name, button1 = '', button2 = '', button3 = '', button4 = '', button5 = '', button6 = '', button7 = '', button8 = '', button9 = '', button10 = ''):
        ''' Generic version using named arguments for 1 to 10 buttons for Server graphs - Finish off the web page '''
        if self.debug:
            print("output_end(name=%s)"%(name))
        file.write('\t}\n')
        file.write('\t</script>\n')
        file.write('\t</head>\n')
        file.write('\t<body bgcolor="#EEEEFF">\n')
        file.write('\t<b>Server: ' + name + ': </b>\n')
        file.write('\t<button id="draw_1" style="color:red;"><b>'+ button1 + '</b></button>\n')
        if button2 != '':
            file.write('\t<button id="draw_2" style="color:red;"><b>'+ button2 + '</b></button>\n')
        if button3 != '':
            file.write('\t<button id="draw_3" style="color:blue;"><b>'+ button3 + '</b></button>\n')
        if button4 != '':
            file.write('\t<button id="draw_4" style="color:blue;"><b>'+ button4 + '</b></button>\n')
        if button5 != '':
            file.write('\t<button id="draw_5" style="color:purple;"><b>'+ button5 + '</b></button>\n')
        if button6 != '':
            file.write('\t<button id="draw_6" style="color:purple;"><b>'+ button6 + '</b></button>\n')
        if button7 != '':
            file.write('\t<button id="draw_7" style="color:green;"><b>'+ button7 + '</b></button>\n')
        if button8 != '':
            file.write('\t<button id="draw_8" style="color:green;"><b>'+ button8 + '</b></button>\n')
        if button9 != '':
            file.write('\t<button id="draw_9" style="color:brown;"><b>'+ button9 + '</b></button>\n')
        if button10 != '':
            file.write('\t<button id="draw_10" style="color:brown;"><b>'+ button10 + '</b></button>\n')
        file.write('\t<div id="chart_master" style="width:100%; height:85%;">\n')
        file.write('\t<h2 style="color:blue">Click on a Graph button above, to display that graph</h2>\n')
        file.write('\t</div>\n')
        file.write('\n')
        file.write('Author: Nigel Griffiths @mr_nmon generated from HMC REST API using Python\n')
        file.write('Now with Zoom = Left-click and drag. To Reset = Right-click.\n')
        file.write('</body>\n')
        file.write('</html>\n')


    # ----------------------------------------------
    # SPECIFIC FUNCTIONS FOR NEXTRACT FUNCTIONALITY
    # convert HMCdate+time 2017-08-21T20:12:30 to google date+time 2017,04,21,20,12,30
    def googledate(self, date):
        if self.debug:
            print("googledate(%s)"%(date))
    def googledate(self, date):
        if self.debug:
            print("googledate(%s)"%(date))
        d = date[0:4] + "," +  str(int(date[5:7]) -1) + "," + date[8:10] + "," + date[11:13] + "," + date[14:16] + "," + date[17:19]
        return d
    
    def nchart_energy(self, filename, info, data):
        if self.debug:
            print("nchart_energy(%s, info,data)"%(filename))
            print("open:" + filename)
        self.web = open(filename,"w")
        self.output_start(self.web, 'Energy server ' + info['server']+" MTM="+info['mtm']+" Serial="+info['serial'])

        self.output_top(self.web, 1, 'Watts') 
        for row in data:
            self.web.write(",['Date(%s)', %d]\n" %(self.googledate(row['time']),row['watts']))
        self.output_bot(self.web,  1, info['server'] + " -  Electrical power in Watts")

        self.output_top(self.web, 2, 'planar1', 'planar2', 'planar3', 'planar4', 'cpu1', 'cpu2', 'cpu3', 'cpu4', 'cpu5', 'cpu6', 'cpu7', 'cpu8', 'inlet') 
        for row in data:
            self.web.write(",['Date(%s)', %.1f,%.1f,%.1f,%.1f, %.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f, %.1f]\n" %(self.googledate(row['time']),
              row['mb0'],row['mb1'],row['mb2'],row['mb3'],row['cpu0'],row['cpu1'],row['cpu2'],row['cpu3'],row['cpu4'],row['cpu5'],row['cpu6'],row['cpu7'],row['inlet']) )
        self.output_bot(self.web,  2, info['server'] + ' - Temperature in degrees Celsius. planar=System-Planer cpu=POWER8-Chip inlet=Room-Temp')

        self.output_end2(self.web, info['server'],'Electrical power use in Watts','Temperatures in Celsius')
        self.web.close()

    def nchart_ssp(self, filename, info, ssp, header, vios):
        if self.debug:
            print("nchart_ssp(%s, info,data,ssp, header, vios)"%(filename))
            print("open:" + filename)
        self.web = open(filename,"w")
        self.output_start(self.web, 'Shared Storage Pool cluster=' + info['cluster']+' SSP='+info['ssp'])

        self.output_top(self.web, 1, 'Size (GB)', 'Free (GB)')
        for s in ssp:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['size']/1024, s['free']/1024))
        self.output_bot(self.web, 1, info['ssp'] + " - SSP Pool Size/Use statisitics")

        self.output_top(self.web, 2, 'Read (MB/s)', 'Write (MB/s)')
        for s in ssp:
            self.web.write(",['Date(%s)', %.2f,%.2f]\n" %(self.googledate(s['time']), s['readBytes']/1024/1024, -s['writeBytes']/1024/1024))
        self.output_bot(self.web, 2, info['ssp'] +  " - SSP Read & Write MB/s statisitics")

        self.output_top(self.web, 3, 'Read (ms)', 'write (ms)')
        for s in ssp:
            self.web.write(",['Date(%s)', %.3f,%.3f]\n" %(self.googledate(s['time']),
                        s['readServiceTime']/1000000,-s['writeServiceTime']/1000000))
        self.output_bot(self.web, 3, info['ssp'] +  " - SSP Service Time milli-sec statisitics")

        # prepare list of colouns names=  VIOS hostnams
        headline = ""
        for count,viosname in enumerate(header):
            if count == 0:
                headline = "'" + viosname + "'"
            else:
                headline = headline + ", '" + viosname + "'"
        self.output_top_unitstring(self.web, 4, headline)
        for v in vios:
            self.web.write(",['Date(%s)'" %(self.googledate(v['time'])))
            for readkb in v['readKB']:
                self.web.write(",%.2f" % (  readkb))
            for writekb in v['writeKB']:
                self.web.write(",%.2f" % (-writekb))
            self.web.write("]\n")

        self.output_bot(self.web, 4, info['ssp'] + " - VIOS Read & Write statistics")

        self.output_end_ssp(self.web, info['ssp'],'SSP Size','SSP I/O MB/s', 'SSP Service Time msec', 'VIOS MB/s')
        self.web.close()

    def nchart_server(self, filename, info, data):
        if self.debug:
            print("nchart_server(%s, info, data)"%(filename))
            print("open:" + filename)
        details = ' for Server=' + info['name'] + ' MTM & Serial=' + info['mtms']
        self.web = open(filename,"w")
        self.output_start(self.web, 'Server =' + info['name'])

        self.output_top(self.web, 1, 'Available', 'Configured', 'Total', 'Used')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f,%.1f,%.2f]\n" %(self.googledate(s['time']), s['cpu_avail'], s['cpu_conf'], s['cpu_total'], s['cpu_used']))
        self.output_bot(self.web, 1, "CPU core" + details)

        self.output_top(self.web, 2, 'Available', 'Configured', 'Total', 'In-VMs')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f,%.1f,%.1f]\n" %(self.googledate(s['time']), s['mem_avail'], s['mem_conf'], s['mem_total'], s['mem_inVM']))
        self.output_bot(self.web, 2, "Memory in MB" + details)

        self.output_top(self.web, 3, 'Used')
        for s in data:
            self.web.write(",['Date(%s)', %.3f]\n" %(self.googledate(s['time']), s['phype_cpu'] ))
        self.output_bot(self.web, 3, "pHypervisor CPU" + details)

        self.output_top(self.web, 4, 'Configured')
        for s in data:
            self.web.write(",['Date(%s)', %.1f]\n" %(self.googledate(s['time']), s['phype_mem'] ))
        self.output_bot(self.web, 4, "pHypervisor Memory" + details)

        self.output_top(self.web, 5, 'Configured', 'Entitled', 'Used')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f,%.1f]\n" %(self.googledate(s['time']), s['vios_cpu_vp'], s['vios_cpu_entitled'], s['vios_cpu_used'] ))
        self.output_bot(self.web, 5, "VIOS Total CPU" + details)

        self.output_top(self.web, 6, 'Configured', 'Used')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['vios_mem_conf'],s['vios_mem_used'] ))
        self.output_bot(self.web, 6, "VIOS Total Memory" + details)

        self.output_top(self.web, 7, 'Read bytes/s', 'Write bytes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['vios_net_rbytes'],s['vios_net_wbytes'] ))
        self.output_bot(self.web, 7, "VIOS Total Network I/O read:write bytes" + details)

        self.output_top(self.web, 8, 'Reads/s', 'Writes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['vios_net_reads'],s['vios_net_writes'] ))
        self.output_bot(self.web, 8, "VIOS Total Network I/O reads:writes" + details)


        self.output_top(self.web, 9, 'Read bytes/s', 'Write bytes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['vios_fc_rbytes'],s['vios_fc_wbytes'] ))
        self.output_bot(self.web, 9, " VIOS Total Disk read:write bytes" + details)

        self.output_top(self.web, 10, 'Reads/s', 'Writes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['vios_fc_reads'],s['vios_fc_writes'] ))
        self.output_bot(self.web, 10, "VIOS Total Disk reads:writes" + details)

        self.output_end_all(self.web, info['name'],'Server CPU','Server Memory','pHype CPU','pHype Memory','VIOS CPU','VIOS Memory','VIOS Net I/O','VIOS Net Packets','VIOS Disk I/O','VIOS Disk Packets')
        self.web.close()


    def nchart_lpar(self, filename, info, data):
        if self.debug:
            print("nchart_lpar(%s, info, data)"%(filename))
        details = ' for LPAR=' + info['lparname'] + ' Server=' + info['server'] + ' MTM & Serial=' + info['mtms'] + ' State=' + info['lparstate']
        self.web = open(filename,"w")
        self.output_start(self.web, info['lparname'])
        self.output_start(self.web, 'LPAR =' + info['lparname'])

        self.output_top(self.web, 1, 'VP', 'Entitled', 'Used')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f,%.1f]\n" %(self.googledate(s['time']), s['cpu_vp'], s['cpu_entitled'], s['cpu_used']))
        self.output_bot(self.web, 1, 'CPU cores' + details)

        self.output_top(self.web, 2, 'RAM (MB)')
        for s in data:
            self.web.write(",['Date(%s)', %.1f]\n" %(self.googledate(s['time']), s['mem_conf']))
        self.output_bot(self.web, 2, 'Memory configured' + details)

        self.output_top(self.web, 3, 'Read bytes/s', 'Write Bytes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['net_rbytes'],s['net_wbytes'] ))
        self.output_bot(self.web, 3, 'Network bytes/sec' + details)

        self.output_top(self.web, 4, 'Reads/s', 'Writes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['net_reads'],s['net_writes'] ))
        self.output_bot(self.web, 4, 'Network Ops/sec' + details)

        self.output_top(self.web, 5, 'Read bytes/s', 'Write Bytes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['disk_rbytes'],s['disk_wbytes'] ))
        self.output_bot(self.web, 5, 'Disk bytes/sec' + details)

        self.output_top(self.web, 6, 'Reads/s', 'Writes/s')
        for s in data:
            self.web.write(",['Date(%s)', %.1f,%.1f]\n" %(self.googledate(s['time']), s['disk_reads'],s['disk_writes'] ))
        self.output_bot(self.web, 6, 'Disk Ops/sec' + details)

        self.output_end_all(self.web, info['lparname'],'LPAR CPU','LPAR Memory','Network bytes/s','Network Ops','Disk Bytes/s','Disk Ops')
        self.web.close()
# The End
