import pandas as pd
import csv
import ast
import urllib
import json

import requests
from progressbar import ProgressBar

print "THIS IS VERY SLOW, BUT YOU CAN START VISUALISING THE RESULTS IN THE MEANTIME... PAY FOR THE GEOCODING API IF YOU WANT IT TO BE FASTER :P"
dupe_file = pd.read_csv('dupes.csv')
header = ['pictures', 'price_per_month', 'link', 'description', 'location']
dupe_file = pd.read_csv('dupes.csv')

data = pd.DataFrame()

sites = ['craigslist', 'gumtree', 'rightmove', 'zoopla']
for site in sites:
    data = data.append(pd.read_csv(site + '.csv', header=None, names=header), ignore_index=True)

grouped_by_url = data.groupby('link')

def get_coordinate(location):
    address_url = 'http://api.opencagedata.com/geocode/v1/json?' + urllib.urlencode({'key': '1e78cfcaae5460eff7aa61d0ea849958', 'query': location})
    try :
        response = requests.get(address_url).json()
    except (ValueError, requests.exceptions.ConnectionError):
        return None
    if response and u'results' in response.keys() and response[u'results']:
        result = response[u'results'][0][u'geometry']
        return str(result[u'lat']) + ', ' + str(result[u'lng'])

def filter_nan(l):
    return [a for a in l if str(a).lower() != 'nan']

with open('site/app/assets/data.txt', 'wb') as outfile:
    with ProgressBar(len(dupe_file)) as progress:
        for idx, row in dupe_file.iterrows():
            new_row = {}
            new_row['page_urls'] = row[0] #page_urls
            new_row['pic_urls'] = filter_nan(ast.literal_eval(row[1])) #pic urls
            descriptions = []
            prices = []
            locations = []
            coordinates = []
            for page_url in ast.literal_eval(row[0]):
                descriptions += list(grouped_by_url.get_group(page_url)['description'])
                prices += list(grouped_by_url.get_group(page_url)['price_per_month'])
                locations += list(grouped_by_url.get_group(page_url)['location'])
                coordinates += [get_coordinate(l) for l in locations if get_coordinate(l) is not None]
            new_row['descriptions'] = filter_nan(descriptions)
            new_row['locations'] = filter_nan(locations)
            new_row['coordinates'] = filter_nan(coordinates)
            new_row['prices'] = filter_nan(prices)
            outfile.write(json.dumps(new_row) + '\n')
            progress.update(idx)