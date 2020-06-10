# Go to https://asuntojen.hintatiedot.fi/haku/
# Cycle through all location options
# Get the tabular data and save it down
from bs4 import BeautifulSoup
import requests
import csv

r = requests.get("https://asuntojen.hintatiedot.fi/haku/?c=Akaa&cr=1&ps=37800&ps=37830&ps=37900&ps=37910&amin=&amax=&renderType=renderTypeTable&print=1&search=1&submit=Tulosta")

soup = BeautifulSoup(r.text, 'html.parser')
#print(soup.prettify())
table = soup.select("#mainTable")
#print(table)
#print(table[0])
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