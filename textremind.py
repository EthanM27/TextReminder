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
client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

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
            # TODO: Add options for every day/time combination
            date = datetime.now().strftime('%m/%d/%Y')
            hour = datetime.now().strftime('%H')
            day_name = datetime.now().strftime('%A')
            # fills in Day and Date for the row of the day if its 12:00am or todays row is non existent
            if today_row_blank(date) or (hour == "00" and not today_updated):
                s = shelve.open('daytrack')

                row_num = s['rowNum']
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

            # remind mom to take out trash
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
            print("loop completed at:", datetime.now())
        
            
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

def today_row_blank(date):
    global sheet
    s = shelve.open('daytrack')
    blank = False
    try:
        # if todays date cell is found, blank = false.
        cell = sheet.find(str(date), in_column=3)
        if cell:
            blank = False
            s['rowNum'] = cell.row
    except (KeyError, gspread.exceptions.CellNotFound) as e:
        # what to do if rowNum key is not in daytrack shelve file or if todays cell is not found.
        s['rowNum'] = sheet.find('', in_column=3).row
        blank = True
    finally:
        s.close()
        return blank

if __name__ == "__main__":
    send_message()
