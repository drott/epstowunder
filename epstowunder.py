#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014, Dominik Röttsches
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DOMINIK RÖTTSCHES BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import requests
from datetime import datetime
import sys
from time import strptime, localtime
from pytz import *

UPDATE_REPORT_URL='http://eps.poista.net/lastWeather1m'
MS_TO_MPH = 2.237

class WUUpdate:
    def __init__(self):
        self.epsDict = None
        self.wu_config = { 'station_id' : 'IESPOO11', 'password' : '<removed>' }

    def updateFromEpsDict(self,epsDict):
        self.epsDict = epsDict
        tzFi = timezone("Europe/Helsinki")
        timeFormat = datetime.now(tzFi).strftime("%Y-%m-%d ") + self.epsDict['time'] + ":00"
        timeFi = datetime.strptime(timeFormat, "%Y-%m-%d %H:%M:%S")
        timeFi = tzFi.localize(timeFi)
        timeUtc = timeFi.astimezone(utc);
        timeFormat = timeUtc.strftime("%Y-%m-%d %H:%M:%S")
        self.requestDict = dict(self.epsDict.items() + self.wu_config.items() + [("timeFormat", timeFormat)])

    def cToF(self, celsius):
        return (celsius * 9 / 5) + 32

    def doUpdate(self):
        requestParams = { 'ID' : self.requestDict['station_id'], 
                          'PASSWORD' : self.requestDict['password'],
                          'dateutc' : self.requestDict['timeFormat'], 
                          'winddir' : self.requestDict['direction'],
                          'windspeedmph' : float(self.requestDict['avg']) * MS_TO_MPH, 
                          'windgustmph' : float(self.requestDict['highTo']) * MS_TO_MPH,
                          'tempf' : self.cToF(float(self.requestDict['temp'])) }
        r = requests.get("http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php", params=requestParams)
        return r.text.startswith("success");

class EPSFetcher:
    def __init(self):
        self.last_eps_update = ""

    def _update(self):
        r = requests.get(UPDATE_REPORT_URL)
        self.last_eps_update = r.text.split('\n', 1)[0].encode('utf-8')

    def get_update_dict(self):
        named_groups = '\s*(?P<time>\d{1,2}:\d{1,2})\s+Dir:\s+(?P<direction>\d+)\s*Low:\s*(?P<lowFrom>\d+.\d+)\s+-\s+(?P<lowTo>\d+.\d+)\s*Avg:\s+(?P<avg>\d+.\d+)\s*High:\s*(?P<highFrom>\d+.\d+)\s+-\s+(?P<highTo>\d+.\d+)\s*\s(?P<temp>\d+.\d+)°C'
        weather_matcher = re.compile(named_groups)
        self._update()
        matched = weather_matcher.match(self.last_eps_update)
        if (matched):
            return matched.groupdict()
        else:
            return None

wuupdate = WUUpdate()
update_dict = EPSFetcher().get_update_dict()
if (update_dict):
    wuupdate.updateFromEpsDict(update_dict)
    if (wuupdate.doUpdate()):
        exit(0)
exit(1)

