import pandas as pd
import csv

header = ['image_url', 'page_url', 'descriptor']
sites = ['craigslist', 'gumtree', 'rightmove', 'zoopla']
image_descriptors = [pd.read_csv('image_descriptors_' + site + '.csv', header=None, names=header) for site in sites]

data = pd.DataFrame()
for d in image_descriptors:
    data = data.append(d, ignore_index=True)
    
data = data.drop_duplicates('image_url')
data = data.drop_duplicates(['descriptor', 'page_url'])

lower_level = []
for descriptor, group in data.groupby('descriptor'):
    lower_level.append(list(group['page_url']))

upper_level = []
finished = False

while not finished:
    finished = True
    for index, candidates in enumerate(lower_level):
        upper_level_entry = list(set(candidates))
        for targets in lower_level[index+1:]:
            if set(candidates).intersection(set(targets)):
                upper_level_entry += list(set(candidates).union(set(targets)))
                lower_level.remove(targets)
                finished = False
        upper_level.append(upper_level_entry)
    lower_level = upper_level
    upper_level = []

grouped_by_url = data.groupby('page_url')

with open('dupes.csv', 'wb') as outfile:
    writer = csv.writer(outfile)
    for dupe_list in lower_level:
        image_urls = sum([list(grouped_by_url.get_group(dupe_url)['image_url'].unique()) for dupe_url in dupe_list], [])
        writer.writerow([dupe_list, image_urls])

