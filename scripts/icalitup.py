#!/usr/bin/python

# Create lib folder: python3 setup.py


import os
from urllib.request import urlopen
from json import loads
from calendar import monthrange
from datetime import date, datetime

import boto3
from dateutil.relativedelta import relativedelta
from pytz import timezone
from icalendar import Calendar, Event


# TOKEN = 'QI619nKp8I3xwXYDndAyu%252fHOzsQ9OmI1ib7DclIirB%252bqnTgtB9f%252fpQ%253d%253d'
# C_URL = 'https://account.subitup.com/API2/employee/communication.asmx/getContactList?employeeToken='
# S_URL = 'https://account.subitup.com/API2/employee/schedule.asmx/getFullSchedule_AllDepts?employeeToken='

TOKEN = os.environ['TOKEN']
C_URL = os.environ['C_URL']
S_URL = os.environ['S_URL']

class iCalItUp:

    def __init__(self, token, contact_url, schedule_url):
        self.token = token
        self.contact_url = contact_url
        self.schedule_url = schedule_url

        self.contacts = {}


    # store contacts into self.contacts
    def get_contacts(self):
        response = urlopen(self.contact_url + self.token)
        people = loads(response.read())

        for person in people:
            first = person['firstname']
            last = person['lastname']
            email = person['email']
            self.contacts[last + first] = email

    # create event given shift
    def create_event(self, shift):
        start = timezone('America/New_York').localize(datetime.strptime(shift['start'], '%m/%d/%Y %I:%M %p'))
        end = timezone('America/New_York').localize(datetime.strptime(shift['end'], '%m/%d/%Y %I:%M %p'))
        name = shift['last'] + ',' + shift['first']
        event = Event()
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('summary', 'Stamp IT Shift')
        event.add('description', shift['title'])
        event.add('location', 'Stamp Student Union')
        return (event, name)

    # create calendar given events
    def create_cal(self, person):
        first = person.split(',')[1]
        last = person.split(',')[0]
        cal = Calendar()
        cal.add('prodid', '-//' + first + ' ' + last + '//SubItUp//EN')
        cal.add('version', '1.0')
        cal.add('name', 'Stamp IT')
        cal.add('X-WR-CALNAME', 'Stamp IT')
        cal.add('X-WR-TIMEZONE', 'America/New_York')
        return cal

    # main function
    def get_all_shifts(self):
        today = date.today()
        n_month = today + relativedelta(months=+1)
        start = str(today.month) + '-01-' + str(today.year)
        end = str(n_month.month) + '-' + str(monthrange(n_month.year, n_month.month)[1]) + '-' + str(n_month.year)

        response = urlopen(S_URL + TOKEN + '&startdate=' + start + '&enddate=' + end)
        all_shifts = loads(response.read())

        cals = {}
        events = {}

        for shift in all_shifts:
            event, name = self.create_event(shift)
            if name not in events:
                events[name] = []
            events[name].append(event)

        for person in events:
            cal = self.create_cal(person)

            for event in events[person]:
                cal.add_component(event)
            
            cals[person] = cal.to_ical()
        
        return cals

# handler for AWS Lambda
def handler(event, context):
    client = boto3.client('s3')
    cal = iCalItUp(os.environ['TOKEN'], os.environ['C_URL'], os.environ['S_URL'])
    cals = cal.get_all_shifts()
    for person, cal in cals.items():
        client.put_object(ACL='public-read', Body=cal, Bucket='subitup-calendars', Key=(person.replace(',','') + '.ics'))
