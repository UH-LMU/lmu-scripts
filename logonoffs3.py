import csv
from datetime import datetime
from icalendar import Calendar, Event
import sys
import uuid


try:
    f = open(sys.argv[1], 'rb') # opens the csv file
    reader = csv.reader(f)  # creates the reader object

    user = ''
    cal = Calendar()
    event = None
    previous = set()
    for row in reader:   # iterates the rows of the file in orders
        #print row
        timegen = row[0]
        eventid = row[1]
        logon = row[2]
        logoff = row[3]

        # cludge to skip header row
        if timegen == "TimeGenerated":
            continue

        day, time = timegen.split()
        y, m, d = day.split('-')
        h, minutes,s = time.split(':')

        # sequence 4648 is successfull login
        if eventid == '4648':
            user = logon
            print "Logon:", timegen, user

            # create calendar event
            event = Event()
            event.add('summary', 'logon ' + user)
            event.add('dtstart', datetime(int(y), int(m), int(d), int(h), int(minutes)))
            uid = uuid.uuid4()
            event['uid'] = uid
            cal.add_component(event)

        # 4647 is normal logoff
        if eventid == '4647':
            user = logoff
            print "Logoff:", timegen, user

            event = Event()
            event.add('summary', 'logoff ' + user)
            event.add('dtstart', datetime(int(y), int(m), int(d), int(h), int(minutes)))
            uid = uuid.uuid4()
            event['uid'] = uid
            cal.add_component(event)


finally:
    print "close file"
    print previous
    f.close()      # closing

    f = open('logonoffs.ics', 'wb')
    f.write(cal.to_ical())
    f.close()
