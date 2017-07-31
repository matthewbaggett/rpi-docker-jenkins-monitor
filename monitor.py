#!/usr/bin/python
#
# author: ajs
# license: bsd
# copyright: re2

import os
import time
import json 
import sys
import urllib
import urllib2
import redis

jenkinsUrl = "http://jenkins.home.gone.io/job/"
brightness = 0.5

r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=0)

jobList = ["Build_Microsites", "Build_Phusion_Arm", "Gone.io Docker Images (x86_64)", "Gone.io Docker Images (armhf)", "Niall/job/Build_Niall_Service"]

for index, jobName in enumerate(jobList):
    r.hmset('blinkt_light_state:' + str(index), {'r':0, 'g':0, 'b':0, 'bri': brightness, 'mode': 'none'})

time.sleep(2)

print "Starting main loop"

while True:
    for i, jobName in enumerate(jobList):
        pipe = r.pipeline()

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

        if buildStatusJson.has_key( "result" ) and buildStatusJson["result"]:
            print "[" + jobName + "] build status: " + buildStatusJson["result"]
            pipe.hset('blinkt_light_state:' + str(i), 'bri', brightness)

            if buildStatusJson["result"] == "SUCCESS" :
                pipe.hset('blinkt_light_state:' + str(i), 'r', 0)
                pipe.hset('blinkt_light_state:' + str(i), 'g', 255)
                pipe.hset('blinkt_light_state:' + str(i), 'b', 0)
            elif buildStatusJson["result"] == "ABORTED" :
                pipe.hset('blinkt_light_state:' + str(i), 'r', 255)
                pipe.hset('blinkt_light_state:' + str(i), 'g', 255)
                pipe.hset('blinkt_light_state:' + str(i), 'b', 255)
                pipe.hset('blinkt_light_state:' + str(i), 'bri', 30)
            elif buildStatusJson["result"] == "FAILURE":
                pipe.hset('blinkt_light_state:' + str(i), 'r', 255)
                pipe.hset('blinkt_light_state:' + str(i), 'g', 0)
                pipe.hset('blinkt_light_state:' + str(i), 'b', 0)

        if buildStatusJson.has_key( "building" ):
            if buildStatusJson["building"]:
                pipe.hset('blinkt_light_state:' + str(i), 'mode', 'flashing')
            else:
                pipe.hset('blinkt_light_state:' + str(i), 'mode','none')

        pipe.execute();
        #print str(r.hgetall('blinkt_light_state:' + str(i)))

    print ""
    time.sleep(2);
