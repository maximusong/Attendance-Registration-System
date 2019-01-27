#! /usr/bin/env python
from __future__ import print_function
import re, argparse, datetime, sys, requests
from smartcard.System import readers
from time import localtime, strftime, sleep

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from pprint import pprint

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# # If modifying these scopes, delete your previously saved credentials
# # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret_2.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#ACS ACR122U NFC Reader
#handshake cmd needed to initiate data transfer
COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00] 

# Disable the standard buzzer when a tag is detected, Source : https://gist.github.com/nixme/2717287
DISABLEBEEP = [0xFF, 0x00, 0x52, 0x00, 0x00]

# get all the available readers
r = readers()
reader =r[0]

def stringParser(dataCurr):
    if isinstance(dataCurr, tuple):
        temp = dataCurr[0]
        code = dataCurr[1]
    else:
        temp = dataCurr
        code = 0
    
    dataCurr = ''

    for val in temp:
        dataCurr += format(val, '#04x')[2:]

    dataCurr = dataCurr.upper()

    if (code == 144):
        return dataCurr

def readTag(page):
        try:
            connection = reader.createConnection()
            status_connection = connection.connect()
            connection.transmit(DISABLEBEEP)
            connection.transmit(COMMAND)

            resp = connection.transmit([0xFF, 0xB0, 0x00, int(page), 0x04])
            dataCurr = stringParser(resp)

            if(dataCurr is not None):
                return dataCurr
            else:
                print ("Something went wrong. Page " + str(page))
        except Exception,e: print (str(e))

# def writeTag(page, value):
#     if type(value) != str:
#         print "Value input should be a string"
#         exit()
#     while(1):
#         if len(value) == 8:
#             try:
#                 print "trying to write"
#                 connection = reader.createConnection()
#                 status_connection = connection.connect()
#                 connection.transmit(DISABLEBEEP)
#                 connection.transmit(COMMAND)
#                 WRITE_COMMAND = [0xFF, 0xD6, 0x00, int(page), 0x04, int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), int(value[6:8], 16)]

#                 resp = connection.transmit(WRITE_COMMAND)
#                 if resp[1] == 144:
#                     print "Wrote " + value + " to page " + str(page)
#                     break
#             except Exception, e:
#                 print e
#                 continue
#         else:
#             print "Must have a full 4 byte write value"
#             break

# Application starts here

# #START: THIS IS CODE FOR WRITING TO CARD
# #EXAMPLE: writing the hexadecimal string '00000000' into page 9
# page = 9
# data = '0000E86D'
# if len(data) == 8:
#     writeTag(page, data)
#     print "write success!!!!!"
# else:
#     raise argparse.ArgumentTypeError("Must have a full 4 byte write value")
# #END OF SNIPPET

# Read from page 9 of card
page = '9'

# Google sheets credentials
credentials = get_credentials()
http = credentials.authorize(httplib2.Http())
discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                'version=v4')
service = discovery.build('sheets', 'v4', http=http,
                          discoveryServiceUrl=discoveryUrl)

spreadsheetId = '1Bx59e7rxjh7joMw_yOR3T6McNlFGdjvCs0yLQBx5oCY'
rangeName = 'Sheet1'
value_input_option = 'USER_ENTERED'  # TODO: Update placeholder value.
insert_data_option = 'INSERT_ROWS'


while True:
    x = readTag(page)
    if x:
        print ("The value read from the card is", x)

        y = strftime("%H:%M", localtime())
        z = datetime.datetime.today().strftime('%Y-%m-%d')
        strhexnum = x[4:8]
        str_id = str(int(strhexnum, 16))
        str_time = str(y)
        str_date = str(z)
        myArray = [str_id, str_time, str_date]
        value_range_body = {
            'values' : [myArray]
        }
        
        # url = "http://localhost:5000/newdata" + "?" + "id=" + str_id + "&" + "time=" + str_time
        print ("ID Number:", str_id)
        print ("Time arrived:", str_time)
        print ("Date:", str_date)
        print (myArray)
            
        request = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=rangeName, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
        response = request.execute()
        pprint(response)
        sleep(15)
    sleep(0.5)
