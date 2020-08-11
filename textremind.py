import os
import sched
from twilio.rest import Client
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#twilio setup
ethan_account = {'accountSID': os.environ['TWILIO_ACCOUNT_SID'], 'Auth Token': os.environ['TWILIO_AUTH_TOKEN']}
client = Client(ethan_account['accountSID'], ethan_account['Auth Token'])

file = open('phonenumbers', 'r')
text = file.readlines()
myTwilioNumber = text[0].strip()
ethanCell = text[1].strip()
mathieuCell = text[2].strip()

#google drive file setup


#sending text messages
#mat_message = client.messages.create(body='Test python message', from_=myTwilioNumber, to=mathieuCell)
#ethan_message = client.messages.create(body='Test python message', from_=myTwilioNumber, to=ethanCell)

def testtime():
    x = datetime.datetime.now()
    print(x)

if __name__ == "__main__":
    testtime()
