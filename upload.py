#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
from datetime import datetime

UPDATE_REPORT_URL='http://eps.poista.net/lastWeather1m'
MS_TO_MPH = 2.237

class WUUpdate:
    def __init__(self):
        self.epsDict = None
        self.wu_config = { 'station_id' : 'IESPOO11', 'password' : 'goD6io2k' }

    def updateFromEpsDict(self,epsDict):
        self.epsDict = epsDict
        timeFormat = datetime.utcnow().strftime("%Y-%m-%d ") + self.epsDict['time'] + ":00"
        self.requestDict = dict(self.epsDict.items() + self.wu_config.items() + [("timeFormat", timeFormat)])
        print self.requestDict

    def cToF(self, celsius):
        return (celsius * 9 / 5) + 32

    def doUpdate(self):
        requestParams = { 'ID' : self.requestDict['station_id'], 
                          'PASSWORD' : self.requestDict['password'],
                          'dateutc' : self.requestDict['timeFormat'], 
                          'winddir' : self.requestDict['direction'],
                          'windspdmph_avg2m' : float(self.requestDict['avg']) * MS_TO_MPH, 
                          'windgustmph' : float(self.requestDict['highTo']) * MS_TO_MPH,
                          'tempf' : self.cToF(float(self.requestDict['temp'])) }
        r = requests.get("http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php", params=requestParams)
        print r.url
        print r.text

class EPSFetcher:
    def __init(self):
        self.last_eps_update = ""

    def _update(self):
        r = requests.get(UPDATE_REPORT_URL)
        self.last_eps_update = r.text.split('\n', 1)[0].encode('utf-8')

    def get_update_dict(self):
        named_groups = '(?P<time>\d{1,2}:\d{1,2})\s+Dir:\s+(?P<direction>\d+)\s*Low:\s*(?P<lowFrom>\d+.\d+)\s+-\s+(?P<lowTo>\d+.\d+)\s*Avg:\s+(?P<avg>\d+.\d+)\s*High:\s*(?P<highFrom>\d+.\d+)\s+-\s+(?P<highTo>\d+.\d+)\s*\s(?P<temp>\d+.\d+)°C'
        weather_matcher = re.compile(named_groups)
        self._update()
        return weather_matcher.match(self.last_eps_update).groupdict()

weather_update = "10:35  Dir:  71  Low:  1.9 -  3.2  Avg:  3.4  High:  3.9 -  5.2   18.9°C"

wuupdate = WUUpdate()
wuupdate.updateFromEpsDict(EPSFetcher().get_update_dict())
wuupdate.doUpdate()


