import csv
import sys
import urllib2
from multiprocessing import Pool

from skimage.io import imread
from skimage.transform import downscale_local_mean, resize
from skimage.feature import local_binary_pattern
from skimage.color import rgb2gray
import numpy as np

def process_line(t):
    i, row = t
    image_urls = row[0].split(',')
    for image_url in image_urls:
        if 'http' in image_url:
            try:
                image_data = imread(image_url)
                grayed = rgb2gray(image_data)
                image_resized = resize(grayed, (100, 100))
                descriptor = local_binary_pattern(image_resized, 3, 20, 'uniform')
                descriptor = downscale_local_mean(descriptor, (10, 10))
                descriptor_list = np.floor(descriptor.flatten()).tolist()
                return [image_url, row[2], descriptor_list]
            except:
                return [image_url, row[2], []]

if __name__ == '__main__':
    file_name = sys.argv[1].strip()
    p = Pool(25)
    with open(file_name + '.csv', 'rb') as csvfile:
        listing_reader = csv.reader(csvfile)
        total_lines = sum(1 for _ in listing_reader)
        csvfile.seek(0)
        listing_reader = csv.reader(csvfile)
        data = [(idx, row) for idx, row in enumerate(listing_reader)]
        rows = p.map(process_line, data)
        desc_file = 'image_descriptors_' + file_name + '.csv'
        with open(desc_file, 'wb') as outfile:
            descriptors_writer = csv.writer(outfile)
            for row in rows:
                if row is not None:
                    descriptors_writer.writerow(row)
