from datetime import datetime
from collections import deque

class TimeQueue(object):
    def __init__(self):
        """
        Creates a table that lists the last attempts to unlock the door.
        This table stores the times to limit the possibility of brute force.
        """
        self.REQUEST_LIMIT_PER_TIME = 5
        self.HOURS = 1.0/60 / 4
        self.MINUTES_IN_HOUR = 60
        self.SECONDS_IN_MINUTE = 60

        self.access_table = deque()

    def push_access_time(self):
        now = datetime.now()
        #print now
        self.access_table.append(now)

    def rate_limit_full(self):
        """
        Checks the amount of unlocks that have been done in the last hour,
        removing them from the queue if they are older. If fewer than the limit
        (the size of the queue) have been done, goes through with the unlock if valid.
        """


        if len(self.access_table) >= self.REQUEST_LIMIT_PER_TIME:
            now = datetime.now()
            then = self.access_table[0]

            while len(self.access_table) > 0 and \
                abs(now - then).total_seconds() > \
                self.HOURS * self.MINUTES_IN_HOUR * self.SECONDS_IN_MINUTE:

                #current = self.access_table[0]
                #print "Current:" + str(current)

                if len(self.access_table) > 0:
                    then = self.access_table.popleft()

                #print len(self.access_table)

                #sprint abs(now - then).total_seconds()

            if len(self.access_table) >= self.REQUEST_LIMIT_PER_TIME:
                return True
            else:
                self.push_access_time()
                return False

        else:
            self.push_access_time()
            return False

tq = TimeQueue()
abcdef = "abc"
while 1 == 1:
    abcdef = raw_input("Input: ")
    if tq.rate_limit_full():
        print "Rate limit reached."
    else:
        print "Successful request."
