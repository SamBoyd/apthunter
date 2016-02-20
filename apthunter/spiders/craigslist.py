# -*- coding: utf-8 -*-
import scrapy

from apthunter.items import ApartmentItem
from apthunter import config

class CraigslistSpider(scrapy.Spider):
    name = 'craigslist'
    allowed_domains = ['craigslist.co.uk']
    start_urls = (
        'http://london.craigslist.co.uk/search/apa?max_price=' + str(config.MAX_PRICE_PER_WEEK)
            + '&bedrooms=' + str(config.NUM_BEDROOMS),
    )
    
    def parse_price_pcm(self, price_str):
        if price_str:
            return float(price_str[1:].replace(',', '')) * 4.3

    def get_text(self, raw_html_elem):
        return '\n'.join([l.strip() for l in raw_html_elem.xpath('.//text()').extract()])

    def parse(self, response):
        for listing in response.css('.content p.row'):
            item = ApartmentItem()
            item['link'] = response.urljoin(listing.css('span.pl a::attr(href)').extract_first())
            item['price_per_month'] = self.parse_price_pcm(self.get_text(listing.css('.l2 .price')))
            item['location'] = self.get_text(listing.css('.pnr small'))
            request = scrapy.Request(response.urljoin(item['link']), callback=self.parse_details)
            request.meta['item'] = item
            yield request
        next_page_url = response.css('a.button.next::attr(href)').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_details(self, response):
        item = response.meta['item']
        item['description'] = self.get_text(response.css('section#postingbody'))
        item['pictures'] = response.css('#thumbs a::attr(href)').extract()
        if not 'share' in item['description']:
            yield item
