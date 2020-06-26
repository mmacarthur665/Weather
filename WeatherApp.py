"""
Program: Weather Forecast Application
Author: Michael Macarthur
Date: 06/15/2020

Purpose: This application will take user input for a zipcode and scrape relevant weather information from wunderground.
There will be a nicely designed GUI of some sort that will be what the user interfaces with.
"""



from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import lxml
import re
import pandas as pd
import os
import time
from datetime import datetime

# Chrome driver setting to not show extra chrome window running
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")

# Pandas preferences
pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)
pd.set_option('display.width', 200)


def userZip():
    """
    function will ask user what zipcode they want to see
    :return: zipcode
    """
    zipcode = input("Please enter the zipcode you want to see weather information for:")
    return zipcode

# Things I want this to grab
# 1. Name of area searched for and date
# 2. Current temp, daily high, daily low, weather status (sunny, partly cloudly, rain, etc.)
# 3. Same for tomorrow (with date)
# 4. Next 5 days

def timeCheck():
    """
    This checks if the current time is before or after 3pm EST. If before it will run the daytime version. If after
    it will point program to nighttime version.
    :return: D or N flag
    """
    if(datetime.utcnow().hour < 19):
        check = 'D'
        return check
    else:
        check = 'N'
        return check

def scraping(zipcode):
    """
    function will take user's zipcode and feed to wunderground. will also scrape relevant data and return data structure
    :param zipcode: returned by userZip
    :return: weather dataframe
    """
    loc_name_lst = []
    today_hi_lst = []
    today_lo_lst = []
    current_temp_lst = []
    current_day_type_lst = []
    tomorrow_hi_lst = []
    tomorrow_lo_lst=[]
    today_description_lst = []
    tomorrow_description_lst = []
    counter = 0

    url = 'https://www.wunderground.com/'
    driver = webdriver.Chrome(r'C:\Users\3183328\Desktop\Python Script Stuff\Chromdriver\chromedriver.exe', options=chrome_options)
    driver.get(url)
    time.sleep(3)
    driver.find_element_by_id('wuSearch').send_keys(zipcode) # enters zipcode from user
    time.sleep(2)
    driver.find_element_by_id('wuSearch').send_keys(Keys.ENTER)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    loc_name = driver.current_url

    while counter == 0:

        try:
            time.sleep(5)
            loc_name_split = loc_name.upper().split('/')
            loc_name_final = loc_name_split[6]+', '+loc_name_split[5]

        except IndexError:
            print("An issue occurred, please try again")
            continue

        else:
            loc_name_lst.append(loc_name_final)
            daily_high = driver.find_element_by_class_name('hi').text
            today_hi_lst.append(daily_high)
            daily_low = driver.find_element_by_class_name('lo').text
            today_lo_lst.append(daily_low)
            current_temp = soup.find('div', {'class':'current-temp'}).next_sibling()
            current_temp_lst.append(current_temp)
            current_day_type = soup.find('div', {'class':'condition-icon small-6 medium-12 columns'})
            current_day_type_lst.append(current_day_type)
            tomorrow_hi = soup.find('span', {'class': 'primary-temp has-secondary'})
            tomorrow_hi_lst.append(tomorrow_hi)
            tomorrow_lo = soup.find('span', {'class': 'secondary-temp ng-star-inserted'})
            tomorrow_lo_lst.append(tomorrow_lo)
            today_desc = soup.find('div', {'class': 'small-12 medium-4 large-4 columns forecast-wrap ng-star-inserted'})
            today_description_lst.append(today_desc)
            tomorrow_desc = soup.find('div', {'class': 'small-12 medium-4 large-4 columns forecast-wrap ng-star-inserted'}).next_sibling.next_sibling
            tomorrow_description_lst.append(tomorrow_desc)

            driver.quit()

            weather = pd.DataFrame(list(zip(loc_name_lst, today_hi_lst, today_lo_lst, current_temp_lst, current_day_type_lst,
                                    tomorrow_hi_lst, tomorrow_lo_lst, today_description_lst, tomorrow_description_lst)),
                           columns = ['Location', 'Today_high', 'Today_low', 'Current_Temp', 'Current_Day_Type',
                                      'Tomorrow_Hi', 'Tomorrow_Lo', 'Today_Description', 'Tomorrow_Description'])
            return weather
            #counter += 1

