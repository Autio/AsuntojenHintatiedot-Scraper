# -*- coding: iso-8859-1 -*-
# Go to https://asuntojen.hintatiedot.fi/haku/
# Cycle through all location options
# Get the tabular data and save it down
from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from functools import reduce
import time

# Keep track of stats
postcode_count = 0
city_count = 0

# Configuration
save_in_one_file = True

def get_table(c, p, pg):
    # Return the HTML of the correct search term by city, postcode and page
    city = c
    postcode = p
    pagenumber = pg
    # Need to know the Name, postcode, and then increment the page number until no more data is available
    # Should also append the postcode to the row to keep track of it
    # This implies we should only make one postcode query at a time
    # Could also append the date the code is run[

    request = "https://asuntojen.hintatiedot.fi/haku/?c=" + city + "&cr=1&ps="+ postcode + "&t=1&l=0&z="+ str(pagenumber) + "&search=1&sf=0&so=a&renderType=renderTypeTable&search=1"
    # Reference
    # https://asuntojen.hintatiedot.fi/haku/?c=Akaa&cr=1&ps=37800&nc=5&l=0&z=1&search=1&sf=0&so=a&renderType=renderTypeTable&search=1
    # https://asuntojen.hintatiedot.fi/haku/?c=Espoo&cr=1&ps=02100&nc=112&amin=&amax=&renderType=renderTypeTable&search=1
    # https://asuntojen.hintatiedot.fi/haku/?c=Espoo&cr=1&ps=02100&t=3&l=0&z=2&search=1&sf=0&so=a&renderType=renderTypeTable&submit=seuraava+sivu+%C2%BB

    r = requests.get(request)
    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.select("#mainTable")
    return table


def get_print_table():
    r = requests.get(
        "https://asuntojen.hintatiedot.fi/haku/?c=Akaa&cr=1&ps=37800&ps=37830&ps=37900&ps=37910&amin=&amax=&renderType=renderTypeTable&print=1&search=1&submit=Tulosta")

    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup.prettify())
    table = soup.select("#mainTable")

def is_valid_row(cell):
    # Assume the year built field is always filled
    if(cell.isnumeric()):
        return True
    else:
        return False


def scrape_data_for_table(table, city, postcode):

    output_rows = []
    for table_row in table[0].findAll('tr'):
        columns = table_row.findAll('td')
        output_row = []

        # Skip blank rows
        if len(columns) == 0:
            continue

        try:
            year_built = columns[6].text
        except:
            year_built = ""

        # Check if we should add the row or not
        if is_valid_row(year_built):

            # Keep track of city
            output_row.append(city)
            # Prepend postcode to keep track of specific location
            output_row.append(postcode)
            for column in columns:
                # Some kind of data handling
                output_row.append(column.text)
            output_rows.append(output_row)

    return output_rows

def save_data(output_rows, outputfile):
    with open(outputfile + '.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)

def loadcities():
    citynames = []

    alphabet = "E" #BCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ"
    for letter in alphabet:
        #d.get('https://asuntojen.hintatiedot.fi/haku/')

        citydiv = d.find_element_by_class_name("city").click()
        city = d.find_element_by_id("cityField")
        city.send_keys(letter)
        time.sleep(0.5)
        citylist = d.find_element_by_xpath("//ul[@class='ui-autocomplete ui-front ui-menu ui-widget ui-widget-content ui-corner-all']")
        print(citylist.text)
        if citylist.text != "":
            citynames.append(citylist.text.split("\n"))
        citynames[:] = [x for x in citynames if x]
        flatten = lambda l: [item for sublist in l for item in sublist]
        city.clear()
        time.sleep(.5)
    x = 1
    print(citynames)
    citynames = reduce(lambda x, y: x + y, citynames)

    return citynames

# Initialize Selenium
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
d = webdriver.Chrome(options=chrome_options)
d.get('https://asuntojen.hintatiedot.fi/haku/')
d.set_window_size(1200, 920)
#d.maximize_window()

def main():

    # Go through the alphabet and load the city options
    citynames = loadcities()
    d.get('https://asuntojen.hintatiedot.fi/haku/')

    # Select the city selector
    citydiv = d.find_element_by_class_name("city").click()
    # Enter the city name
    city_element = d.find_element_by_id("cityField")

    data = []
    final_result = []

    # Main loop
    for city in citynames:
        d.get('https://asuntojen.hintatiedot.fi/haku/')
        data = []
        # Select the city selector
        citydiv = d.find_element_by_class_name("city").click()
        # Enter the city name
        city_element = d.find_element_by_id("cityField")

        print("\nLoading data for " + city +"\n")
        city_element.send_keys(str(city)+"\n") # Make sure to hit Enter after the name
        time.sleep(.5)

        # Pick out all of the postcodes, if any
        postal_select = d.find_element_by_id("postalSelect")
        postcodelist = postal_select.find_elements_by_tag_name("option")
        postcodes = []
        for i in postcodelist:
            postcodes.append(i.get_attribute("value"))

        for p in postcodes:
            print("Loading data for postcode " + p)
            # Handle the potential for multiple pages
            pg = 1
            is_data = True

            while is_data:
                table = get_table(city, p, pg)
                scrapedtable = scrape_data_for_table(table, city, p)
                pg += 1
                if scrapedtable == []:
                    is_data = False

                data.append(scrapedtable)
        time.sleep(1)
        # Need to re-find the element after the page refresh
        city_element = d.find_element_by_id("cityField")
        city_element.clear()

        # Handle empty dataset
        try:
            data = reduce(lambda x, y: x + y, data)
        except:
            # Don't write if there's no data
            continue

        if data:
            if save_in_one_file:
                final_result.extend(data)
            else:
                save_data(data, city)
            time.sleep(1)

    if save_in_one_file:
        # Now do the actual saving
        save_data(final_result, "Final result")

main()

