# Go to https://asuntojen.hintatiedot.fi/haku/
# Cycle through all location options
# Get the tabular data and save it down
from bs4 import BeautifulSoup
import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
d = webdriver.Chrome(options=chrome_options)
d.get('https://asuntojen.hintatiedot.fi/haku')
d.maximize_window()


# Select the city selector
citydiv = d.find_element_by_class_name("city").click()
# Enter the city name
city = d.find_element_by_id("cityField")
city.send_keys("Akaa\n") # Make sure to hit Enter after the name

# Pick out all of the postcodes, if any
postal_select = d.find_element_by_id("postalSelect")
postcodelist = postal_select.find_elements_by_tag_name("option")
for i in postcodelist:
    print(i.get_attribute("value"))

p2 = d.find_element_by_xpath("//ul[@class='ui-multiselect-checkboxes ui-helper-reset']")
#result = [{"postcode": postcodelist.get_attribute("ul")}
#          for postcode in postcodelist]

citytext = d.find_element_by_id("ui-id-1")
# d.find_element_by_id("cityField").send_keys("value","Akaa") #d.find_element_by_xpath("//input[@class='slim ui-autocomplete-input']")
#citytext.send_keys("Akaa")
d.implicitly_wait(10)
ActionChains(d).move_to_element(citytext).send_keys("value","Akaa").perform()

#d.find_element_by_xpath("//input[@class='ui-autocomplete ui-front ui-menu ui-widget ui-widget-content ui-corner-all']").send_keys("Akaa")

a = 1
print(d)
def get_table():
    # Need to know the Name, postcode, and then increment the page number
    # Should also append the postcode to the row to keep track of it
    # This implies we should only make one postcode query at a time
    # Could also append the date the code is run[


    r = requests.get(
        "https://asuntojen.hintatiedot.fi/haku/?c=Akaa&cr=1&ps=37800&ps=37830&ps=37900&ps=37910&t=4&l=0&z=1&search=1&sf=0&so=a&renderType=renderTypeTable&submit=%C2%AB+edellinen+sivu")
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup.prettify())
    table = soup.select("#mainTable")
    return table


def get_print_table():
    r = requests.get(
        "https://asuntojen.hintatiedot.fi/haku/?c=Akaa&cr=1&ps=37800&ps=37830&ps=37900&ps=37910&amin=&amax=&renderType=renderTypeTable&print=1&search=1&submit=Tulosta")

    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup.prettify())
    table = soup.select("#mainTable")

def scrape_data():
    table = get_table()

    output_rows = []
    for table_row in table[0].findAll('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_rows.append(output_row)
    with open('output.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(output_rows)
    x = 1
