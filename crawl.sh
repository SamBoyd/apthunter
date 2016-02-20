#!/usr/bin/env bash
SITES=(craigslist zoopla rightmove gumtree)

for site in ${SITES[@]}; do
	scrapy crawl $site -o $site.csv
done