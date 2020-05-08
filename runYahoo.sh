#!bash

#generate list of stocks
python getlist.py
cp list_djia.csv list.csv
cat list_sp500.csv >> list.csv

#run analysis
python yahoo.py
