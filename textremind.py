import os
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client

#twilio setup
ethan_account = {'accountSID': os.environ['TWILIO_ACCOUNT_SID'], 'Auth Token': os.environ['TWILIO_AUTH_TOKEN']}
client = Client(ethan_account['accountSID'], ethan_account['Auth Token'])

file = open('phonenumbers', 'r')
text = file.readlines()
myTwilioNumber = text[0].strip()
ethanCell = text[1].strip()
mathieuCell = text[2].strip()

#google drive file setup
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('./client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Education and Fitness Tracking").sheet1

#sending text messages


def send_message():
    workout_sent = False
    coding_sent = False
    while datetime.now().strftime('%H'):
        hour = datetime.now().strftime('%H')

        if hour == "10":
            if not coding_sent:
                coding_remind()
                coding_sent = True
        elif (hour == "17") or (hour == "19"):
            if not workout_sent:
                workout_remind()
                workout_sent = True
            
        if hour == "11":
            coding_sent = False
        elif (hour == "18") or (hour == "20"):
            workout_sent = False
        
        time.sleep(5)
        print("loop executed at:", datetime.now())
        
            
def coding_remind():
    mat_message = client.messages.create(body='Remember to do at least one hour of coding practice today', from_=myTwilioNumber, to=mathieuCell)
    ethan_message = client.messages.create(body='Remember to do at least one hour of coding practice today', from_=myTwilioNumber, to=ethanCell)

def workout_remind():
    mat_message = client.messages.create(body='Remember to workout today', from_=myTwilioNumber, to=mathieuCell)
    ethan_message = client.messages.create(body='Remember to workout today', from_=myTwilioNumber, to=ethanCell)

if __name__ == "__main__":
    send_message()
