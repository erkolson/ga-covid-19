## Georgia COVID-19 tracker

The GA State Department of Public Health publishes a [report](https://dph.georgia.gov/covid-19-daily-status-report) each day of
the confirmed cases of COVID-19 within the state.  The trends are more important
than any single day's report so this script scrapes the site, parses the
data for confirmed cases, counties, testing, and appends each result to
the relevant csv file in `data/`.


## How to use?

The installation is no longer a simple pip install * .  You will need a copy
of firefox, and the geckodriver to run firefox from selenium.  In OS X, you
can:
```
brew install geckodriver
```
But pay attention to the [version compatibility chart](https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html)

Then, clone the repository and create the virtual env:
```
cd ga-covid-19
python3 -m venv venv-scrape
source ./venv-scrape/bin/activate
pip install -U pip
pip install -r ./requirements.txt
```
Finally, execute the script to parse the website, update the csv files, and plot the trends.
```
./scrape.py
```

###### * Why?

On 3/28, the report site started using js to pull the actual report data into an
iframe, for good measure.  To render the js and get the actual report data, a
number of options were tried:
*   `Dryscrape` looked promising but required installing qt, then an [ugly hack](https://stackoverflow.com/a/42809) to install webkit.
*   `requests-html` looked even more promising but after some initial investigation
    it was not returning the data expected and I noticed that only python 3.6
    is supported.  I did not want to install yet another python to troubleshoot further.
*   That led to `selenium`, it is a massive and unwieldy hammer but it smashes
    things so here we are.

## Breakage
The DOH has been changing their page quite a bit so this will probably break frequently, :-/
