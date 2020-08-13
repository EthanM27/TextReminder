import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    number = request.form['From']
    message_body = request.form['Body']

    resp = MessagingResponse()
    resp.message('Hello {}, you said: {}'.format(number, message_body))
    return str(resp)
# use creds to create a client to interact with the Google Drive API
# scope = [
#     'https://www.googleapis.com/auth/spreadsheets',
#     'https://www.googleapis.com/auth/drive'
# ]
# creds = ServiceAccountCredentials.from_json_keyfile_name('./client_secret.json', scope)
# client = gspread.authorize(creds)

# # Find a workbook by name and open the first sheet
# # Make sure you use the right name here.
# sheet = client.open("Education and Fitness Tracking").sheet1

# Extract and print all of the values
# cell = sheet.acell("B4")
# print(cell)

if __name__ == '__main__':
    app.run(debug=True)