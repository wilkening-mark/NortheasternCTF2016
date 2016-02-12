# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 17:57:12 2016

@author: vsuha
"""

import unittest 
#import server
from datetime import datetime

class ServerTest(unittest.TestCase):
    '''
    def test1_add_reg_request(self):
        #check good JSON values
        DEFAULT_PIN = '123456'
        DEFAULT_FLAG = '<theflag>'
        goodSampleData = {"device_key": "123456", "flag": "<theflag>", "pin": "999999", "device_id": "000000000000000"}
        dictionaryData = {'device_id': device_id,
         'device_key' : device_key,
         'flag' : DEFAULT_FLAG,
         'pin'  : DEFAULT_PIN}        
        self.assertEqual(goodSampleData, server.add_reg_request(request['123456'],request['000000000000000']))
        
    def test2_add_reg_request(self):
        #check bad JSON values, add_reg_request only passes in two values - device_key and device_id are constants at the beginning of server.py
        self.assertRaises(ValueError, server.add_reg_request(request['you suck'],request['000000000000000']))
        
    def test3_add_reg_request(self):
        #check bad JSON values
        self.assertRaises(ValueError, server.add_reg_request(request['123456'],request['no, you suck']))    
        '''
    def get_bb_date(self, date):
        # Expected format: 'Tue Feb  9 21:28:23 UTC 2016'
        bb_date = date

        # Format to '2016Feb0921:28:23'
        bb_date = datetime.strptime(bb_date, '%a %b %d %H:%M:%S %Z %Y')
        print bb_date
        bb_date = datetime.strftime(bb_date, '%Y%b%d%H:%M:%S')
        print bb_date

        return bb_date
        
    def get_network_date(self, date):
        # Expected format: 'Tue Feb  9 21:28:23 UTC 2016'
        network_date = date
        # network_date doesn't have a year, append to end
        network_date = network_date + ' 2016'

        # Format to '2016Feb0921:28:23'
        network_date = datetime.strptime(network_date, '%d %b %H:%M:%S %Y')
        print network_date
        network_date = datetime.strftime(network_date, '%Y%b%d%H:%M:%S')
        print network_date

        return network_date
    
    #check if timestamps are formatted properly 
    def test_bb_format_date(self):
        #checking against good date value
        self.assertEqual('2016Feb1211:24:25', self.get_bb_date('Fri Feb 12 11:24:25 EST 2016'))
        
    def test_network_format_date(self):
        self.assertEqual('2016Feb1211:26:13', self.get_network_date('12 Feb 11:26:13'))      
        
    #can add another test to assertRaises
           
if __name__ == '__main__':
    unittest.main()


