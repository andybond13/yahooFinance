#from urllib2 import Request
import urllib2
#from urllib2 import Request
#import urllib
from bs4 import BeautifulSoup
import datetime
import dateutil.relativedelta as dr
import pandas as pd

import ssl
try:
   _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def get_constituents(index='SP500'):
    # URL request, URL opener, read content
    if (index == 'SP500'):
        table_idx = 0
        req = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    elif (index == 'DJIA'):
        table_idx = 1
        req = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'

    opener = urllib2.urlopen(req)
    content = opener.read().decode('unicode_escape') # Convert bytes to UTF-8

    soup = BeautifulSoup(content)
    tables = soup.find_all('table') # HTML table we actually need is tables[0] 

    external_class = tables[table_idx].findAll('a', {'class':'external text'})

    tickers = []

    for ext in external_class:
        if not 'reports' in ext:
            tickers.append(ext.string)

    return tickers

def write_to_file(filename,tickers):

    with open(filename,'w') as fopen:
        for ticker in tickers:
            fopen.write('{}\n'.format(ticker))

    return

#S&P500
#tickers = get_constituents(index='SP500')
#write_to_file('list_sp500.csv',tickers)
#print tickers
#Dow Jones
tickers = get_constituents(index='DJIA')
write_to_file('list_djia.csv',tickers)
print tickers

