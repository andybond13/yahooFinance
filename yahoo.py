#!python

#/*******************************************************************************
#
#  Script <yahooFinance/yahoo.py> 
#
#  Author: Andrew J. Stershic
#  E-mail: astershic@gmail.com
#  Web:    www.linkedin.com/in/andrew-stershic-phd-pe 
#
#  Copyright (c) 2020 Andrew Stershic. All rights reserved. No warranty. No
#  liability.
#
#  Much thanks to: Ran Aroussi (aroussi.com), Rodrigo Bercini Martins (https://github.com/rodrigobercini)
#      using https://github.com/ranaroussi/yfinance/
#      due to https://github.com/ranaroussi/yfinance/issues/283,
#          using fork https://github.com/rodrigobercini/yfinance
#
#  *Please cite ALL use of code in academic works, presentations, and
#  publications, an example template of which is given by:
#  http://lrweb.beds.ac.uk/guides/ref/cite_computer_program
#
#*******************************************************************************/

import ssl
try:
   _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

import yfinance as yf
import csv
import xlwt

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)

#    for item in ticker.info:
#        print item, ticker.info[item]

    data = {}

    try:
        ticker.info
    except:
        return None

    data['name'] = ticker.info['shortName'] 
    data['price'] = ticker.info['regularMarketPrice']
    data['beta'] = ticker.info['beta']

    if 'priceToBook' in ticker.info.keys():
        data['price_book_ratio'] = ticker.info['priceToBook'] 
    else:
        data['price_book_ratio'] = float("NaN")

    marketCap = ticker.info['marketCap']
    data['market_cap'] = marketCap 

    qtr = ticker.quarterly_cashflow
    qtr = qtr.fillna(0)

    dates = qtr.columns.values
    if qtr.index.str.contains('Dividends').any():
        div = -(qtr[dates[0]]['Dividends Paid'] + qtr[dates[1]]['Dividends Paid'] + qtr[dates[2]]['Dividends Paid'] + qtr[dates[3]]['Dividends Paid'])
    else:
        div = 0 
    divYield = div / marketCap

    if qtr.index.str.contains('Repurchase').any():
        repurchase = -(qtr[dates[0]]['Repurchase Of Stock'] + qtr[dates[1]]['Repurchase Of Stock'] + qtr[dates[2]]['Repurchase Of Stock'] + qtr[dates[3]]['Repurchase Of Stock'])
    else:
        repurchase = 0

    if qtr.index.str.contains('Issuance').any():
        issuance = qtr[dates[0]]['Issuance Of Stock'] + qtr[dates[1]]['Issuance Of Stock'] + qtr[dates[2]]['Issuance Of Stock'] + qtr[dates[3]]['Issuance Of Stock']
    else:
        issuance = 0

    repurchase = repurchase - issuance
    repurchaseYield = repurchase / marketCap
    shareholderYield = divYield + repurchaseYield 

    data['dividends_paid'] = div 
    data['share_repurchase'] = repurchase
    data['dividend_yield'] = divYield
    data['repurchase_yield'] = repurchaseYield 
    data['shareholder_yield'] = shareholderYield

    return data

def parse_symbol(inString):
	out = inString.replace('.','-')
	return out

def get_symbols(file):

    inReader = csv.reader(open(file, 'rb'), delimiter=' ', quotechar='"')
    symbols = []

    for row in inReader:
#        time.sleep(0.)
        if not row[0]:
            break

        symbol = row[0]
        urlSymbol = parse_symbol(symbol)
        symbols.append(urlSymbol)

    return symbols

def main(file,out):

    book = xlwt.Workbook()
    sheet1 = book.add_sheet("Sheet 1")

    row = sheet1.row(0)
    cols = ['Symbol', 'Company Name', 'Price', 'Market Cap', \
        'Dividends Paid','Share Repurchase','Dividend Yield','Repurchase Yield', \
        'Shareholder Yield','Beta','Price/Book Ratio']
    for index, col in enumerate(cols):
        row.write(index, col)

    #import list of symbols
    symbols = get_symbols(file)

    #import data for each symbol
    for i in range(0, len(symbols)):

        symbol = symbols[i]
        print symbol
        this_data = get_stock_data(symbol)

        #check validity
        if this_data == None:
            continue

        row = sheet1.row(i+1)
        row_data = [symbol, this_data['name'], this_data['price'], this_data['market_cap'], \
            this_data['dividends_paid'], this_data['share_repurchase'], this_data['dividend_yield'], this_data['repurchase_yield'], \
            this_data['shareholder_yield'], this_data['beta'], this_data['price_book_ratio']]

        for index, datum in enumerate(row_data):
            row.write(index, datum)

    book.save(out)

main('list.csv','out.xls')
