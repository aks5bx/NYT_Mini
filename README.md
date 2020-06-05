# NYT_Mini

## Project Overview 
The New York Times has a daily mini crossword and an associated leaderboard, which allows friends to compete to see who completes the crossword the fastest. The goal of this project is to collect data on my NYT Leaderboard, store it, and make analytics available. 

## Technology Used
This project takes in the HTML code of my NYT Mini Leaderboard Page, extracted from the page source (via Google Chrome). Then, a Python script reads in that HTML and parses it in order to extract the data. The data is then stored in a relational database with multiple tables. Finally, the data is leveraged to create analytics on the individual crosswords and user performances. I have build several methods in Python to quickly produce these.  
