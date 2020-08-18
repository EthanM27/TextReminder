import os
import time
import shelve
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client

'''
Used for daily repeat updates (text or google sheets)

Designed to run at the same time as spreadsheet.py
'''
# twilio setup
ethan_account = {
    'accountSID': os.environ['TWILIO_ACCOUNT_SID'], 'Auth Token': os.environ['TWILIO_AUTH_TOKEN']}
client = Client(ethan_account['accountSID'], ethan_account['Auth Token'])

file = open('phonenumbers', 'r')
text = file.readlines()
myTwilioNumber = text[0].strip()
ethanCell = text[1].strip()
mathieuCell = text[2].strip()
nikolaCell = text[3].strip()
momCell = text[4].strip()

# google drive file setup
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    './client_secret.json', scope)
gspread_client = gspread.authorize(creds)
sheet = gspread_client.open("Education and Fitness Tracking").sheet1

# try:
#     s = shelve.open('daytrack')
#     today_row = s['rowNum']
# except KeyError:
#     today_row = update_row()
# finally:
#     s.close()
    
# sending text messages
def send_message():
    global sheet
    global today_row
    workout_sent = False
    coding_sent = False
    today_updated = False
    trash_sent = False
    while datetime.now().strftime('%H'):
        try:
            # TODO: dont send message if sheet is already filled in for the day.
            hour = datetime.now().strftime('%H')
            day_name = datetime.now().strftime('%A')
            
            # fills in Day and Date for the row of the day if its 5:00am or todays row is not equal to
            if (hour == "00" and not today_updated) or (today_row_blank()):
                date = datetime.now().strftime('%m/%d/%Y')
                day_name = datetime.now().strftime('%A')
                row_num = update_todays_row()

                s = shelve.open('daytrack')
                coding_cells = sheet.range(row_num, s['COL_OFFSET_CODING'], row_num, s['COL_OFFSET_CODING'] + 1)
                workout_cells = sheet.range(row_num, s['COL_OFFSET_EX'], row_num, s['COL_OFFSET_EX'] + 1)
                coding_cells[0].value = day_name
                workout_cells[0].value = day_name
                coding_cells[1].value = date
                workout_cells[1].value = date

                sheet.update_cells(coding_cells, value_input_option='USER_ENTERED')
                sheet.update_cells(workout_cells, value_input_option='USER_ENTERED')
                today_updated = True
                s.close()
                print('Updated Todays Row')

            #remind mom to take out trash
            if (hour == '18'):
                if day_name == 'Wednesday':
                    if not trash_sent:
                        trash_and_recycle_remind()
                        trash_sent = True
                elif day_name == 'Sunday':
                    if not trash_sent:
                        trash_remind()
                        trash_sent = True

            # sends coding and workout messages based on time
            if hour == "10":
                if not coding_sent:
                    coding_remind()
                    coding_sent = True
            elif (hour == "17") or (hour == "19"):
                if not workout_sent:
                    workout_remind()
                    workout_sent = True
            
            # reset tracking at end of the day
            if hour == "23":
                coding_sent = False
                workout_sent = False
                today_updated = False
                trash_sent = False

        except Exception as e:
            print(e)
        finally:
            time.sleep(5)
            print("loop executed at:", datetime.now())
        
            
def coding_remind():
    mat_message = client.messages.create(body='Remember to do at least one hour of coding practice today', from_=myTwilioNumber, to=mathieuCell)
    ethan_message = client.messages.create(body='Remember to do at least one hour of coding practice today', from_=myTwilioNumber, to=ethanCell)

def workout_remind():
    mat_message = client.messages.create(body='Remember to workout today', from_=myTwilioNumber, to=mathieuCell)
    ethan_message = client.messages.create(body='Remember to workout today', from_=myTwilioNumber, to=ethanCell)

def trash_remind():
    mom_message = client.messages.create(body='Remember to take out the trash today', from_=myTwilioNumber, to=momCell)

def trash_and_recycle_remind():
    mom_message = client.messages.create(body='Remember to take out the trash and recycling today', from_=myTwilioNumber, to=momCell)

def update_todays_row():
    global sheet
    # finds next empty row and returns that row
    s = shelve.open('daytrack')

    try:
        rownum = sheet.find('', in_column=2).row
        s['rowNum'] = rownum
    finally:
        s.close()
    
    return rownum

def today_row_blank():
    #TODO fix this to base it on the date string and not next empty cell
    global sheet
    s = shelve.open('daytrack')
    blank = False
    try:
        if sheet.cell(s['rowNum'], 2).value == '':
            blank = True
    except KeyError:
        s['rowNum'] = sheet.find('', in_column=2)
        blank = True
    finally:
        s.close()
        return blank
if __name__ == "__main__":
    send_message()
