import requests
import schedule
import time
from datetime import datetime
import csv
from bs4 import BeautifulSoup

# Main function
def main():
    # BeautifulSoup. Get website and parse to HTML.
    page = requests.get('https://www.worldometers.info/coronavirus/country/malaysia/')
    soup = BeautifulSoup(page.text, 'html.parser')

    # Step 1) Get the date of the last update from CSV file.
    # Step 2) Get the updated data scraped from website. The update date and number of cases.
    # Step 3) Check if new update date is actually a new update by comparing it to the last update.
    # Step 4) If its a new update, add it to the CSV file. Otherwise, do nothing.

    # CSV

    # Gets the date of last update as datetime object
    date_prev = datetime.strptime(getLastUpdateDate(), "%B %d, %Y")

    # date as datetime object
    date_curr = datetime.strptime(getNewUpdateDate(soup), "%B %d, %Y")

    # current time
    cTime = datetime.now().strftime("%A, %d %B | %H:%M%p")

    # Check to see if new update is actually 'new' and we are not adding the same data as previous
    if(date_curr > date_prev):
        print(cTime)
        print("New case. Adding to CSV...\n")
        # Get data (new cases) for the day
        cases_today = soup.find("div", class_="maincounter-number").find("span").contents[0]
        #Add data to CSV
        addToCSV(cases_today)

    else:
        print(cTime)
        print("No new cases!\n")

# Functions
def getLastUpdateDate():
    # Data pulled from CSV
    data_from_csv = []
    # Get date of last update
    with open('covid19_malaysia.csv', 'r') as file:
        reader = csv.reader(file, delimiter="|")
        for row in reader:
            data_from_csv.append(row)
    return data_from_csv[-1][0]

def getNewUpdateDate(parsedHTML):
    # Check date of current update
    # Date not formatted: E.g., 'Last updated: March 30, 2020, 23:01 GMT'
    date_raw = parsedHTML.find(attrs={"style":"font-size:13px; color:#999; text-align:center"}).contents[0]
    # Slice String to get just date
    return date_raw[14:-11]

def addToCSV(data):
    with open('covid19_malaysia.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow([getNewUpdateDate(), data])

# Program is scheduled to run every hour
schedule.every(1).hour.do(main)
while True:
    schedule.run_pending()
    time.sleep(1)