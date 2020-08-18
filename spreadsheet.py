import gspread
import shelve
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

'''
Continuously running program that waits for an sms message then updates a google sheet to track personal trends in
coding and working out

Designed to be run at the same time as textremind.py
'''
#NOTE: Cell indexes start at (1,1)
s = shelve.open('daytrack')

#initialize column offset vals
try:
    s['COL_OFFSET_CODING'] = 2
    s['COL_OFFSET_EX'] = 10
    s['ETHAN_COL'] = {'C': 4, 'W': 12}
    s['MATHIEU_COL'] = {'C': 5, 'W': 13}
finally:
    s.close()

app = Flask(__name__)
file = open('phonenumbers', 'r')
text = file.readlines()
people = {text[1].strip(): 'Ethan', text[2].strip(): 'Mathieu', text[3].strip(): 'Nikola'}
commands = ['coded', 'worked out', 'commands']

# google sheets setup
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('./client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
sheet = client.open("Education and Fitness Tracking").sheet1

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    global people
    global sheet
    global commands
    number = request.form['From']
    sender = people[number]
    message_body = request.form['Body']
    resp = MessagingResponse()

    # TODO: add option to update previous dates through text.
    # TODO: add status command to see who has worked out
    # TODO: add progress command to see working out and coding trends for week/month
    #check for sender and message type to know which data to update
    if (sender == 'Ethan') or (sender == 'Mathieu'):
        if message_body.lower() == commands[0]:
            update_cell(sender, 'coded')
            resp.message('The google sheet has been updated')
        
        if message_body.lower() == commands[1]:
            update_cell(sender, 'worked out')
            resp.message('The google sheet has been updated')
        
        if message_body.lower() == commands[2]:
            resp.message('Commands are: {}'.format(', '.join(commands)))  
    return str(resp)

def update_cell(person, action):
    global sheet
    date = datetime.now().strftime('%m/%d/%Y')
    day_name = datetime.now().strftime('%A')
    s = shelve.open('daytrack')

    #TODO: need to make sure to not override existing change sent in
    if person == 'Ethan':
        if action == 'coded':
            sheet.update_cell(s['rowNum'], s['ETHAN_COL']['C'], True)
        elif action == 'worked out':
            sheet.update_cell(s['rowNum'], s['ETHAN_COL']['W'], True)
    elif person =='Mathieu':
        if action == 'coded':
            sheet.update_cell(s['rowNum'], s['MATHIEU_COL']['C'], True)
        elif action == 'worked out':
            sheet.update_cell(s['rowNum'], s['MATHIEU_COL']['W'], True)
    
    s.close()


if __name__ == '__main__':
    app.run(debug=True)