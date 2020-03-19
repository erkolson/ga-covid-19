## Georgia COVID-19 tracker

The GA State Department of Public Health publishes a [report](https://dph.georgia.gov/covid-19-daily-status-report) each day of
the confirmed cases of COVID-19 within the state.  The trends are more important
than any single day's report so this script scrapes the site, parses the
confirmed cases data, the county breakdown, and appends each result to
the relevant csv file.


## How?
Clone the repository then create the virtual env:
```
cd ga-covid-19
python3 -m venv venv-scrape
source ./venv-scrape/bin/activate
pip install -U pip
pip install -r ./requirements.txt
```
Finally, execute the script to parse the website, update the csv files, and plot the trends.


## Breakage
The DOH has been changing their page quite a bit so this will probably break frequently, :-/
