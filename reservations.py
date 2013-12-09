from datetime import datetime
from icalendar import Calendar, Event
import re
import sys
import uuid

filename = sys.argv[1]
file = open(filename)
lines = file.readlines()
file.close()

re_date = re.compile('([A-Z,a-z]{3}) ([0-9]{1,2}) ([0-9]{1,2}):([0-9][0-9]):[0-9][0-9] EEST ([0-9]{4})')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def resultgroup2datetime(r):
    monthstring = r[0]
    m = months.index(monthstring) + 1
    d = r[1]
    h = r[2]
    min = r[3]
    y = r[4]
    
    return datetime(int(y), int(m), int(d), int(h), int(min))
    
def resultgroup2str(r):
    monthstring = r[0]
    m = months.index(monthstring) + 1
    d = r[1]
    h = r[2]
    min = r[3]
    y = r[4]
    
    return y+'-'+ str(m).zfill(2)+'-'+d.zfill(2) + ' ' + h.zfill(2) + ':' + min.zfill(2)

cal = Calendar()
event = None

for l in lines:        
    #print l.rstrip()
    start = None
    end = None
    result = re.findall(re_date, l)
    if result:
        start = result[0]
        end = result[1]
        
    fields = l.split(',')
    user = fields[2]
    
    if start and end:
        print resultgroup2str(start),  "START",  user
        print resultgroup2str(end),  "END",  user
        
        event = Event()
        event.add('summary', user)
        event.add('dtstart', resultgroup2datetime(start))
        event.add('dtend', resultgroup2datetime(end))
        uid = uuid.uuid4()
        event['uid'] = uid
        cal.add_component(event)

f = open('reservations.ics', 'wb')
f.write(cal.to_ical())
f.close()

