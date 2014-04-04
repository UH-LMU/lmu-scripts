from collections import deque
import csv
from datetime import datetime
from icalendar import Calendar, Event
import sys
import uuid


# store three previous events
records = deque(3*[0],3)
times = deque(3*[0],3)
eventids = deque(3*[0],3)
infos = deque(3*[0],3)

try:
    f = open(sys.argv[1], 'rb') # opens the csv file
    reader = csv.reader(f)  # creates the reader object
    
    user = ''
    cal = Calendar()
    event = None
    previous = set()
    for row in reader:   # iterates the rows of the file in orders
        #print row
        record = row[1]
        timegen = row[2]
        eventid = row[4]
        info = row[10]

        # cludge to skip header row
        if record == "RecordNumber":
            continue

        records.append(record)
        times.append(timegen)
        eventids.append(eventid)
        infos.append(info)

        day, time = timegen.split()
        y, m, d = day.split('-')
        h, minutes,s = time.split(':')

        # sequence 4648,4624,4624 is successfull login
        if eventids[0] == '4648':# and eventids[1] == '4624' and eventids[2] == '4624':
            fields = infos[0].split('|')
            # 
            if fields[11] == "C:\\Windows\\System32\\winlogon.exe":
                user = fields[5]
                print "Logon:", timegen, user

                # create calendar event
                event = Event()
                event.add('summary', user)
                event.add('dtstart', datetime(int(y), int(m), int(d), int(h), int(minutes)))
                uid = uuid.uuid4()
                event['uid'] = uid

        # 4647 is normal logoff
        if eventid == '4647':
            fields = info.split('|')
            user_logoff = fields[1]

            # user logging off must be same that logged on...
            if user_logoff == user:
                print "Logoff:", timegen, user

                # close calendar event
                if event:
                    event.add('dtend', datetime(int(y), int(m), int(d), int(h), int(minutes)))
                    cal.add_component(event)
            # ... if not, probably it is some admin account action
            else:
                print "Strange logoff:", timegen, user_logoff, user


        # 4608 is system startup, find previous event
        if eventids[2] == '4608':
            print "Shutdown", times[0], user#, records[0], eventids[0]
            #print "Shutdown", times[1], user, records[1], eventids[1]

            # nobody is logged in after startup
            user = 'startup_no_user'
            print "Startup", times[2], user#, records[2], eventids[2]

            # debug: store all events before 4608
            previous.add(eventids[1])
            
            # close calendar event
            if event:
                # sometimes event 1101 precedes 4608 at startup, therefore use the event
                # before that (times[0]) for shutdown time.
                day, time = times[0].split()
                y, m, d = day.split('-')
                h, minutes,s = time.split(':')

                event.add('dtend', datetime(int(y), int(m), int(d), int(h), int(minutes)))
                cal.add_component(event)
                
           
finally:
    print "close file"
    print previous
    f.close()      # closing

    f = open('logonoffs.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

'4648', '4634', '4905', '4672', '4647', '4624', '1100', '1101', '4616'