def cleaning(weather):
    """
    This function will take the data structure returned by scraper and parse out important parts. This will be the data
    presented to the user of the application
    :param weather: data structure returned by scraping
    :return: weather_clean
    """

    weather['Current_Temp'] = weather['Current_Temp'].apply(str)
    weather['Current_Temp'] = weather['Current_Temp'].str.split('>').str[1]
    weather['Current_Temp'] = weather['Current_Temp'].str.split('<').str[0]
    #weather['Current_Temp'] = weather['Current_Temp'].str.strip()
    weather['Current_Day_Type'] = weather['Current_Day_Type'].apply(str)
    weather['Current_Day_Type'] = weather['Current_Day_Type'].str.split('"">').str[1]
    weather['Current_Day_Type'] = weather['Current_Day_Type'].str.split('</p').str[0]
    #weather['Current_Day_Type'] = weather['Current_Day_Type'].str.strip()
    weather['Tomorrow_Hi'] = weather['Tomorrow_Hi'].apply(str)
    weather['Tomorrow_Hi'] = weather['Tomorrow_Hi'].str.split('to">').str[1]
    weather['Tomorrow_Hi'] = weather['Tomorrow_Hi'].str.split('</span>').str[0]
    #weather['Tomorrow_Hi'] = weather['Tomorrow_Hi'].str.strip()
    weather['Tomorrow_Lo'] = weather['Tomorrow_Lo'].apply(str)
    weather['Tomorrow_Lo'] = weather['Tomorrow_Lo'].str.split('to">').str[1]
    weather['Tomorrow_Lo'] = weather['Tomorrow_Lo'].str.split('</span>').str[0]
    #weather['Tomorrow_Lo'] = weather['Tomorrow_Lo'].str.strip()
    weather['Today_Description'] = weather['Today_Description'].apply(str)
    weather['Today_Description'] = weather['Today_Description'].str.split('modtoday">').str[2]
    weather['Today_Description'] = weather['Today_Description'].str.split('</a></div>').str[0]
    #weather['Today_Description'] = weather['Today_Description'].str.strip()
    weather['Tomorrow_Description'] = weather['Tomorrow_Description'].apply(str)
    weather['Tomorrow_Description'] = weather['Tomorrow_Description'].str.split('modtomorrow">').str[2]
    weather['Tomorrow_Description'] = weather['Tomorrow_Description'].str.split('</a></div>').str[0]
    #weather['Tomorrow_Description'] = weather['Tomorrow_Description'].str.strip()
    return weather
    #weather.to_csv(r'C:\Users\3183328\Desktop\Python Script Stuff\testoutput_step2.csv')

def printing(weather_clean):
    """
    This function will take the weather dataframe and print out sections of it as a summary
    :param weather: previously manipulated data structure
    :return: N/A
    """

    print("Today's Weather Summary for: ",weather_clean['Location'].to_string())
    print("--------------------------------------------------------------------------------------------")
    print("The current temperature is: ",weather_clean['Current_Temp'].to_string())
    print("The high for today is: ",weather_clean['Today_high'].to_string())
    print("The low for today is: ",weather_clean['Today_low'].to_string())
    print("The descrption of today's weather is: ",weather_clean['Today_Description'].to_string())
    print("--------------------------------------------------------------------------------------------")
    print("Tomorrow's Weather Forecast: ",weather_clean['Location'].to_string())
    print("The forecasted high for tomorrow is: ",weather_clean['Tomorrow_Hi'].to_string())
    print("The forecasted low for tomorrow is: ",weather_clean['Tomorrow_Lo'].to_string())
    print("The descrption of tomorrow's forecast is: ",weather_clean['Tomorrow_Description'].to_string())

def main():
    '''
    This function serves to run all other functions and reduce confusion. Will return nothing.
    :return: none
    '''
    pd.set_option('display.max_columns', 200)
    pd.set_option('display.max_rows', 200)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_colwidth', 2000)

    zipcode = userZip()
    check = timeCheck()
    if check == 'D':

        weather = scraping(zipcode = zipcode)
        weather_clean = cleaning(weather = weather)
        printing(weather_clean = weather_clean)

    else:
        print('you should probably write the code for the night time one')

main()
