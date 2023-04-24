
def stats(emails):
    i = 14
    dict = {}
    while(i < len(emails)):
        rep = 0
        opens = 0
        sent = 0
        if emails[i][3] != '' and emails[i][4] != '':
            if "REPLIED" in emails[i][4]:
                sent += int(emails[i][4][0]) + 1
            else:
                sent += int(emails[i][4]) + 1
            for j in range(1,5):
                if emails[i][j+4] != "no" and emails[i][j+4] != '':
                    rep += 1
                if emails[i][j+10] != "no" and emails[i][j+10] != '':
                    opens += 1
        if emails[i][3] not in dict:
            dict[emails[i][3]] = (sent,opens,rep)
        else:
            dict[emails[i][3]] = (dict[emails[i][3]][0] + sent,dict[emails[i][3]][1] + opens,dict[emails[i][3]][2] +rep)
        i+=1
    print(dict)
    return emails
