from datetime import datetime
from icalendar import Calendar, Event
import re
import sys
import uuid

filename = sys.argv[1]
file = open(filename)
lines = file.readlines()
file.close()

re_date = re.compile('([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9])')
re_user_logoff = re.compile('\|(.*)\|ATKK')
re_user_logon = re.compile('\}\|(.*)\|ATKK')
re_logon = re.compile(',4648,')
re_logoff = re.compile(',4647,')
re_admin_lmu = re.compile('admin_lmu')
re_tcs_user = re.compile('tcs_user')

LOGGEDON = False
cal = Calendar()
event = None

for l in lines:
    logon = False
    result = re.search(re_logon, l)
    if result:
        logon = True
        
    logoff = False
    result = re.search(re_logoff, l)
    if result:
        logoff = True

    if logon and logoff:
        print "Confusion, both logon and logoff event"
        sys.exit(1)

    # neither logon or logoff, skip line
    if not (logon or logoff):
       continue
        
    # logon event while already logged in, skip line
    if LOGGEDON and logon:
        continue
    
    # save state
    if logon:
        LOGGEDON = True
    else:
        LOGGEDON = False
        
    date = ''
    result = re.search(re_date, l)
    if result:
        date = result.groups(1)[0]

    user = 'USER_NOT_FOUND'
    if re.search(re_admin_lmu, l):
        user = 'admin_lmu'
    elif re.search(re_tcs_user, l):
        user = 'tcs_user'
    else:
        if logoff:
            result = re.search(re_user_logoff, l)
            if result:
                user = result.groups(1)[0]
            
        else:
            result = re.search(re_user_logon, l)
            if result:
                user = result.groups(1)[0]

    
    action = ''
    if logon:
        action = "LOGON"
    else:
        action = "LOGOFF"

    print date,  action,  user
    
    day, time = date.split()
    y, m, d = day.split('-')
    h, min = time.split(':')
    
    if logon:
        event = Event()
        event.add('summary', user)
        event.add('dtstart', datetime(int(y), int(m), int(d), int(h), int(min)))
        uid = uuid.uuid4()
        event['uid'] = uid
    elif logoff and event:
        event.add('dtend', datetime(int(y), int(m), int(d), int(h), int(min)))
        cal.add_component(event)

f = open('logonoffs.ics', 'wb')
f.write(cal.to_ical())
f.close()

