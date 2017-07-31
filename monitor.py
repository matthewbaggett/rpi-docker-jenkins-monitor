#!/usr/bin/python
#
# author: ajs
# license: bsd
# copyright: re2

import os
import json 
import sys
import urllib
import urllib2
import redis

jenkinsUrl = "http://jenkins.home.gone.io/job/"
brightness = 0.5

r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=0)

jobList = ["Build_Microsites", "Build_Phusion_Arm", "Gone.io Docker Images (x86_64)", "Gone.io Docker Images (armhf)", "Niall/job/Build_Niall_Service"]
for i, jobName in enumerate(jobList):
	jobNameURL = urllib.quote(jobName)

	try:
		jenkinsStream   = urllib2.urlopen( jenkinsUrl + jobNameURL + "/lastBuild/api/json" )
	except urllib2.HTTPError, e:
		print "URL Error: " + str(e.code) 
		print "\t  (job name [" + jobName + "] probably wrong)"

	try:
		buildStatusJson = json.load( jenkinsStream )
	except:
		print "Failed to parse json"

	if buildStatusJson.has_key( "result" ):
		print "[" + jobName + "] build status: " + buildStatusJson["result"]
		if buildStatusJson["result"] == "SUCCESS" :
			r.hmset('blinkt_light_state:' + str(i), {'r':0, 'g':255, 'b':0, 'bri': brightness})
		elif buildStatusJson["result"] == "ABORTED" : 
			r.hmset('blinkt_light_state:' + str(i), {'r':255, 'g':215, 'b':0, 'bri': brightness})
		elif buildStatusJson["result"] == "FAILURE":
			r.hmset('blinkt_light_state:' + str(i), {'r':255, 'g':0, 'b':0, 'bri': brightness})


	if buildStatusJson.has_key( "building" ):
		if buildStatusJson["building"]:
			r.hmset('blinkt_light_state:' + str(i), {'mode':'flashing'})
		else:
			r.hmset('blinkt_light_state:' + str(i), {'mode':'none'})

print ""
