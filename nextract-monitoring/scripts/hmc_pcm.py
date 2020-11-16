#!/usr/bin/python3
# Version 10
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as ET
import json
import sys
import os
import time
import atexit

class HMC(object):
    def __init__(self,hmc, user, pw):
        '''Class initialisation is used to login to the HMC
           registers the clean up function for automatic log-off even if the python program crashes
           Arguments: 1=hostname of HMC or IP address, 2=HMC username with access to stats, 3=HMC user password
           Returns: the HMC object'''
        self.HMCname = ''
        self.token = ''
        self.debug = False
        #self.debug = True
        self.connected = False
        self.logon(hmc, user, pw)
        atexit.register(self.cleanup)

    def cleanup(self):
        '''Internal function:
            Logoff the HMC if the user doesn't so we don't leave 100's sessions running
            Arguments: none
            Returns = never'''
        if self.connected:
                logoffheaders = {'X-API-Session' : self.token }
                logoffUrl =  'https://'+self.HMCname+':12443/rest/api/web/Logon'
                ret = requests.delete(logoffUrl,headers=logoffheaders,verify=False)

    def set_debug(self, on_off):
        ''' Set the internal debug to True or False then this library get a lot more verbose 
            Arguments: 1=True or False
            Returns: nothing
            example hmc.set_debug(True) or hmc_pcm.debug(False) '''
        if on_off == True:
            if os.path.isdir("debug") == False:
                print("Creating sub-directory: debug")
                os.mkdir("debug")
            self.debug = True
            print("DEBUG: debug set to True")
        else:
            self.debug = False
            print("DEBUG: debug set to False")

    def save_to_file(self, filename, string):
        ''' Simple debugging option to save data like XML or JSON for learning and diags
            Note: it assumes a sub-directory called debug 
            Arguments: 1=the filename to open in the debug sub-directory 2=the data to write to the file
            Returns: nothing'''
        filename = 'debug/' + filename
        file = open(filename,"w")
        file.write(string)
        file.close()

    def save_json_txt_to_file(self, filename, string):
        ''' Simple debugging option to convert JSON to human readable style and save to a file for learning and diags
            Note: it assumes a sub-directory called debug 
            Arguments: 1=the filename to open in the debug sub-directory 2=raw JSON data to write to the file
            Avoids unreadable JSON data typically with whole file on a line DOH! 
            Returns: nothing'''
        readable = json.dumps(json.loads(string),indent=4)
        self.save_to_file(filename,readable)

    def read_from_file(self, filename):
        ''' Simple debugging option to read a saved file
            Note: it assumes a sub-directory called debug 
            Arguments: 1=the filename to read in the debug sub-directory
            Returns: the file contents as a string'''
        filename = 'debug/' + filename
        file = open(filename,"r")
        string = file.read()
        file.close()
        return string

    def check_connected(self,context):
        '''Internal function
           Sanity check that we have logged on to the HMC = avoid exceptions
           Arguments: 1= string to explain what the module is doing - only used to report the error
           Returns: never if there is no connection'''
        if self.connected == False:
            print("Attempt to " + context + " when not logged on. Halting!")
            sys.exit(42)

    def logon(self, hmc, user, passwd):
        '''Internal function called from the class initialisation
           Arguments: same as class initialisation
           a) set up put request to the HMC for log-on
           b) check the status as username/password or even HMC details can be wrong
           c) if logon fails exit - there is nothing further that can be done
           d) convert returned text to XML and extract the authorisation token
           e) return the token which is used for all subsequent HMC interactions '''
        if self.connected:
            print("Attempt to logon when already logged on. Halting!")
            sys.exit(42)
        if self.debug:
            print("DEBUG:logon()")
            print("DEBUG:Switching off ugly Security Warnings 'Unverified HTTPS request is being made'")
        # HMC appears not to have a genuine recognised CA certficate
        # HMC Users can set that up if they desire
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.HMCname = hmc
        logonheaders = {'Content-Type': 'application/vnd.ibm.powervm.web+xml; type=LogonRequest'}
        logonUrl =  'https://'+self.HMCname+':12443/rest/api/web/Logon'
        logonPayload = '<LogonRequest schemaVersion="V1_0" xmlns="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/" xmlns:mc="http://www.ibm.com/xmlns/systems/power/firmware/web/mc/2012_10/"><UserID>' + user + '</UserID><Password>' + passwd + '</Password></LogonRequest>'
        ret = requests.put(logonUrl,data=logonPayload,headers=logonheaders,verify=False)
        if ret.status_code != 200:
                print("Error: Logon failed error code=%d url=%s" %(ret.status_code,logonUrl))
                if self.debug:
                        print("DEBUG: Returned:%s" %(ret.text))
                # Do not return if we failed to logon
                sys.exit(ret.status_code)
        #Extract from the XML the token
        xmlResponse = ET.fromstring(ret.text)
        self.token = xmlResponse[1].text
        if self.debug:
                print("DEBUG:Log on response=%d and got Token=\n----\n%s\n----" %(ret.status_code, self.token))
        self.connected = True
    
    def logoff(self):
        '''Disconnect from the HMC
           This is actually a HTTP delete request (delete the token)
           Arguments: none
           Returns::
           if the logoff fails this function exits the program
           if the logoff works it returns nothing'''
        if self.debug:
            print("DEBUG:Logoff()")
        self.check_connected("logoff")
        logoffheaders = {'X-API-Session' : self.token }
        logoffUrl =  'https://'+self.HMCname+':12443/rest/api/web/Logon'
        ret = requests.delete(logoffUrl,headers=logoffheaders,verify=False)
        rcode = ret.status_code
        # delete can respond with these three good values
        if rcode == 200 or rcode == 202 or rcode == 204:
            if self.debug:
                print("DEBUG:Successfully disconnected from the HMC (code=%d)" %(rcode))
            self.connected = False
        else:
            print("Error: Logoff failed error code=%d url=%s data=%s" %(rcode, logoffUrl, ret.text))
            sys.exit(rcode)

    # ------ Deal with initial preferences below ---#
    def get_preferences_ssp(self):
        '''Get the XML list of Shared Storage Pools the HMC knows about and the settings
           Arguments: none
           Returns: XML preferences from the HMC
        '''
        return self.__internal__get_preferences('/SSP')

    def get_preferences_pcm(self):
        '''Get the XML list of Managed Server connected to the HMC and the settings
           Arguments: none
           Returns: XML preferences from the HMC
        '''
        return self.__internal__get_preferences('')

    def get_stripped_preferences_ssp(self):
        '''Get the XML list of Shared Storage Pools the HMC knows about and the settings
           and remove the garbage lines at the top and bottom that the HMC will not accept but sent us!
           Arguments: none
           Returns: XML preferences from the HMC without the fluff
        '''
        return self.strip_preferences_ssp(self.__internal__get_preferences('/SSP'))

    def get_stripped_preferences_pcm(self):
        '''Get the XML list of Managed Server connected to the HMC and the settings
           and remove the garbage lines at the top and bottom that the HMC will not accept but sent us!
           Arguments: none
           Returns: XML preferences from the HMC  without the fluff
        '''
        return self.strip_preferences_pcm(self.__internal__get_preferences(''))

    def get_server_details_pcm(self):
        '''Get the XML list of Managed Server connected to the HMC and the settings
           and remove the garbage lines at the top and bottom that the HMC will not accept but sent us!
           then convert the details to python array of dictionaries
           Arguments: none
           Returns: Servers and settings array of dictionaries - one per Server
        '''
        return self.parse_prefs_pcm(self.strip_preferences_pcm(self.__internal__get_preferences('')))

    def __internal__get_preferences(self, extension):
        ''' INTERNAL function that gets the HMC Preferences
            Arguments: a string either empty the extra bit needed on the end of the URL
            Returns: the data fromt he HMC as a string
        '''
        if self.debug:
            print("DEBUG:__internal__get_preferences()")
        self.check_connected("get_preferences")
        prefHeaders = {'X-API-Session' : self.token}
        prefUrl = 'https://'+self.HMCname+':12443/rest/api/pcm/preferences'+extension
        ret = requests.get(prefUrl, headers=prefHeaders,verify=False)
        if self.debug:
            self.save_to_file("preferences.xml", ret.text)
        if ret.status_code != 200:
            print("Error: GET preferences error code=%d header=%s url=%s" %(ret.status_code, preHeaders, prefUrl))
            if ret.status_code == 401:
                    print("Unauthorisied: wrong HMC hostname/User/Password")
            if self.debug:
                    print("DEBUG:Returned:%s" %( ret.text))
            return ""
        return ret.text
    
    def strip_preferences_ssp(self,pref_string):
        ''' Removes the first and last few lines of SSP XML preferences
            Arguments: the XML string
            Returns: a smaller XML string '''
        return self.__internal__strip_preferences(pref_string,"<ManagementConsolePCMSSPPreference")

    def strip_preferences_pcm(self,pref_string):
        ''' Removes the first and last few lines of Server XML preferences
            Arguments: the XML string
            Returns: a smaller XML string '''
        return self.__internal__strip_preferences(pref_string,"<ManagementConsolePcmPreference")

    def __internal__strip_preferences(self,pref_string,findstring):
        '''Internal function
           Uses string manipulation to find the data acceptable to the HMC during set preferences
           and removed the garbage preamble
           then find the start of the junk trailer and removing the following bits 
           Arguemtns: 1=the orininal returned preferences 2=the string which is used to identify the real data
           Returns: the reduced preferences strings
        '''
        if self.debug:
            print("DEBUG:__internal__strip_preferences(%s,%s)" % (pref_string,findstring))
        #Find the first part of what we need then remove everything before the offset
        i = pref_string.find(findstring)
        pref_string = pref_string[i : ]
        # rip off the trailer
        #Find the first part of what we don't need at the end then remove everything after the offset
        i = pref_string.find("</content>")
        pref_string = pref_string[ :i ]
        return pref_string

    def parse_prefs_ssp(self,preferences):
        ''' Convert Shared Storage Pools XML preferences to python data structures
            This is made very complex by the use of XML namespaces see yyy and ns variables for details
            Arguments: 1=the preferences
            Returns: an array (list) of dictionaries - one per SSP
        '''
        # Convert the GET preferenses response TEXT to XML 
        #    So we can extract the Management Server UUID
        if self.debug:
            print("DEBUG:parse_prefs_ssp(prefs)")
        xml = ET.fromstring(preferences)
        result = []
        ns = {'yyy': 'http://www.ibm.com/xmlns/systems/power/firmware/pcm/mc/2012_10/'}
        for this_ssp in xml.findall('yyy:ManagementConsoleSSPPreference',ns):
            cluster = this_ssp.find('yyy:ClusterName',ns).text
            ssp     = this_ssp.find('yyy:SSPName',ns).text
            uuid    = this_ssp.find('yyy:SSPUuId',ns).text
            agg     = this_ssp.find('yyy:AggregationEnabled',ns).text
            mon     = this_ssp.find('yyy:MonitorEnabled',ns).text
            #print('FOUND cluster=%16s ssp=%16s uuid=%32s agg=%5s mon=%5s' %(cluster, ssp, uuid, agg, mon))
            result.append({'cluster': cluster, 'pool':ssp, 'uuid':uuid, 'agg':agg, 'mon': mon})
        return result

    def parse_prefs_pcm(self,preferences):
        ''' Convert Server XML preferences to python data structures
            This is made very complex by the use of XML namespaces see "yyy" and "ns" variables for details
            and the required data is at different levels
            Note AtomID is called ServerID in the documentation but are the one and same thing 
            Arguments: 1=the preferences
            Returns: an array (list) of dictionaries - one per Server
            side effect it saves the XML version of the preferences in self.stats_xml
        '''
        # Convert the GET preferenses response TEXT to XML 
        #    So we can extract the Management Server UUID
        if self.debug:
            print("DEBUG:parse_prefs_pcm(prefs)")
        self.stats_xml = ET.fromstring(preferences)
        result = []
        ns = {'yyy': 'http://www.ibm.com/xmlns/systems/power/firmware/pcm/mc/2012_10/'}
        for this_server in self.stats_xml.findall('yyy:ManagedSystemPcmPreference',ns):
            name    = this_server.find('yyy:SystemName',ns).text
            capable = this_server.find('yyy:EnergyMonitoringCapable',ns).text
            lterm   = this_server.find('yyy:LongTermMonitorEnabled',ns).text
            agg     = this_server.find('yyy:AggregationEnabled',ns).text
            sterm   = this_server.find('yyy:ShortTermMonitorEnabled',ns).text
            compute = this_server.find('yyy:ComputeLTMEnabled',ns).text
            energy  = this_server.find('yyy:EnergyMonitorEnabled',ns).text
            # get the atomid from the meta record
            meta   = this_server.find('yyy:Metadata',ns)
            atom   = meta.find('yyy:Atom',ns)
            atomid = atom.find('yyy:AtomID',ns).text

            #print('FOUND Server name=%16s agg=%-5s capable=%-5s enabled=%-5s' %(name, agg, capable, enabled))
            #print('FOUND Server name=%10s agg=%s capable=%s enabled=%s atomid=%s' %(name, agg, capable, enabled, atomid))
            result.append({'name': name, 'capable':capable, 'lterm':lterm, 'agg':agg, 'sterm':sterm,  'compute':compute, 'energy':energy, 'atomid': atomid})
        return result

    def set_energy_flags(self,server,value):
        '''Set the energy monitoring enabled flag so the HMC starts collecting the watts and Celsius stats
           Arguments: 1 the server name - as seen on the HMC an invalid name is ignored
           Returns: none '''
        if self.debug:
            print("DEBUG:set_energy_flags(%s)"%(server))
        ns = {'yyy': 'http://www.ibm.com/xmlns/systems/power/firmware/pcm/mc/2012_10/'}
        for this_server in self.stats_xml.findall('yyy:ManagedSystemPcmPreference',ns):
            name    = this_server.find('yyy:SystemName',ns).text
            if name == server:
                agg     = this_server.find('yyy:AggregationEnabled',ns)
                enabled = this_server.find('yyy:EnergyMonitorEnabled',ns)
                agg.text = value
                enabled.text = value
                # enabled.text = 'false'  # For testing only
                break

    def set_preferences_pcm(self):
        '''Sends the self.stats_xml to the HMC to change the current settings
           via the HTTP post request
           self.stats_xml saved in the function get_server_details_pcm and/or parse_prefs_pcm
           self.stats_xml updated by the function set_preferences_pcm
           Arguments: 1 none
           Returns: none 
           if the HMC returns an error data is dumped to the screen and it logs off the HMC'''
        if self.debug:
            print("DEBUG:set_preferences_pcm()")
        self.check_connected("set_preferences_pcm")
        if self.debug:
            tree = ET.ElementTree(self.stats_xml)
            filename= 'debug/' + 'energy-prefs-updated.xml'
            tree.write(filename)

        postHeaders = {'Content-Type': 'application/xml', 'X-API-Session' : self.token }
        postUrl = 'https://'+self.HMCname+':12443/rest/api/pcm/preferences'
        xmlStr = ET.tostring(self.stats_xml)
        r = requests.post(postUrl, headers=postHeaders, data=xmlStr, verify=False)
        if r.status_code != 200:
            print("Error: post preferences error code=%d header=%s url=%s" %( r.status_code,postHeaders,postUrl))
            if self.debug:
                print("DEBUG:URL:" + postUrl)
                print("DEBUG:Body:")
                print(xmlStr)
                print("DEBUG:Returned%s:" %(r.text))
            HMClogoff()

    def set_preferences_ssp(self,postBody):
        ''' This function assume as there is likely to be only a few SSP that you want stats from all of them
           Arguments: the SSP XML stripped preferences string
           After removing a number of pointless options from the preferences
           the function replace false with true for AggregationEnabled and MonitorEnabled
           then using a HTTP post request sends them to the HMC
           Returns: the amended preferences  
           if the HMC returns an error data is dumped to the screen and it logs off the HMC'''
        if self.debug:
            print("DEBUG:set_preferences_ssp()")
        self.check_connected("set_preferences_ssp")
        # We assume the preferences have been stripped of head and tail
        # Note ALL SSP's can be enables and here we force them all Enabled
        # Note that currently the prefereences have AggregationEnabled=true as a default - but we may not need that
        # It was remommended to force it anyway, so we set two flags to true
        # Set the flags to true for each SSP
        # Note: kb= and kxe= are in different orders!! But we can strip them out for a simpler replace
        postBody = postBody.replace(' kb="UOD"',   '')
        postBody = postBody.replace(' kb="ROO"',   '')
        postBody = postBody.replace(' kb="ROR"',   '')
        postBody = postBody.replace(' kxe="false"','')
        postBody = postBody.replace(' kxe="true"', '')
        # Set AggregationEnabled=true & MonitorEnabled=true
        # Not clear if the Aggregate flag is really needed for ProcessedMetrics
        postBody = postBody.replace('<AggregationEnabled>false</AggregationEnabled>',\
                                    '<AggregationEnabled>true</AggregationEnabled>')
        postBody = postBody.replace('<MonitorEnabled>false</MonitorEnabled>',\
                                    '<MonitorEnabled>true</MonitorEnabled>')
        if self.debug:
            self.save_to_file ("SSP-prefs-updated.xml", postBody)
        postHeaders = {'Content-Type': 'application/xml', 'X-API-Session' : self.token }
        postUrl = 'https://'+self.HMCname+':12443/rest/api/pcm/preferences/SSP'
        r = requests.post(postUrl, headers=postHeaders, data=postBody, verify=False)
        if r.status_code != 200:
            print("Error: post preferences error code=%d header=%s url=%s" %( r.status_code,postHeaders,postUrl))
            if self.debug:
                    print("DEBUG:URL:%s" %(postUrl))
                    print("DEBUG:Body:%s" %(postBody))
                    print("DEBUG:Returned:%s" %(r.text))
            HMClogoff()
        return postBody

    def get_filenames_ssp(self, SSPid, SSP):
        '''For Shared Storage Pools set the URL and resource name
           and call get_filenames directly returning the result 
           Arguments: 1=SSPid from the preferences 2=the Pool name
           Returns: an array of JSON filenames '''
        if self.debug:
            print("DEBUG:get_filenames_ssp(%s,%s)" % (SSPid, SSP))
        url =  'https://'+self.HMCname+':12443/rest/api/pcm/SharedStoragePool/'+SSPid+'/ProcessedMetrics'
        xxx = "SSP-" + SSP
        return self.get_filenames(url, xxx)

    def get_energy(self, Atomid, Server):
        '''For energy stats set the URL and resource name
           and call get_filenames directly 
           then use get_stats to fetch the JSON data returning the result 
           Arguments: 1=AtomId also call ServerId 2=Server by name for any error reporting
           results JSON data - for energy there is only one data file'''
        if self.debug:
            print("DEBUG:get_energy(atom=%s, Server=%s)"%(Atomid, Server))
        JSONfiles = self.get_filenames_energy(Atomid, Server) # XML of filenames
        if len(JSONfiles) <= 0:
            return None
        return self.get_stats(JSONfiles[0]['url'],JSONfiles[0]['filename'], Server) # returns JSON stats

    def get_filenames_energy(self, Atomid, Server):
        '''For energy stats set the URL and resource name
           and call get_filenames directly returning the result 
           Arguments: 1=AtomId also call ServerId 2=Server by name for any error reporting
           results the array of filenames (only one for energy stats)'''
        if self.debug:
            print("DEBUG:get_filenames_energy(%s,%s)" % (Atomid, Server))
        url =  'https://'+self.HMCname+':12443/rest/api/pcm/ManagedSystem/'+Atomid+'/ProcessedMetrics?Type=Energy' 
        xxx = "Energy-" + Server
        return self.get_filenames(url, xxx)
    
    def get_filenames_server(self, Atomid, Server):
        '''For Server and LPAR stats set the URL and resource name
           and call get_filenames directly returning the result
           Arguments: 1=AtomId also call ServerId 2=Server by name for any error reporting
           results the array of filenames '''
        if self.debug:
            print("DEBUG:get_filenames_server(%s,%s)" % (Atomid, Server))
        url =  'https://'+self.HMCname+':12443/rest/api/pcm/ManagedSystem/'+Atomid+'/ProcessedMetrics' 
        xxx = "Server-" + Server
        return self.get_filenames(url, xxx)
    
    def get_filenames(self, fileUrl, resource_name):
        '''Given the full URL for the file of filename - fetch it from the HMC
           Arguments: 1=URL of file of filenames 2=resource for any error reporting
           parse the XML for the actual JSON filenames of stats data
           results array of dictionaries containing the file and full JSON file URL'''
        if self.debug:
            print("DEBUG:get_filenames(%s,%s)" % (fileUrl, resource_name))
        self.check_connected("get_filenames")
        result = []
        fileHeaders = {'X-API-Session': self.token, 'Accept': 'application/atom+xml' }

        r = requests.get(fileUrl,headers=fileHeaders,verify=False)
        if self.debug:
                file_name = resource_name + "-filenames" + ".xml"
                self.save_to_file(file_name, r.text)
        if r.status_code != 200:
                print("Error %d: returned for GET \"%s\" file of filenames" % (r.status_code,resource_name))
                if r.status_code == 204:
                    print("Hint: 204=No Content")
                if self.debug:
                    print("DEBUG:Error %s: Details\n\tHeader=%s \n\tURL=%s" % (r.status_code,str(fileHeaders),fileUrl))
                    print("DEBUG:Returned:%s" %(r.text))
                return result
        # Parse the file of filenames
        refResponse = ET.fromstring(r.text)
        for reffeed in refResponse:
            if 'entry' in reffeed.tag:
                for entry in reffeed:
                    if 'title' in entry.tag:
                        name = entry.text
                    if 'link' in entry.tag:
                        href = entry.get('href')
                        if self.debug:
                            print("DEBUG:JSON URL |%s|" % (href))
                            print("DEBUG:JSON filename |%s|" % (name))
                        result.append({'filename': name, 'url': href})
        return result

    def get_filename_from_xml(self, xmltext):
        '''For Server or LPAR stats from the HMC there many files of filenames
           this function find the only URL and filename is such a XML file
           Arguments: the server or LPAR XML file of a single filename
           Returns: the filename and URL strings '''
        if self.debug:
            print("DEBUG:get_filenamefrom_xml(%s)" % (xmltext))
        refResponse = ET.fromstring(xmltext)
        for reffeed in refResponse:
            if 'entry' in reffeed.tag:
                for entry in reffeed:
                    if 'title' in entry.tag:
                        name = entry.text
                    if 'link' in entry.tag:
                        href = entry.get('href')
                        if self.debug:
                            print("DEBUG:JSON URL |%s|" % (href))
                            print("DEBUG:JSON filename |%s|" % (name))
        return name, href

    def get_stats(self, JSON_url, JSON_file, resource_name):
        '''Fest the JSON file from the HMC, 
           Arguments: 1=URL on the HMC 
                     2=filename (used to save a copy if debug=True and error logging 
                     3=resouce name for error loging
           Returns: JSON data'''
        #self.debug = 1
        if self.debug:
            print("DEBUG:get_stats(url=%s, file=%s, resourse=%s)" % (JSON_url, JSON_file, resource_name))
        self.check_connected("get_stats")
        jsonHeaders = {'X-API-Session' : self.token }
        r = requests.get(JSON_url,headers=jsonHeaders,verify=False)
        if self.debug:
            file_name = "Stats--" + resource_name + "-" + JSON_file
            self.save_to_file(file_name, r.text)
        if r.status_code != 200:
            print("Error: get %s JSON file error code=%d filename=%s" %(resource_name, r.status_code, JSON_file))
            if self.debug:
                    print("DEBUG:Returned:%s" %(r.text))
            return ''
        return r.text
    
    def extract_ssp_info(self,stats):
        ''' This function extracts the header information from the JSON file for SSP
            Arguments: the SSP JSON stats string
            Returns: a dictionary of facts about the data set
        '''
        #self.debug = 1
        if self.debug:
            print("DEBUG:extract_ssp_info(stats)")
        data = json.loads(stats) # convert to JSON
        sspName        = data["sspUtil"]["utilInfo"]["name"]
        clusterName    = data["sspUtil"]["utilInfo"]["clusterName"]
        frequency      = data["sspUtil"]["utilInfo"]["frequency"]
        startTimeStamp = data["sspUtil"]["utilInfo"]["startTimeStamp"]
        endTimeStamp   = data["sspUtil"]["utilInfo"]["endTimeStamp"]
        metricType     = data["sspUtil"]["utilInfo"]["metricType"]
            
        if self.debug:
            print("\tSSP:%s cluster=%s frequency=%s type=%s" % \
                    (sspName,clusterName,frequency,metricType ))
            print("\tSSP:%s Start=%s" % (sspName,startTimeStamp))
            print("\tSSP:%s End  =%s" % (sspName,endTimeStamp))
        ret = { 'ssp': sspName, 'cluster': clusterName, 'frequency': frequency, 'start': startTimeStamp, 'end': endTimeStamp }
        return ret
    
    def extract_ssp_totals(self,stats):
        ''' This function extracts the stats from the JSON file for the whole SSP
            Arguments: the SSP JSON stats string
            Returns: an array of dictionaries of the whole SSP stats - one dictionary per snapshot
        '''
        #self.debug = 1
        if self.debug:
            print("DEBUG:extract_ssp_totals(stats)")
        data = json.loads(stats) # convert to JSON
        ret = []
        bad=0
        good=0
        for sample in data["sspUtil"]["utilSamples"]:
            # NOTE: ERRORS ARE AT SSP LEVEL EVEN IF IT IS A NODE ERROR
            try:
                timeStamp   = sample['sampleInfo']['timeStamp']
                timeStamp   = timeStamp[0:19] # strip off fractions of a second
                free        = sample['poolUtil']['free'][0]
                size        = sample['poolUtil']['size'][0]
                numOfReads  = sample['poolUtil']['numOfReads'][0]
                numOfWrites = sample['poolUtil']['numOfWrites'][0]
                readBytes  = sample['poolUtil']['readBytes'][0]
                writeBytes = sample['poolUtil']['writeBytes'][0]
                readServiceTime = sample['poolUtil']['readServiceTime'][0]
                writeServiceTime = sample['poolUtil']['writeServiceTime'][0]
                entry = {'time':timeStamp[0:19], 'size':size, 'free':free, 
                               'numOfReads':numOfReads, 'numOfWrites':numOfWrites, 
                               'readBytes':readBytes, 'writeBytes':writeBytes,
                               'readServiceTime':readServiceTime, 'writeServiceTime':writeServiceTime }
                ret.append(entry)
                good += 1
                if self.debug:
                    print("DEBUG:%s size=%d free=%d OPs:read=%6d write=%6d Bytes:read=%9d write=%9d ServiceTime:read=%9d write=%9d"
                           %(timeStamp,size,free,numOfReads,numOfWrites,readBytes,writeBytes,readServiceTime,writeServiceTime))
            except:
                if self.debug:
                    print("Data includes error reports errID=%s"%(sample["sampleInfo"]["errorInfo"][0]["errId"]))
                    print("- errMsg=%s"%(sample["sampleInfo"]["errorInfo"][0]["errMsg"]))
                    #print(sample)
                bad += 1
                continue
        if self.debug:
            print("extract_ssp_totals returning good=%d bad=%d"%(good,bad))
        return ret
    
    def extract_ssp_vios(self,stats):
        ''' This function extracts the stats from the JSON file for VIOS's of the SSP
            Arguments: the SSP JSON stats string
            Returns: an array of dictionaries of the SSP VIOS stats - one dictionary per snapshot
        '''
        #self.debug = 1
        if self.debug:
            print("DEBUG:extract_ssp_vios(stats)")
        data = json.loads(stats) # convert to JSON
        if self.debug:
            self.save_to_file("ssp_vios_string.json",str(data))
        viosstats = []
        header = []
        good = 0
        bad = 0
        for sample in data["sspUtil"]["utilSamples"]:
            nname=[]
            nrbytes=[]
            nwbytes=[]
            try:
                timeStamp = sample['sampleInfo']['timeStamp']
                timeStamp = timeStamp[0:19]
                entry = {'time':timeStamp }
                for count,node in enumerate(sample['poolUtil']['nodeUtil']):
                    # Remove any domain name to shorten the VIOS hostname, long name are horrid on graphs
                    tmp = node['name'].split(".")
                    viosname = tmp[0]
                    nname.append(viosname)
                    nrbytes.append(node[ 'readBytes'][0]/1024)
                    nwbytes.append(node['writeBytes'][0]/1024)
                entry = {'time':timeStamp[0:19], 'readKB': nrbytes, 'writeKB': nwbytes }
                viosstats.append(entry)
                good = good +1
            except:
                bad = bad+1
        if self.debug:
            print("extract_ssp_vios(): good stats:%d errors:%d"%(good,bad))
        if len(viosstats) == 0:
           return header,viosstats  # bail out with no data

        for vios in nname:  # list the vios names and units from the last sample (finger crossed)
            header.append(vios + "-Read-KBs")
        for vios in nname:
            header.append(vios + "-Write-KBs")
        if self.debug:
            print("extract_ssp_vios: good=%d bad=%d len(header)=%d len(viosstats)=%d"%(good,bad,len(header),len(viosstats)))
        return header, viosstats
    
    def extract_server_info(self,data):
        ''' This function extracts the header information from the JSON file for Server
            Arguments: the Server JSON stats string
            Returns: a dictionary of facts about the data set
        '''
        if self.debug:
            print("DEBUG:extract_server_info(data)")
        jdata = json.loads(data)
        u = jdata["systemUtil"]["utilInfo"]
        name = u['name']
        mtms = u['mtms']
        mtype = u['metricType']
        freq = str(u['frequency'])
        stime = u['startTimeStamp']
        etime = u['endTimeStamp']
        result = { "name":name,"mtms":mtms,"mtype":mtype,"freq":freq,"stime":stime,"etime":etime }
        return result

    def extract_server_stats(self,data):
        ''' This function extracts the stats from the JSON file for the whole Server and sum VIOS stats
            Arguments: the Server JSON stats string
            Returns: an array of dictionaries of the whole Server& sum of VIOS  stats - one dictionary per snapshot
        '''
        if self.debug:
            print("DEBUG:extract_server_stats(data)")
        jdata = json.loads(data)
        # get Server name
        name = jdata["systemUtil"]["utilInfo"]['name']
        firstTime = True
        errors = 0
        count = 0
        statslist = []
        headerline = 'sampleTime, cpu_total, cpu_used, cpu_avail, cpu_conf, mem_avail, mem_total, mem_conf, mem_inVM, vios_mem_conf, vios_mem_used, vios_net_rbytes, vios_net_wbytes, vios_net_reads, vios_net_writes, vios_proc_vp, vios_proc_entitled, vios_proc_used, vios_fc_rbytes, vios_fc_wbytes, vios_fc_reads, vios_fc_writes'

        for sample in jdata['systemUtil']['utilSamples']:
            status = sample['sampleInfo']['status']
            sampletime = sample['sampleInfo']['timeStamp']
            if status != 0 :
                errmsg1 = "None"
                try:
                    errmsg = sample['sampleInfo']['errorInfo'][0]['errMsg'] 
                except:
                    print("Oh dear status non-zero but there is now error message . . . continuing")
                print("*** Error Server %s: status=%d (not zero)\n**** mgs=%s" %(name,status,errmsg))
                errors+= 1
                if errors > 2:
                    break
            else :
                count += 1
                cpu_avail  = sample['serverUtil']['processor']['availableProcUnits'][0]
                cpu_conf   = sample['serverUtil']['processor']['configurableProcUnits'][0]
                cpu_total  = sample['serverUtil']['processor']['totalProcUnits'][0]
                cpu_used   = sample['serverUtil']['processor']['utilizedProcUnits'][0]
        
                mem_avail  = sample['serverUtil']['memory']['availableMem'][0]
                mem_conf   = sample['serverUtil']['memory']['configurableMem'][0]
                mem_total  = sample['serverUtil']['memory']['totalMem'][0]
                mem_inVM   = sample['serverUtil']['memory']['assignedMemToLpars'][0]

                phype_mem  = sample['systemFirmwareUtil']['assignedMem'][0]
                phype_cpu  = sample['systemFirmwareUtil']['utilizedProcUnits'][0]

                vios_mem_conf = 0.0
                vios_mem_used = 0.0
                vios_net_rbytes = 0.0
                vios_net_wbytes = 0.0
                vios_net_reads  = 0.0
                vios_net_writes = 0.0
                vios_proc_vp       = 0.0
                vios_proc_entitled = 0.0
                vios_proc_used     = 0.0
                vios_fc_rbytes = 0.0
                vios_fc_wbytes = 0.0
                vios_fc_reads  = 0.0
                vios_fc_writes = 0.0
                try:
                  for v in sample['viosUtil']:
                    vios_mem_conf += v['memory']['assignedMem'][0]
                    vios_mem_used += v['memory']['utilizedMem'][0]
                    if 'genericAdapters' in v['network']:
                        for n in v['network']['genericAdapters']:
                            vios_net_rbytes += n['receivedBytes'][0]
                            vios_net_wbytes += n['sentBytes'][0]
                            vios_net_reads  += n['receivedPackets'][0]
                            vios_net_writes += n['sentPackets'][0]
                    if 'sharedAdapters' in v['network']:
                        for n in v['network']['sharedAdapters']:
                            vios_net_rbytes += n['receivedBytes'][0]
                            vios_net_wbytes += n['sentBytes'][0]
                            vios_net_reads  += n['receivedPackets'][0]
                            vios_net_writes += n['sentPackets'][0]
                    if 'virtualEthernetAdapters' in v['network']:
                        for n in v['network']['virtualEthernetAdapters']:
                            vios_net_rbytes += n['receivedBytes'][0]
                            vios_net_wbytes += n['sentBytes'][0]
                            vios_net_reads  += n['receivedPackets'][0]
                            vios_net_writes += n['sentPackets'][0]
                    if 'sriovLogicalPorts' in v['network']:
                        for n in v['network']['sriovLogicalPorts']:
                            vios_net_rbytes += n['receivedBytes'][0]
                            vios_net_wbytes += n['sentBytes'][0]
                            vios_net_reads  += n['receivedPackets'][0]
                            vios_net_writes += n['sentPackets'][0]
                    vios_proc_vp       += v['processor']['maxVirtualProcessors'][0]
                    vios_proc_entitled += v['processor']['entitledProcUnits'][0]
                    vios_proc_used     += v['processor']['utilizedProcUnits'][0]
                    if 'genericVirtualAdapters' in v['storage']:
                        for fc in v['storage']['genericVirtualAdapters']:
                            vios_fc_rbytes += fc['readBytes'][0]
                            vios_fc_wbytes += fc['writeBytes'][0]
                            vios_fc_reads  += fc['numOfReads'][0]
                            vios_fc_writes += fc['numOfWrites'][0]
                    if 'genericPhysicalAdapters' in v['storage']:
                        for fc in v['storage']['genericPhysicalAdapters']:
                            vios_fc_rbytes += fc['readBytes'][0]
                            vios_fc_wbytes += fc['writeBytes'][0]
                            vios_fc_reads  += fc['numOfReads'][0]
                            vios_fc_writes += fc['numOfWrites'][0]
                    if 'fiberChannelAdapters' in v['storage']:
                        for fc in v['storage']['fiberChannelAdapters']:
                            vios_fc_rbytes += fc['readBytes'][0]
                            vios_fc_wbytes += fc['writeBytes'][0]
                            vios_fc_reads  += fc['numOfReads'][0]
                            vios_fc_writes += fc['numOfWrites'][0]
                    if 'sharedStoragePools' in v['storage']:
                        for fc in v['storage']['sharedStoragePools']:
                            vios_fc_rbytes += fc['readBytes'][0]
                            vios_fc_wbytes += fc['writeBytes'][0]
                            vios_fc_reads  += fc['numOfReads'][0]
                            vios_fc_writes += fc['numOfWrites'][0]
                except:
                  if firstTime:
                     print("viosUtils missing: writing sample to: %s"%("sample_missing_viosUtils.json"))
                  firstTime = False
                  if self.debug:
                      self.save_to_file("sample_missing_viosUtils.json",str(sample))

                result = { 'time': sampletime, 
                           'cpu_avail': cpu_avail, 
                           'cpu_conf':cpu_conf, 
                           'cpu_total':cpu_total, 
                           'cpu_used':cpu_used, 
                           'mem_avail':mem_avail, 
                           'mem_conf':mem_conf, 
                           'mem_total':mem_total, 
                           'mem_inVM':mem_inVM,
                           'phype_mem':phype_mem,
                           'phype_cpu':phype_cpu,
                           'vios_mem_conf':vios_mem_conf,
                           'vios_mem_used':vios_mem_used,
                           'vios_net_rbytes':vios_net_rbytes,
                           'vios_net_wbytes':vios_net_wbytes,
                           'vios_net_reads':vios_net_reads,
                           'vios_net_writes':vios_net_writes,
                           'vios_cpu_vp':vios_proc_vp,
                           'vios_cpu_entitled':vios_proc_entitled,
                           'vios_cpu_used':vios_proc_used,
                           'vios_fc_rbytes':vios_fc_rbytes,
                           'vios_fc_wbytes':vios_fc_wbytes,
                           'vios_fc_reads':vios_fc_reads,
                           'vios_fc_writes':vios_fc_writes }
                statslist.append(result)
        return headerline, statslist, errors, count

    def extract_lpar_info(self,data):
        ''' This function extracts the header information from the JSON file for LPAR
            Arguments: the LPAR JSON stats string
            Returns: a dictionary of facts about the data set
	'''
        if self.debug:
            print("DEBUG:extract_lpar_info(data)")
        jdata = json.loads(data)
        mtms      = jdata["systemUtil"]["utilInfo"]['mtms']
        server    = jdata["systemUtil"]["utilInfo"]['name'] # name of server
        frequency = jdata["systemUtil"]["utilInfo"]['frequency'] # seconds

        lparname  = jdata["systemUtil"]["utilSamples"][0]['lparsUtil'][0]['name']
        lparstate = jdata["systemUtil"]["utilSamples"][0]['lparsUtil'][0]['state']
        return { 'mtms':mtms, 'server':server, 'frequency':frequency, 'lparname': lparname,'lparstate':lparstate }

    def extract_lpar_stats(self,data):
        ''' This function extracts the stats from the JSON file for the LPAR
            Arguments: the Server JSON stats string
            Returns: an array of dictionaries of the LPAR stats - one dictionary per snapshot
        '''
        if self.debug:
            print("DEBUG:extract_lpar_stats(data)")
        jdata = json.loads(data)
        lparname  = jdata["systemUtil"]["utilSamples"][0]['lparsUtil'][0]['name']

        errors=0
        count=0
        statslist = []
        headerline = 'time, cpu_vp, cpu_entitled, cpu_used, mem_conf, net_rbytes, net_wbytes, net_reads, net_writes, disk_rbytes, disk_wbytes, disk_reads, disk_writes'

        for sample in jdata['systemUtil']['utilSamples']:
            samplestatus = sample['sampleInfo']['status']
            sampletime   = sample['sampleInfo']['timeStamp']
            if samplestatus != 0 :
                errmsg1 = "None"
                errmsg2 = "None"
                try:
                    errmsg = sample['sampleInfo']['errorInfo'][0]['errMsg'] 
                except:
                    print("Oh dear non-zero state but there is no error messages . . . continuing")
                print("*** Error LPAR %s: status=%d (not zero)\n**** mgs1=%s" %(lparname,status,errmsg1))
                errors+= 1
                if errors > 5:
                    break
            else :
                count += 1
                processor = sample['lparsUtil'][0]['processor']
                cpu_vp       = processor['maxVirtualProcessors'][0]
                cpu_entitled = processor['entitledProcUnits'][0]
                cpu_used     = processor['utilizedUncappedProcUnits'][0] + processor['utilizedProcUnits'][0] + processor['utilizedCappedProcUnits'][0]
        
                mem_conf = sample['lparsUtil'][0]['memory']['logicalMem'][0]

                net_rbytes = 0.0
                net_wbytes = 0.0
                net_reads  = 0.0
                net_writes = 0.0
                disk_rbytes = 0.0
                disk_wbytes = 0.0
                disk_reads  = 0.0
                disk_writes = 0.0
                exceptions = 0

                try:
                    networks = sample['lparsUtil'][0]['network']['virtualEthernetAdapters']
                except:
                    exceptions += 1
                    #print("No virtual network")
                else:
                    for net in networks:
                        net_rbytes += net['receivedBytes'][0]
                        net_wbytes += net['sentBytes'][0]
                        net_reads  += net['receivedPackets'][0]
                        net_writes += net['sentPackets'][0]

                try:
                    networks = sample['lparsUtil'][0]['network']['sriovLogicalPorts']
                except:
                    exceptions += 1
                    #print("No sriov network")
                else:
                    for net in networks:
                        net_rbytes += net['receivedBytes'][0]
                        net_wbytes += net['sentBytes'][0]
                        net_reads  += net['receivedPackets'][0]
                        net_writes += net['sentPackets'][0]

                try:
                    disks = sample['lparsUtil'][0]['storage']['virtualFiberChannelAdapters']
                except:
                    exceptions += 1
                    #print("No vFC storage")
                else:
                    for disk in disks:
                        disk_rbytes += disk['readBytes'][0]
                        disk_wbytes += disk['writeBytes'][0]
                        disk_reads  += disk['numOfReads'][0]
                        disk_writes += disk['numOfWrites'][0]

                try:
                    disks = sample['lparsUtil'][0]['storage']['genericVirtualAdapters']
                except:
                    exceptions += 1
                    #print("No virtual Adapter storage")
                else:
                    for disk in disks:
                        disk_rbytes += disk['readBytes'][0]
                        disk_wbytes += disk['writeBytes'][0]
                        disk_reads  += disk['numOfReads'][0]
                        disk_writes += disk['numOfWrites'][0]

                result = { 'time':        sampletime, 
                           'cpu_vp':      cpu_vp, 
                           'cpu_entitled':cpu_entitled, 
                           'cpu_used':    cpu_used, 
                           'mem_conf':    mem_conf, 
                           'net_rbytes':  net_rbytes,
                           'net_wbytes':  net_wbytes,
                           'net_reads':   net_reads,
                           'net_writes':  net_writes,
                           'disk_rbytes': disk_rbytes,
                           'disk_wbytes': disk_wbytes,
                           'disk_reads':  disk_reads,
                           'disk_writes': disk_writes }
                statslist.append(result)
        return headerline, statslist, errors, count

    def extract_energy_info(self,stats):
        ''' This function extracts the header information from the JSON file for Watts 7 Celsius
            Arguments: the LPAR JSON stats string
            Returns: a dictionary of facts about the data set
	'''
        if self.debug:
            print("extract_energy_info(stats)")
        data = json.loads(stats) # convert to JSON
        frequency  = data['systemUtil']['utilInfo']['frequency']
        name = data['systemUtil']['utilInfo']['name']
        mtms = data['systemUtil']['utilInfo']['mtms']
        i = mtms.find('*')
        mtm = mtms[ :i ]
        serial = mtms[i+1: ]
        mtms = mtms.replace('*', ',') # sepeate with a comma.
        start =  data['systemUtil']['utilSamples'][0]['sampleInfo']['timeStamp']
        result = { 'server': name, 'mtm': mtm, 'serial':serial, 'freq': frequency, 'starttime':start  }
        return result

    def extract_energy_stats(self,stats):
        ''' This function extracts the stats from the JSON file for the energy stats
            Arguments: the Server JSON stats string
            Returns: an array of dictionaries of the energy stats - one dictonary per snapshot
        '''
        if self.debug:
            print("extract_energy_stats(stats)")
            self.save_to_file("energy.json", stats)
        data = json.loads(stats) # convert to JSON
        name = data['systemUtil']['utilInfo']['name']
        mtms = data['systemUtil']['utilInfo']['mtms']
        i = mtms.find('*')
        mtm = mtms[ :i ]
        serial = mtms[i: ]
        result = []
        count = 0
        errors = 0
        for sample in data['systemUtil']['utilSamples']:
            if sample['sampleInfo']['status'] != 0 :
               print("*** Error Server %s: Sample status=%d (not zero) time=%s" %(name,sample['sampleInfo']['status'],
                                                 sample['sampleInfo']['timeStamp']))
               errors+= 1
            else :
                count += 1
                watts  = 0.0
                if 'energyUtil' in sample and 'powerUtil' in sample['energyUtil']:
                    try:
                        watts  = sample['energyUtil']['powerUtil']['powerReading'][0]
                    except:
                        watts  = 0.0

                thermal = sample['energyUtil']['thermalUtil']
                if 'baseboardTemperatures' in thermal:
                    try:
                        mb0    = thermal['baseboardTemperatures'][0]['temperatureReading'][0]
                    except:
                        mb0    = 0.0
                    try:
                        mb1    = thermal['baseboardTemperatures'][1]['temperatureReading'][0]
                    except:
                        mb1    = 0.0
                    try:
                        mb2    = thermal['baseboardTemperatures'][2]['temperatureReading'][0]
                    except:
                        mb2    = 0.0
                    try:
                        mb3    = thermal['baseboardTemperatures'][3]['temperatureReading'][0]
                    except:
                        mb3    = 0.0
                else:
                    mb0 = -1.0
                    mb1 = -1.0
                    mb2 = -1.0
                    mb3 = -1.0

                if 'cpuTemperatures' in thermal:
                    try:
                        cpu0    = thermal['cpuTemperatures'][0]['temperatureReading'][0]
                    except:
                        cpu0 = 0.0
                    try:
                        cpu1    = thermal['cpuTemperatures'][1]['temperatureReading'][0]
                    except:
                        cpu1 = 0.0
                    try:
                        cpu2    = thermal['cpuTemperatures'][2]['temperatureReading'][0]
                    except:
                        cpu2 = 0.0
                    try:
                        cpu3    = thermal['cpuTemperatures'][3]['temperatureReading'][0]
                    except:
                        cpu3 = 0.0
                    try:
                        cpu4    = thermal['cpuTemperatures'][4]['temperatureReading'][0]
                    except:
                        cpu4 = 0.0
                    try:
                        cpu5    = thermal['cpuTemperatures'][5]['temperatureReading'][0]
                    except:
                        cpu5 = 0.0
                    try:
                        cpu6    = thermal['cpuTemperatures'][6]['temperatureReading'][0]
                    except:
                        cpu6 = 0.0
                    try:
                        cpu7    = thermal['cpuTemperatures'][7]['temperatureReading'][0]
                    except:
                        cpu7 = 0.0
                else:
                    cpu0 = -1.0
                    cpu1 = -1.0
                    cpu2 = -1.0
                    cpu3 = -1.0
                    cpu4 = -1.0
                    cpu5 = -1.0
                    cpu6 = -1.0
                    cpu7 = -1.0
                    cpu0 = -1.0

                if 'cpuTemperatures' in thermal:
                    try: 
                        inlet   = thermal['inletTemperatures'][0]['temperatureReading'][0]
                    except:
                        inlet = -2.0
                else:
                    inlet = -1.0
                timeStamp = sample['sampleInfo']['timeStamp']
                resultline = { 'time':timeStamp[0:19], 'watts':watts, 'mb0':mb0,'mb1':mb1,'mb2':mb2,'mb3':mb3,'cpu0':cpu0,'cpu1':cpu1,'cpu2':cpu2,'cpu3':cpu3,'cpu4':cpu4,'cpu5':cpu5,'cpu6':cpu6,'cpu7':cpu7,'inlet':inlet }
                result.append(resultline)

                headerline = 'time,watts,mb0,mb1,mb2,mb3,cpu0,cpu1,cpu2,cpu3,cpu4,cpu5,cpu6,cpu7,inlet'
        return headerline,result

# End of File
