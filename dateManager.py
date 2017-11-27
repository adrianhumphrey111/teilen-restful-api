'''
Created on Nov 25, 2017

@author: adrianhumphrey
'''

from datetime import datetime
import pytz




class DateManager:
    '''Classify Post times. 
        1m - 59m
        1hr - 23h
        Yesterday at 11:39pm
        2 days , Monday 11:49pm, Sunday 4:12 am
        Explicit date'''
    
    def __init__(self, tz, created_at):
        self.now = datetime.now()
        print self.now
        self.date = created_at
        local_tz = pytz.timezone(tz)
        self.nowWithtz = local_tz.localize(self.date) 
        print self.nowWithtz
        
        #Set seconds
        self.seconds = int( self.secondsBetween() )
        
        #Set the type of date you want to send
        self.final_time = self.setTimeType()
        
    def setTimeType(self):
        '''If it is between 1 minute and 59 minutes'''
        if self.seconds < 60:
            return 'less than a minute ago'
        elif self.seconds > 60 and self.seconds  < 60 * 60:
            minute = self.seconds / 60 
            return str( minute ) + 'm ago'
        elif self.seconds > ( 60 * 60 ) and self.seconds < ( 60 * 60 * 24 ):
            hour = self.seconds / ( 60 * 60 )
            return str( hour ) + "h ago"
        elif self.seconds > ( 60 * 60 * 24) and self.seconds < ( 60 * 60 * 48):
            print 'yesterday'
            '''Return the day of the week'''
            dayInt = self.nowWithtz.weekday()
            time = self.nowWithtz.strftime('%-I:%M%p')
            return 'Yesterday ' + str( time )
        elif self.seconds > ( 60 * 60 * 48) and self.seconds < ( 60 * 60 * 84):
            '''Return the day of the week'''
            dayInt = self.nowWithtz.weekday()
            time = self.nowWithtz.strftime('%-I:%M %p')
            if dayInt == 0:
                return 'Monday ' + str( time )
            if dayInt == 1:
                return 'Tuesday ' + str( time )
            if dayInt == 2:
                return 'Wednesday ' + str( time )
            if dayInt == 3:
                return 'Thursday ' + str( time )
            if dayInt == 4:
                return 'Friday ' + str( time )
            if dayInt == 5:
                return 'Saturday ' + str( time )
            if dayInt == 6:
                return 'Sunday ' + str( time )
        else:
            time = self.nowWithtz.strftime('%b %d %-I:%M%p')
            return time
            
        
    def secondsBetween(self):
        seconds = self.now - self.date
        return seconds.total_seconds()

            
            
            