## Import useful libraries
import numpy as np 
import pandas as pd
import statistics
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import re
import codecs
import time
import datetime 

## Open & parse the html 
f=codecs.open("NYTMiniHTML.asp", 'r')
html = f.read()
parsed_html = BeautifulSoup(html)
body = parsed_html.find('body')

## Get the data within the script tags
scripts = body.find_all('script')
dataStr = scripts[0].text

## Get all the names and times
names = re.findall(re.escape('name":"')+"(.*?)"+re.escape('",'),dataStr)
times = re.findall(re.escape('solveTime":"')+"(.*?)"+re.escape('"}'),dataStr)

## Convert times to seconds
for index, each in enumerate(times):
    values = each.split(':')
    seconds = (int(values[0]) * 60) + (int(values[1]))
    times[index] = seconds

###############################
### Preparing Crosswords DF ###
###############################

crosswords = pd.read_csv('crosswords.csv')

todayDate = datetime.datetime.today().strftime('%-m/%-d/%y')
todayDay = datetime.datetime.now().strftime("%a")
numEntries = len(times)
medianTime = round(statistics.median(times), 2)

crosswordDF = pd.DataFrame(columns = ['ID', 'Date', 'DayOfWeek', 'NumEntries', 'MedianTime'])
ID = max(crosswords['ID']) + 1 
crosswordInfo = [ID, todayDate, todayDay, numEntries, medianTime]
crosswordDF.loc[0] = crosswordInfo

crosswords.append(crosswordDF).to_csv('crosswords.csv')

##########################
### Preparing Stats DF ###
##########################

import numpy as np 
import pandas as pd
import statistics
try: 
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import re
import codecs
import time
import datetime 

userDF = pd.read_csv('users.csv')
statsInfoRead = pd.read_csv('crosswordStats.csv')

for index, user in enumerate(names):
    userID = userDF[userDF['ScreenName'] == user]['UserID'].values[0]
    try: 
        rawTime = times[index]
        scaledTime = round(rawTime/medianTime, 2)
        rank = index + 1

    except: 
        rawTime = None 
        scaledTime = None
        rank = None 
    
    temp = pd.DataFrame(columns = ['UserID','CrosswordID', 'RawTime', 'ScaledTime', 'Rank'])
    statsInfo = [userID, ID, rawTime, scaledTime, rank]
    temp.loc[0] = statsInfo

    statsInfoRead = statsInfoRead.append(temp)


statsInfoRead.to_csv('crosswordStats.csv')    
