# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:30:40 2016

@author: vsuha
"""
from datetime import datetime 

localDate = datetime.strptime('Tue Feb  9 21:28:23 UTC 2016', '%a %b  %d %H:%M:%S %Z %Y')
localDate = datetime.strftime(localDate, '%y%b%d%H:%M:%S')

rtcDate = datetime.strptime('Tue 09 Feb 2016 09:29:02 PM UTC', '%a %d %b %Y %H:%M:%S %p %Z')
#parse out '-1.005808 seconds cause the module wont know what to do with it'
rtcDate = datetime.strftime(rtcDate, '%y%b%d%H:%M:%S')

print localDate
print rtcDate

