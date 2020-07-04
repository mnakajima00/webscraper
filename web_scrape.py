import requests
import schedule
import time
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import csv
from bs4 import BeautifulSoup


def start():
    schedule.every(30).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)

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
    date_prev = datetime.strptime(getLastUpdate()[0], "%B %d, %Y")

    # date as datetime object
    date_curr = datetime.strptime(getNewUpdateDate(soup), "%B %d, %Y")

    # current time
    cTime = datetime.now().strftime("%A, %d %B | %H:%M%p")

    # Check to see if new update is actually 'new' and we are not adding the same data as previous
    if(date_curr >= date_prev):
        total_cases = soup.find("div", class_="maincounter-number").find("span").contents[0].replace(',','').strip() #format '2,166 ' -> '2166'
        new_cases = int(total_cases) - int(getLastUpdate()[1])
        total_deaths = soup.find_all("div", class_="maincounter-number")[1].find("span").contents[0].replace(',','')
        total_recovered = soup.find_all("div", class_="maincounter-number")[2].find("span").contents[0].replace(',','')
        active_cases = int(total_cases) - int(total_deaths) - int(total_recovered)
        row = [date_curr.strftime("%B %d, %Y"), total_cases, str(active_cases), str(new_cases), total_deaths, total_recovered]
        if(date_curr > date_prev):
            # New datas for the day
            print(cTime)
            print("New cases: "+str(new_cases)+"\nAdding to CSV...\n")
            # Add data to CSV
            addToCSV(row)
        elif( date_curr == date_prev and row[3] != '0' ):
            # Update datas for the day
            new_cases = int(total_cases) - int(getDataAsArray()[-2][1])
            row = [date_curr.strftime("%B %d, %Y"), total_cases, str(active_cases), str(new_cases), total_deaths, total_recovered]
            print(cTime)
            print("Updating data: "+str(new_cases)+"\nAdding to CSV...\n")
            # Update existing data for current date
            updateData(row)
        else:
            print(cTime)
            print("No new cases!\n")

# Functions
def getDataAsArray():
    # Data pulled from CSV
    data_from_csv = []
    # Get date of last update
    with open('covid19_malaysia.csv', 'r') as file:
        read = csv.reader(file, delimiter=",")
        for row in read:
            data_from_csv.append(row)
    return data_from_csv

def getLastUpdate():
    return getDataAsArray()[-1]

def updateData(updatedRow):
    tempArr = getDataAsArray()
    tempArr[-1] = updatedRow
    with open('covid19_malaysia.csv', 'w', newline='')as file:
        writer = csv.writer(file, delimiter=',')
        for row in tempArr:
            writer.writerow(row)

def init():
    dataset = pd.read_csv('covid19_malaysia.csv', delimiter=',')
    dataset['Date'] = pd.to_datetime(dataset['Date'])
    plt.plot(dataset['Date'], dataset['Active Cases'])

def animate(i):
    newData = pd.read_csv('covid19_malaysia.csv', delimiter=',')
    newData['Date'] = pd.to_datetime(newData['Date'])
    plt.cla()
    plt.plot(newData['Date'], newData['Active Cases'])

def getNewUpdateDate(parsedHTML):
    # Check date of current update
    # Date not formatted: E.g., 'Last updated: March 30, 2020, 23:01 GMT'
    date_raw = parsedHTML.find(attrs={"style":"font-size:13px; color:#999; text-align:center"}).contents[0]
    # Slice String to get just date
    return date_raw[14:-11]

def addToCSV(row):
    with open('covid19_malaysia.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(row)

# Program is scheduled to run every hour
main()
main_thread = threading.Thread(target=start)
main_thread.start()
ani = FuncAnimation(plt.gcf(), animate, init_func=init,interval=500)
plt.show()