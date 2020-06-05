# NYT_Mini

## Project Overview 
The New York Times has a daily mini crossword and an associated leaderboard, which allows friends to compete to see who completes the crossword the fastest. The goal of this project is to collect data on my NYT Leaderboard, store it, and make analytics available. 

## Technology Used
This project takes in the HTML code of my NYT Mini Leaderboard Page, extracted from the page source (via Google Chrome). Then, a Python script reads in that HTML and parses it in order to extract the data. The data is then stored in a relational database with multiple tables. Finally, the data is leveraged to create analytics on the individual crosswords and user performances. I have build several methods in Python to quickly produce these.  

## Metrics Generated
Scaled Time - time of completion for a crossword divided by median of all completion times 

Green Performance - any crossword completion time at or better the median of all completion times 

Green Rate - % of performances that were green performances

Average Scaled Time - average of a user's Scaled Times (available with and without outliers) 

Green Rate Rank - rank of a user's green rate compared with all other user green rates

Scaled Rank - rank of a user's average scaled time compared with all other user average scaled times

Buddy Score - score used to quantify how close two user performances are on a day-to-day basis; uses basic concepts of euclidean distance and adjusts metric to account for number of mutual crosswords (more mutual crosswords --> stronger buddy score) 

Foe Score - score used to quantify how far two user performances are on a day-to-day basis; uses same concepts as buddy score

## Findings 
- Completing more crosswords has no significant impact on crossword performance 



- Saturday is the hardest day of the week, but otherwise there is no significant difference in performance on a daily basis
![alt text](https://github.com/aks5bx/NYT_Mini/blob/master/CrosswordPerformancebyDOW.png)



## Future Work 
- Refine buddy score and foe score; the current method of adjusting for number of mutual crosswords often overestates the importance of mutual crosswords (although this is largely rectified as the data set increases in size) 
- Utilize collaborative filtering in order to predict performance of a singe user based on performances of other users 
- Automate process (currently process is almost fully automated, but NYT CAPTCHA cannot be bypassed by webdriver) 
