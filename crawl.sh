#!/usr/bin/env bash
SITES=( rightmove zoopla craigslist gumtree )

for site in ${SITES[@]}; do
	scrapy crawl $site -o $site.csv
done
