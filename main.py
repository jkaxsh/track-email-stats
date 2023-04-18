from datetime import date
from datetime import datetime
from fastapi import FastAPI
from num_replies import replies
import gspread
import imaplib
import os
from opens import opens
from opens import clean
import pytz

sheet = os.getenv("SECRET_LOCATION") + "sheetAuth.json"

app = FastAPI()

PORT = 587
EMAIL_SERVER = 'imap.gmail.com'

@app.get("/")
def run_myapp():
    return "[QUYKKDEV - SMTP] " + read_root()

def statsupdate(result,emails_values,rep):
    month = str(date.today())[5] + str(date.today())[6]
    if rep != 0:
        replies = rep
        sent = 0
    else:
        replies = result[0]
        j = 0
        if result[1] != " ":
            replies += result[1]
            j +=1
        sent = result[18+j]
        if result[19+j] != " ":
            sent += result[19+j]
        pos = 0
    for k in range(14,26):
        if month == emails_values[3][k]:
            pos = k
            break
    if emails_values[4][pos] == '':
        emails_values[4][pos] = 0
    if emails_values[5][pos] == '':
        emails_values[5][pos] = 0
    emails_values[4][pos] = int(emails_values[4][pos]) + int(sent)
    emails_values[5][pos] = int(emails_values[5][pos]) + int(replies)

def logout(imap):
    imap.close()
    imap.logout()

def login(email,password):
    imap = imaplib.IMAP4_SSL(EMAIL_SERVER)
    imap.login(email, password)
    return imap

def update(emails, emails_values):
    num = len(emails_values[0])-1
    def num_to_alpha(num):
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if num < 26:
            return alphabet[num]
        else:
            q, r = divmod(num, 26)
            return num_to_alpha(q-1) + alphabet[r]
    emails.batch_update([{
    'range': f'A1:{num_to_alpha(num)}{len(emails_values)}',
    'values': emails_values,
    }])  

@app.get("/")
def update_stats():

    print("Updating stats...")

    gc = gspread.service_account(filename=sheet)
    emails = gc.open("Emails").sheet1
    emails_values = emails.get_all_values()
    templates = gc.open("Emails").get_worksheet(1)
    templates_values = templates.get_all_values()

    i = 14
    ret = 0
    openz = 0
    while(i < len(emails_values)):
        if emails_values[i][2] == '':
            i+=1
            continue
        rep = 0
        open = 0
        if emails_values[i][1] != '' and emails_values[i][4] != 'REPLIED':
            if emails_values[i][4] != '' and emails_values[i][0] != "no":
                for enum in range(0,4):
                    if (emails_values[i][11+enum] == "" or emails_values[i][11+enum] == "no"):
                        if opens(emails_values[i][15+enum]) == 1: 
                            now_utc = datetime.now(pytz.utc)
                            tz = pytz.timezone(os.getenv("TIME_ZONE"))
                            now_eastern = now_utc.astimezone(tz)
                            emails_values[i][11+enum] = str(now_eastern)
                            month = int(str(date.today())[5:7]) + 13
                            if emails_values[6][month] == '':
                                emails_values[6][month] = 0
                            emails_values[6][month] = int(emails_values[6][month]) + 1
                            open += 1
                            openz += open
                    if emails_values[i][11+enum] == "":
                        emails_values[i][11+enum] = "no"
                email = os.getenv(f"EMAIL_{str(emails_values[i][1])}")
                password = os.getenv(f"PASSWORD_{str(emails_values[i][1])}")
                log = login(email,password)
                rep += replies(i, log, templates_values, emails_values)
                ret += rep
                logout(log)
            if(rep != 0):
                emails_values[i][4] = 'REPLIED'

        i+=1
    clean()
    statsupdate(f'''0 New replies and 0 Emails Sent.''',emails_values,ret)
    update(emails, emails_values)
    return f"{ret}#{openz}"