import unittest
from datetime import datetime

class ServerConnectionTests(unittest.TestCase):

    def get_rtc_date(self, date):
        # Expected format: 'Tue 09 Feb 2016 09:29:02 PM UTC -1.005808 second'
        rtc_date = date
        # Parse out '-1.005808 seconds' cause the module wont know what to do with it
        rtc_date = rtc_date[0:31]
        # Format to '2016Feb0921:28:23'
        rtc_date = datetime.strptime(rtc_date, '%a %d %b %Y %H:%M:%S %p %Z')
        rtc_date = datetime.strftime(rtc_date, '%Y%b%d%H:%M:%S')

        return rtc_date

    def test_get_rtc_date(self):
        date = 'Tue 09 Feb 2016 21:29:02 PM UTC -1.005808 second'
        expected = '2016Feb0921:29:02'

        actual = self.get_rtc_date(date)
        self.assertEqual(expected, actual)



def main():
    unittest.main()

if __name__ == '__main__':
    main()
