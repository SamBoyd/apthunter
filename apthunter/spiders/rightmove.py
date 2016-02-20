# -*- coding: utf-8 -*-
import scrapy

from apthunter.items import ApartmentItem
from apthunter import config
import math


class RightmoveSpider(scrapy.Spider):
    name = 'rightmove'
    allowed_domains = ['rightmove.co.uk']
    start_urls = (
        'http://www.rightmove.co.uk/property-to-rent/find.html' + 
        '?searchType=RENT&locationIdentifier=' + config.RIGHTMOVE_POSTCODE + '&insId=1&radius=' + str(config.MAX_DISTANCE_MILES) +
        '&minPrice=' + str(config.MIN_PRICE_PER_WEEK) +
        '&maxPrice=' + str(config.Max_PRICE_PER_MONTH) +
        '&minBedrooms=' + str(config.NUM_BEDROOMS) +
        '&maxBedrooms=' + str(config.NUM_BEDROOMS) +
        '&displayPropertyType=&maxDaysSinceAdded=3&sortByPriceDescending=&_includeLetAgreed=on' +
        '&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=' +
        '&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare=false',
    )

    def parse_price_pcm(self, price_str):
            if price_str:
                return float(price_str[:-4].replace(',', ''))

    def get_text(self, raw_html_elem):
        return '\n'.join([l.strip() for l in raw_html_elem.xpath('.//text()').extract()])

    def parse(self, response):
        for listing in response.css('.summary-list-item'):
            item = ApartmentItem()
            item['link'] = response.urljoin(listing.css('.price-new > a::attr(href)').extract_first())
            item['price_per_month'] = self.parse_price_pcm(listing.css('.price-new > a').re_first(r'\d?,?\d+ pcm'))
            item['location'] = self.get_text(listing.css('.displayaddress strong'))
            request = scrapy.Request(response.urljoin(item['link']), callback=self.parse_details)
            request.meta['item'] = item
            yield request
        next_page_url = response.xpath('//li/span[@class="current"]/../following-sibling::li[1]/a/@href').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_details(self, response):
        item = response.meta['item']
        item['description'] = self.get_text(response.css('.description .agent-content div:nth-child(3)'))
        item['pictures'] = response.css('.js-gallery-thumbnail img::attr(src)').extract()
        if not 'share' in item['description']:
            yield item
