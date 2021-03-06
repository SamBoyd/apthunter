# -*- coding: utf-8 -*-
import scrapy
import re
import math

from apthunter.items import ApartmentItem
from apthunter import config


class ZooplaSpider(scrapy.Spider):
    FLOAT_REGEX = re.compile(r'\d+.\d+')
    name = 'zoopla'
    allowed_domains = ['zoopla.co.uk']

# http://www.zoopla.co.uk/to-rent/property/3-bedrooms/oxford-circus/?duration=900&include_shared_accommodation=true
    # &price_frequency=per_month&price_max=2250&price_min=1750&q=Oxford%20Circus%2C%20London
    # &results_sort=newest_listings&search_source=refine&transport_type=walking_train

    start_urls = (
        'http://www.zoopla.co.uk/to-rent/property/3-bedrooms/' + config.ZOOPLA_LOCATION +
        '?duration=' + str(config.MAX_TRAVEL_TIME_SECONDS) +
        '&price_frequency=per_month' +
        '&price_max=' + str(config.Max_PRICE_PER_MONTH) +
        '&price_min=' + str(config.MIN_PRICE_PER_MONTH) +
        '&q=' + config.SEARCH_LOCATION +
        '&results_sort=newest_listings' +
        '&search_source=travel-time&transport_type=walking_train',
    )

    def parse_price_pcm(self, price_str):
        price = self.FLOAT_REGEX.search(price_str)
        return float(price.group(0).replace(',', '')) if price else 0

    def get_text(self, raw_html_elem):
        text = raw_html_elem.xpath('text()').extract_first()
        return text.strip() if text else ''

    def parse(self, response):
        for listing in response.css('.listing-results-right'):
            item = ApartmentItem()
            item['link'] = response.urljoin(listing.css('a.listing-results-price::attr(href)').extract_first())
            item['price_per_month'] = self.parse_price_pcm(self.get_text(listing.css('a.listing-results-price')))
            item['location'] = self.get_text(listing.css('a.listing-results-address'))
            request = scrapy.Request(response.urljoin(item['link']), callback=self.parse_details)
            request.meta['item'] = item
            yield request
        next_page_url = response.css('.current + a::attr(href)').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_details(self, response):
        item = response.meta['item']
        item['description'] = self.get_text(response.css('div[itemprop=description]'))
        item['pictures'] = response.css('img[itemprop=contentUrl]::attr(src)').extract()
        yield item
