## Importing libraries to use
import pandas as pd 
import numpy as np 
from scipy import stats
import math
import matplotlib.pyplot as plt
import pylab

################################
### DataFrame initialization ###
################################

## Setting these values to "password" strings - if they are set, data structures will be initialized
needsInit = ''
initializeRanks = ''

## Initializing data structures (if password is set)
if needsInit == 'Needs To Be Initialized':
    col_names =  ['ID', 'Date', 'DayOfWeek', 'NumEntries', 'MedianTime']
    crosswords  = pd.DataFrame(columns = col_names)
    crosswords.to_csv('crosswords.csv')

    col_names =  ['UserID', 'CrosswordID', 'RawTime', 'ScaledTime', 'Rank']
    crosswordStats  = pd.DataFrame(columns = col_names)
    crosswordStats.to_csv('crosswordStats.csv')

    col_names = ['UserID', 'Name', 'ScreenName', 'LaptopOrPhone']
    users = pd.DataFrame(columns = col_names)
    users.to_csv('users.csv')

######################################
### Read in initialized dataframes ###
######################################

## Contains meta data on the crossword
crosswords = pd.read_csv('crosswords.csv')
## Contains users + user stats
crosswordStats = pd.read_csv('crosswordStats.csv')
## Contains meta data on users 
users = pd.read_csv('users.csv')

## Initialize ranks if needed
if initializeRanks == 'Initialize Ranks': 
    for i in range(1, 31): 
        df = crosswordStats[crosswordStats['CrosswordID'] == i]
        df['Rank'] = df['RawTime'].rank().astype('int')
        crosswordStats.loc[crosswordStats['CrosswordID'] == i, 'Rank'] = df['Rank'].astype('int32')

    crosswordStats['Rank'] = crosswordStats['Rank'].astype('int')
    crosswordStats.to_csv('crosswordStats.csv')


###############################
### Defining useful methods ###
###############################

## This subsets the crosswords stats dataframe to include data on a single user
def getUserDF(userID, crosswordID):
    df = crosswordStats[crosswordStats['UserID'] == userID]
    if crosswordID != None: 
        df = df[df['CrosswordID'] == crosswordID]
    return df

## Produces baseline performance statistics for a user
def getUserCrosswordStats(userID, crosswordID):
    df = getUserDF(userID, crosswordID)
    print('Raw Time :', df['RawTime'].values, ' seconds')
    print('Scaled Time :', df['ScaledTime'].values, ' of the median')
    print('Rank :', df['Rank'].values, ' th/st/rd place')

## Gets the average scaled time for a user
## limitDays allows the user to get stats on their last __ days  
def getUserAvgScaledTime(userID, limitDays): 
    df = getUserDF(userID, None)
    df = df.sort_values(by='CrosswordID', ascending=False)

    if limitDays != None: 
        df = df.head(limitDays)

    return round(df['ScaledTime'].mean(), 4)

## Same as method above, but removes outliers
## limitDays allows the user to get stats on their last __ days  
def getUserAvgScaledTimeNoOutliers(userID, limitDays): 
    df = getUserDF(userID, None)
    df = df.sort_values(by='CrosswordID', ascending=False)

    if limitDays != None: 
        df = df.head(limitDays)

    df = df[['UserID' , 'ScaledTime']]

    df = df[np.abs(df.ScaledTime-df.ScaledTime.mean()) <= (3*df.ScaledTime.std())]
    df = df[~(np.abs(df.ScaledTime-df.ScaledTime.mean()) > (3*df.ScaledTime.std()))]

    return round(df['ScaledTime'].mean(), 4)

## Retrieves the green rate for a user 
## Green rate is the % of crosswords a user complete at or better than the median performance
## limitDays allows the user to get stats on their last __ days  
def getUserGreenRate(userID, limitDays): 
    df = getUserDF(userID, None)
    df = df.sort_values(by='CrosswordID', ascending=False)

    if limitDays != None: 
        df = df.head(limitDays)

    totalRows = len(df)
    greenRows = len(df[df['ScaledTime'] <= 1])

    return round(greenRows / totalRows, 4)
    
## Gets the user rank based on the green rate metric
def getGreenRateRank(userID): 
    userIDs = list(set(list(crosswordStats['UserID'])))
    
    vals = []

    for user in userIDs: 
        vals.append(getUserGreenRate(user, None))

    array = np.array(vals)

    temp = array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(array))

    index = userID - 1

    return ranks[index]

## Gets the user rank based on the scaled times
def getScaledRank(userID): 
    userIDs = list(set(list(crosswordStats['UserID'])))
    
    vals = []

    for user in userIDs: 
        vals.append(getUserAvgScaledTime(user, None))

    array = np.array(vals)

    temp = array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(array))

    index = userID - 1

    return ranks[index]

## Same as method above, but removes outliers
def getScaledRankNoOutliers(userID): 
    userIDs = list(set(list(crosswordStats['UserID'])))
    
    vals = []

    for user in userIDs: 
        vals.append(getUserAvgScaledTimeNoOutliers(user, None))

    array = np.array(vals)

    temp = array.argsort()
    ranks = np.empty_like(temp)
    ranks[temp] = np.arange(len(array))

    index = userID - 1

    return ranks[index]

