#!/usr/bin/python
#/*******************************************************************************
#
#  Script <yahooFinanceyahoo_old.py> 
#
#  Author: Andrew J. Stershic
#          Duke Computational Mechanics Lab (DCML)
#          Duke University - Durham, NC (USA)
#  E-mail: ajs84@duke.edu
#  Web:    www.duke.edu/~ajs84
#
#  Copyright (c) 2013 Andrew Stershic. All rights reserved. No warranty. No
#  liability.
#
#  *Please cite ALL use of code in academic works, presentations, and
#  publications, an example template of which is given by:
#  http://lrweb.beds.ac.uk/guides/ref/cite_computer_program
#
#*******************************************************************************/
import time
import csv
import urllib
import os

#define subfunctions
def parse(page,phrase):
	#find phrase
	loc = page.find(phrase)
	loc_end = page.find('<',loc+len(phrase))
	raw = page[loc+len(phrase):loc_end]

	if (loc == -1):
		print 'Phrase not found!'
		return '0'

	#check for &nbsp
	amp_loc = raw.find('&nbsp')
	if (amp_loc != -1):
		raw = raw[0:amp_loc]

	#check for &amp;
	amp_loc = raw.find('&amp;')
	if (amp_loc != -1):
		raw = raw.replace('&amp;','&')

	#check for null
	if (raw.find('-') != -1):
		yahoo_loc = raw.find('Stock - Yahoo!')
		if (yahoo_loc != -1):
			final = raw[0:yahoo_loc]
			common_loc = final.find(' Common')
			if (common_loc != -1):
				final = final[0:common_loc]
			return final
		else:
			return '0'

	#check for negative
	final = raw
	if (raw.startswith('(') and raw.endswith(')')):
		final = '-' + raw[1:len(raw)-1]
	return final

def make_number(phrase):
	out = phrase
	#check for zero
	if (phrase == '0K'):
		return '0'
	#convert suffix to scientific notation
	if (phrase.endswith('B')):
		out = phrase[0:len(phrase)-1] + 'e9'
		if (len(out) == 2):
			out = 0
	if (phrase.endswith('M')):
		out = phrase[0:len(phrase)-1] + 'e6'
		if (len(out) == 2):
			out = 0
	if (phrase.endswith('K')):
		out = phrase[0:len(phrase)-1] + 'e3'
		if (len(out) == 2):
			out = 0
	out = removeComma(out)
	return out

def parseSymbol(inString):
	out = inString.replace('.','-')
	return out

def removeComma(inString):
	out = inString.replace(',','')
	return out

def main(file,out):
	#import list of symbols
	inReader = csv.reader(open(file, 'rb'), delimiter=' ', quotechar='"')
	outWriter = csv.writer(open(out, 'wb'), delimiter=';',quotechar='"', quoting=csv.QUOTE_MINIMAL)
	outWriter.writerow(['symbol', 'Price', '# Shares','Dividends Paid','Stock Sale/(Purchase)', '', 'Net Payout per Share','Dividend Yield','Shareholder Yield','Beta','Price/Book Ratio'])
	#outWriter.writerow(['symbol', 'Company Name', 'Price', '# Shares','Dividends Paid','Stock Sale/(Purchase)', '', 'Net Payout per Share','Dividend Yield','Shareholder Yield','Beta','Price/Book Ratio'])

	#---begin loop
	for row in inReader:
		time.sleep(0.)
		if not row[0]:
			break

		symbol = row[0]

		urlSymbol = parseSymbol(symbol)

		print symbol
		#mix symbol name into string

		cash_flow = urllib.urlopen("http://finance.yahoo.com/q/cf?s=" + urlSymbol + "&annual")
		summary = urllib.urlopen("http://finance.yahoo.com/q/ks?s=" + urlSymbol + "+Key+Statistics")
		cf = cash_flow.read()
		cash_flow.close()
		s = summary.read()
		summary.close()

		#grab data from page

		#name
		name = parse(s, '<title>'+urlSymbol+' Key Statistics | ')
		print name

		#price
		price = parse(s, '<span id="yfs_l84_'+urlSymbol.lower()+'">')
		price_out = make_number(price)
		print price_out

		#shares outstanding
		num_shares = parse(s, 'Shares Outstanding<font size="-1"><sup>5</sup></font>:</td><td class="yfnc_tabledata1">')
		num_shares_out = make_number(num_shares)
		print num_shares_out

		#dividends paid
		div_value = parse(cf, 'Dividends Paid</td><td align="right">')
		div_value_out = make_number(div_value+'K')
		print div_value_out

		#issuance/retirement of shares
		iss_value = parse(cf, 'Sale Purchase of Stock</td><td align="right">')
		iss_value_out = make_number(iss_value+'K')
		print iss_value_out

		#beta
                beta = parse(s, 'Beta:</td><td class="yfnc_tabledata1">')
                beta_out = make_number(beta)
		print beta_out

		#price-book ratio
		pbr = parse(s, 'Price/Book (mrq):</td><td class="yfnc_tabledata1">')
		pbr_out = make_number(pbr)
		print pbr_out

		#skip if not found
		if num_shares_out is '0':
			print "Skipped"
			continue
		if price_out is '0':
			print "Skipped"
			continue

		#calculate
		net_payout = -float(div_value_out)-float(iss_value_out)
		net_payout_per_share = net_payout/float(num_shares_out)
		dividend_yield = -float(div_value_out)/(float(price_out)*float(num_shares_out))
		shareholder_yield = net_payout_per_share/float(price_out)
		print str(net_payout)
		print str(net_payout_per_share)
		print str(dividend_yield)
		print str(shareholder_yield)

		#save to .csv
		#outWriter.writerow([symbol, name, price, num_shares_out, div_value_out, iss_value_out, '', net_payout_per_share, dividend_yield, shareholder_yield,beta_out,pbr_out])
		outWriter.writerow([symbol, price, num_shares_out, div_value_out, iss_value_out, '', net_payout_per_share, dividend_yield, shareholder_yield,beta_out,pbr_out])

	#---end loop

main('list.csv','out.csv')
