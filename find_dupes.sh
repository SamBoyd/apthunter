#!/usr/bin/env bash

SITES=( craigslist zoopla gumtree rightmove )

for site in ${SITES[@]}; do
	python build_image_descriptors.py $site
done

python find_dupes.py
