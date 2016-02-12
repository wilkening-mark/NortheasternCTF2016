# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 17:57:12 2016

@author: vsuha
"""

import unittest 
import server

class ServerTest(unittest.TestCase):
    
    def test1_add_reg_request(self):
        #check good JSON values
        goodSampleData = {"device_key": "123456", "flag": "<theflag>", "pin": "999999", "device_id": "000000000000000"}
        self.assertEqual(goodSampleData, server.add_reg_request('123456','000000000000000'))
        
    def test2_add_reg_request(self):
        #check bad JSON values, add_reg_request only passes in two values - device_key and device_id are constants at the beginning of server.py
        self.assertRaises(ValueError, server.add_reg_request('you suck','000000000000000'))
        
    def test3_add_reg_request(self):
        #check bad JSON values
        self.assertRaises(ValueError, server.add_reg_request('123456','no, you suck'))    
        
    #Potentially, add another test to check that we can read the file, line 195 of server.py
    
    #check if timestamps are formatted properly 
    def test_bb_format_date(self):
        #checking against good date value
        self.assertEqual('2016Feb1109:24:00', server.format_date('Thr Feb 11 09:24:00 EST 2016')[0])
        
    def test_network_format_date(self):
        self.assertEqual('2016Feb1109:24:00', server.format_date('Thr Feb 11 09:24:00 EST 2016')[1])      
        
    #can add another test to assertRaises
           
if __name__ == '__main__':
    unittest.main()


