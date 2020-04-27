#!/usr/bin/env python

import click
import os
import re
import time
import pandas as pd
import matplotlib.pyplot as plt
from requests import get
from bs4 import BeautifulSoup
from datetime import date,timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

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
base_site = 'https://dph.georgia.gov/covid-19-daily-status-report'
confirmed_cases_rows = ["Total", "Deaths", "Hospitalized"]
county_cases_csv = "data/county-cases.csv"
county_deaths_csv = "data/county-deaths.csv"
totals_csv = "data/totals.csv"
testing_csv = "data/testing.csv"

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        scrape()

def parse_rows(table):
    # print("got a table:\n\n")
    rows = []
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        row = [i.text for i in td]
        if len(row) is not 0:
            rows.append(row)
    return rows

def parse_totals(rows, day):
    print('\nparsing totals: ' + str(day))
    totals_dict = {}
    totals_string = str(day) + ', '
    # rows = parse_rows(table)
    for row in rows[1:]:
        type = row[0].replace(u'\xa0', u'').replace(u' ', u'')
        count = re.split(r'[\(\s]', row[1])[0]
        print("{}: {}".format(type, count))
        if type in confirmed_cases_rows:
            totals_dict[type] = count

    for type in confirmed_cases_rows:
        totals_string += totals_dict[type] + ', '
    # remove the trailing ',' and add a newline
    totals_string = ','.join(totals_string.split(',')[:-1]) + '\n'
    with open(totals_csv, 'a') as f:
        f.write(totals_string)

def parse_counties(rows, day):
    county_cases = {}
    county_deaths = {}
    print('\nparsing counties: ' + str(day))
    # rows = parse_rows(table)
    for row in rows[1:]:
        if len(row) == 3:
            county = row[0].replace(u'\xa0', u'').lower()
            cases = row[1].replace(u'\xa0', u'').replace(u' ', u'')
            deaths = row[2].replace(u'\xa0', u'').replace(u' ', u'')
            print("{} county: {} cases, {} deaths".format(county, cases, deaths))
            if county in [county.lower() for county in counties]:
                county_cases[county] = cases
                county_deaths[county] = deaths

    county_cases_string = str(day)
    county_deaths_string = str(day)
    for county in [county.lower() for county in counties]:
        cases = '0'
        deaths = '0'
        if county in county_cases:
            cases = county_cases[county]
        if county in county_deaths:
            deaths = county_deaths[county]
        county_cases_string += ', ' + cases
        county_deaths_string += ', ' + deaths

    county_cases_string += "\n"
    county_deaths_string += "\n"
    with open(county_cases_csv, 'a') as f:
        f.write(county_cases_string)
    with open(county_deaths_csv, 'a') as f:
        f.write(county_deaths_string)

def parse_tests(rows, day):
    print('\nparsing tests: ' + str(day))
    test_string = ''
    # rows = parse_rows(table)
    for row in rows[1:]:
        tester = row[0]
        positive_tests = row[1]
        total_tests = row[2]
        print("{}: {} positive, {} total".format(tester, positive_tests, total_tests))
        test_string += str(day) + ', ' + tester + ', ' + positive_tests + ', ' + total_tests + "\n"
    with open(testing_csv, 'a') as f:
        f.write(test_string)

def parse_table(html_table, day):
    rows = parse_rows(html_table)
    first_cell = rows[0][0]
    if re.search('COVID-19 Confirmed Cases By County:', first_cell):
        parse_counties(rows, day)
    elif re.search('COVID-19 Confirmed Cases:', first_cell):
        parse_totals(rows, day)
    elif re.search('COVID-19 Testing By Lab Type:', first_cell):
        parse_tests(rows, day)
    else:
        print('Error: unknown table!')

@cli.command()
def scrape(day=date.today(),html=None):
    if html is None:
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)

        driver.get(base_site)
        time.sleep(5)
        html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
        base_soup = BeautifulSoup(html, 'html.parser')
        iframe = base_soup.iframe
        report_site = iframe['src']
        report_data = get(report_site, stream=True)
        soup = BeautifulSoup(report_data.content, 'html.parser')

        # import pdb; pdb.set_trace()

        # archive today's site
        today = date.today()
        filename = 'raw-pages/' + str(today) + '.html'
        with open(filename, 'w') as f:
            f.write(report_data.text)
    else:
        soup = BeautifulSoup(open(html), 'html.parser')

    for table in soup.find_all('table'):
        parse_table(table, day)


@cli.command()
def plot_totals():
    totals = pd.read_csv('data/totals.csv', sep=r'\s*,\s*',
        header=0, encoding='ascii', engine='python')
    plt.plot(totals['Date'], totals['Cases'], label="Confirmed Cases")
    plt.plot(totals['Date'], totals['Deaths'], label="Deaths")
    plt.plot(totals['Date'], totals['Hospitalized'], label="Hospitalized")
    plt.bar(totals['Date'],
            totals['Cases'].diff(),
            width=0.4,
            label="New Cases",
            color='lightsteelblue')
    plt.bar(totals['Date'],
            totals['Deaths'].diff(),
            width=0.4,
            label="New Deaths",
            color='palevioletred')
    plt.yscale("log")
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

@cli.command()
def plot_daily():
    totals = pd.read_csv('data/totals.csv', sep=r'\s*,\s*',
        header=0, encoding='ascii', engine='python')

    fs = 7 # smoothing factor in days

    smoothed_cases = totals['Cases'].rolling(fs, win_type='boxcar').sum()/fs
    plt.plot(smoothed_cases, smoothed_cases.diff(), label="Confirmed cases")

    smoothed_deaths = totals['Deaths'].rolling(fs, win_type='boxcar').sum()/fs
    plt.plot(smoothed_deaths, smoothed_deaths.diff(), label="Deaths")

    plt.yscale("log")
    plt.xscale("log")
    plt.legend()
    plt.title("Daily vs Totals")
    plt.show()

@cli.command()
def plot_counties():
    counties_data = pd.read_csv(county_cases_csv, sep=r'\s*,\s*',
        header=0, encoding='ascii', engine='python')
    x = counties_data['Date']
    for county in counties_data.columns.tolist()[1:]:
        plt.plot(x, counties_data[county], label=county)
    plt.xticks(rotation=45)
    plt.yscale("log")
    plt.legend()
    plt.show()

@cli.command()
@click.option('-f', '--filepath', default=None, required=False)
def re_parse(filepath):
    if filepath is None:
        for file in os.listdir('raw-pages'):
            day = file.split('.')[0]
            scrape(day, './raw-pages/' + file)
    else:
        # assumes filename is yyyy-mm-dd.html
        day = os.path.basename(filepath).split('.')[0]
        scrape(day, filepath)

if __name__ == "__main__":
    cli()
