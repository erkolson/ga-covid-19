#!/usr/bin/env python

import re
from requests import get
from bs4 import BeautifulSoup
from datetime import date,timedelta
import matplotlib.pyplot as plt
import pandas as pd

counties = [
    'Appling',
    'Atkinson',
    'Bacon',
    'Baker',
    'Baldwin',
    'Banks',
    'Barrow',
    'Bartow',
    'Ben Hill',
    'Berrien',
    'Bibb',
    'Bleckley',
    'Brantley',
    'Brooks',
    'Bryan',
    'Bulloch',
    'Burke',
    'Butts',
    'Calhoun',
    'Camden',
    'Candler',
    'Carroll',
    'Catoosa',
    'Charlton',
    'Chatham',
    'Chattahoochee',
    'Chattooga',
    'Cherokee',
    'Clarke',
    'Clay',
    'Clayton',
    'Clinch',
    'Cobb',
    'Coffee',
    'Colquitt',
    'Columbia',
    'Cook',
    'Coweta',
    'Crawford',
    'Crisp',
    'Dade',
    'Dawson',
    'Decatur',
    'DeKalb',
    'Dodge',
    'Dooly',
    'Dougherty',
    'Douglas',
    'Early',
    'Echols',
    'Effingham',
    'Elbert',
    'Emanuel',
    'Evans',
    'Fannin',
    'Fayette',
    'Floyd',
    'Forsyth',
    'Franklin',
    'Fulton',
    'Gilmer',
    'Glascock',
    'Glynn',
    'Gordon',
    'Grady',
    'Greene',
    'Gwinnett',
    'Habersham',
    'Hall',
    'Hancock',
    'Haralson',
    'Harris',
    'Hart',
    'Heard',
    'Henry',
    'Houston',
    'Irwin',
    'Jackson',
    'Jasper',
    'Jeff',
    'Davis',
    'Jefferson',
    'Jenkins',
    'Johnson',
    'Jones',
    'Lamar',
    'Lanier',
    'Laurens',
    'Lee',
    'Liberty',
    'Lincoln',
    'Long',
    'Lowndes',
    'Lumpkin',
    'Macon',
    'Madison',
    'Marion',
    'McDuffie',
    'McIntosh',
    'Meriwether',
    'Miller',
    'Mitchell',
    'Monroe',
    'Montgomery',
    'Morgan',
    'Murray',
    'Muscogee',
    'Newton',
    'Oconee',
    'Oglethorpe',
    'Paulding',
    'Peach',
    'Pickens',
    'Pierce',
    'Pike',
    'Polk',
    'Pulaski',
    'Putnam',
    'Quitman',
    'Rabun',
    'Randolph',
    'Richmond',
    'Rockdale',
    'Schley',
    'Screven',
    'Seminole',
    'Spalding',
    'Stephens',
    'Stewart',
    'Sumter',
    'Talbot',
    'Taliaferro',
    'Tattnall',
    'Taylor',
    'Telfair',
    'Terrell',
    'Thomas',
    'Tift',
    'Toombs',
    'Towns',
    'Treutlen',
    'Troup',
    'Turner',
    'Twiggs',
    'Union',
    'Upson',
    'Walker',
    'Walton',
    'Ware',
    'Warren',
    'Washington',
    'Wayne',
    'Webster',
    'Wheeler',
    'White',
    'Whitfield',
    'Wilcox',
    'Wilkes',
    'Wilkinson',
    'Worth',
    'Unknown'
]
report_site = 'https://dph.georgia.gov/covid-19-daily-status-report'
county_counts = {}
county_csv = "data/counties.csv"
totals_csv = "data/totals.csv"

def parse_rows(table):
    rows = []
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        if len(row) is not 0:
            rows.append(row)
    return rows

def parse_totals(table):
    totals_string = str(date.today())
    print('parsing totals')
    rows = parse_rows(table)
    for row in rows:
        type = row[0].replace(u'\xa0', u'')
        count = row[1].split(' ')[0]
        print("{}: {}".format(type, count))
        totals_string = totals_string + ', ' + count

    totals_string += '\n'
    with open(totals_csv, 'a') as f:
        f.write(totals_string)

def parse_counties(table):
    print('parsing counties')
    rows = parse_rows(table)
    for row in rows:
        county = row[0].replace(u'\xa0', u'').lower()
        count = row[1].replace(u'\xa0', u'')
        print("{} county: {}".format(county, count))
        if county in [county.lower() for county in counties]:
            county_counts[county] = count

    county_string = str(date.today())
    for county in [county.lower() for county in counties]:
        count = '0'
        if county in county_counts:
            count = county_counts[county]
        county_string = county_string + ", " + count

    county_string += "\n"
    with open(county_csv, 'a') as f:
        f.write(county_string)

def parse_table(table):
    caption = table.find('caption').text
    if re.search('by County', caption):
        parse_counties(table)
    elif re.search('cases and deaths in Georgia', caption):
        parse_totals(table)
    else:
        print('Error: unknown table!')


def scrape():
    resp = get(report_site, stream=True)
    soup = BeautifulSoup(resp.content, 'html.parser')

    for table in soup.find_all('table'):
        parse_table(table)

    # archive site
    today = date.today()
    filename = 'raw-pages/' + str(today) + '.html'
    with open(filename, 'w') as f:
        f.write(resp.text)

def plot_totals():
    totals = pd.read_csv('data/totals.csv', sep=r'\s*,\s*',
        header=0, encoding='ascii', engine='python')
    x = totals['Date']
    y = totals['Cases']
    plt.plot(totals['Date'], totals['Cases'], label="Confirmed Cases")
    plt.plot(totals['Date'], totals['Deaths'], label="Deaths")
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

def plot_counties():
    counties_data = pd.read_csv('data/counties.csv', sep=r'\s*,\s*',
        header=0, encoding='ascii', engine='python')
    x = counties_data['Date']
    for county in counties_data.columns.tolist()[1:]:
        plt.plot(x, counties_data[county], label=county)
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    scrape()
    plot_totals()
    plot_counties()