## Turns a userID into their username
def getUserName(userID):
    return users[users['UserID'] == userID]['Name'].values[0]

## Turns a userID into their screen name
def getScreenName(userID):
    return users[users['UserID'] == userID]['ScreenName'].values[0]

## Generates a crossword "buddy" for a user 
## A crossword budy is someone who performs most similarly to a user on a day to day basis 
## Uses basic principles of euclidean distance and adjusts the scores to account number of shared crosswords 
## (If someone has done many mutual crosswords with another user, they are more likely to be buddies)
def getBuddy(userID): 
    crosswordsCompleted = list(set(getUserDF(userID, None)['CrosswordID']))
    otherUsers = list(set(crosswordStats['UserID']))

    otherUsers.remove(userID)

    distances = [0] * 50
    sharedCrosswords = [0] * 50

    for crosswordNum in crosswordsCompleted: 
        myTime = getUserDF(userID, crosswordNum)['ScaledTime'].values[0]        
        
        for user in otherUsers: 
            otherUser = getUserDF(user, crosswordNum)
            otherUserTime = otherUser['ScaledTime'].values

            if len(otherUserTime) < 1  or (np.isnan(otherUserTime).any()):
                continue
            else: 
                timeDiff = abs(myTime - otherUserTime[0])
                distances[int(user)] += timeDiff
                sharedCrosswords[int(user)] += 1

    for index, distance in enumerate(distances): 
        if sharedCrosswords[index] == 0: 
            distances[index] = 10000000
        else: 
            distances[index] = (distance / sharedCrosswords[index]) / sharedCrosswords[index]

    m = min(i for i in distances if i > 0)

    minInd = distances.index(m)

    print('User: ', getUserName(userID), '-------   Buddy: ', getUserName(minInd))
  #  print(m)

    return minInd

## Same idea as the buddy system, but instead is the user you are least similar to in day to day performance
def getFoe(userID): 
    crosswordsCompleted = list(set(getUserDF(userID, None)['CrosswordID']))
    otherUsers = list(set(crosswordStats['UserID']))

    otherUsers.remove(userID)

    distances = [0] * 50
    sharedCrosswords = [0] * 50

    for crosswordNum in crosswordsCompleted: 
        myTime = getUserDF(userID, crosswordNum)['ScaledTime'].values[0]        
        
        for user in otherUsers: 
            otherUser = getUserDF(user, crosswordNum)
            otherUserTime = otherUser['ScaledTime'].values

            if len(otherUserTime) < 1  or (np.isnan(otherUserTime).any()):
                continue
            else: 
                timeDiff = abs(myTime - otherUserTime[0])
                distances[int(user)] += timeDiff
                sharedCrosswords[int(user)] += 1

    for index, distance in enumerate(distances): 
        if sharedCrosswords[index] == 0: 
            distances[index] = 10000000
        else: 
            distances[index] = (distance / sharedCrosswords[index]) * sharedCrosswords[index]

    m = max(i for i in distances if i < 10000000)

    minInd = distances.index(m)

    print('User: ', getUserName(userID), '-------   Foe: ', getUserName(minInd))
  #  print(m)

    return minInd


## Prints out buddies
print('CROSSWORD BUDDIES')
for i in range(1, 27):
    getBuddy(i)
    print('---------------------------------')

## Prints out foes
print('CROSSWORD FOES')
for i in range(1, 27):
    getFoe(i)
    print('---------------------------------')



##############
### GRAPHS ###
##############

## Crosswords by Day of the Week
totalCrosswordStats = pd.merge(crosswords, crosswordStats, left_on='ID', right_on='CrosswordID')
totalCrosswordStats = totalCrosswordStats[['DayOfWeek','MedianTime']]
totalCrosswordStats = totalCrosswordStats.groupby('DayOfWeek').mean()

# plt.figure()
totalCrosswordStats.plot.bar()
plt.title('Crossword Performance by Day of Week')
plt.xlabel('Day of the Week')
plt.ylabel('Time (seconds)')
plt.show()

## Median Time vs # of Crosswords Done
times = []
numCrosswords = []
for i in range(1, 27):
    numCrossword = len(getUserDF(i, None))
    avgTime = sum(getUserDF(i, None).dropna()['ScaledTime']) / numCrossword

    times.append(avgTime)
    numCrosswords.append(numCrossword)


plt.scatter(numCrosswords, times)
plt.title('Average Scaled Time vs Number of Crosswords')
plt.xlabel('Number of Crosswords')
plt.ylabel('Average Scaled Time (time / medianTime)')
plt.show()

## Completion Rate 
maxCrosswords = max(crosswords['ID'])
completionRates = []
for i in range(1, 27):
    completionRates.append(len(getUserDF(i, None)) / maxCrosswords)

## Reports the crossword completion rate across all users
## Of all the possible crosswords users could have complete, what % did they complete
print('Crossword Completion Rate ', round(sum(completionRates) / len(completionRates), 1) * 100, '%')