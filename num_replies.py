from datetime import datetime
import pytz
import os
from pathlib import Path
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

def replies(i, imap, templates_values, emails_values):

    # select the inbox
    imap.select('inbox')
    replies = 0

    # search for all messages that are replies
    for j in range(4):
        lett = 5 + j
        if (emails_values[i][lett] == "no" or emails_values[i][lett] == ""):
            if (emails_values[i][3] != ''):
                preset = int(emails_values[i][3]) + 2
                if preset > len(templates_values) or preset < 2:
                    emails_values[i][10] += " | " + '(Preset does not exist:' + 'E' + str(int(emails_values[i][4]) + 1) + ')'
                    emails_values[i][3] = ""
                    print('That preset does not exist')
                    break
                lsub = 1 + (3*j)
                if not (templates_values[preset][lsub] == ''):
                    Subject = templates_values[preset][lsub]
                else:
                    continue
                vars_dict = {}    
                weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
                week_day = weekDays[datetime.now().weekday()]                            
                for j in range(11,len(emails_values[0])):
                    if emails_values[13][j] != '':
                        if emails_values[i][j] != '':
                            vars_dict[str(emails_values[13][j])] = str(emails_values[i][j])
                try:
                    Subject = Subject.format(week_day = week_day, **vars_dict)
                except KeyError as e:
                    missing_variable = str(e).strip("'")
                    emails_values[i][10] += " | " + '(Variable: "' + missing_variable + '" is missing: ' "Reply Verification"+ ')'                
                    print(f"The variable '{missing_variable}' is missing from your sheet")
                    continue
                From = emails_values[i][2]
                typ, data = imap.search(None, f'FROM "{From}" SUBJECT "{Subject}"')
                num_replies = len(data[0].split())
                if emails_values[i][lett] == '':
                    emails_values[i][lett] = "no"
                if num_replies > 0:
                    now_utc = datetime.now(pytz.utc)
                    tz = pytz.timezone(os.getenv("TIME_ZONE"))
                    now_eastern = now_utc.astimezone(tz)
                    emails_values[i][lett] = str(now_eastern)
                    replies += 1

    return replies


