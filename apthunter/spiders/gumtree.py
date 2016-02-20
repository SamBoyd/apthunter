# -*- coding: utf-8 -*-
import scrapy

from apthunter.items import ApartmentItem
from apthunter import config

class GumtreeSpider(scrapy.Spider):
    name = 'gumtree'
    allowed_domains = ['gumtree.com', 'gumtree.co.uk']
    start_urls = (
        'https://www.gumtree.com/search?sort=date&page=1&distance=' + str(config.MAX_DISTANCE_MILES)
            + '&guess_search_category=flats-and-houses-for-rent-offered&q=&search_category=flats-and-houses-for-rent-offered'
            +' &search_location=' + config.SEARCH_LOCATION
        + '&seller_type='
        + '&max_price=' + str(config.MAX_PRICE_PER_WEEK)
        + '&min_price=' + str(config.MIN_PRICE_PER_WEEK)
        + '&min_property_number_beds' + str(config.NUM_BEDROOMS)
        + '&max_property_number_beds' + str(config.NUM_BEDROOMS),
    )

    def parse_price_pcm(self, price_str):
        if price_str:
            if 'pw' in price_str:
                return float(price_str[1:-2].replace(',', '')) * 4.3
            else:
                return float(price_str[1:-2].replace(',', ''))

    def get_text(self, raw_html_elem):
        return '\n'.join([l.strip() for l in raw_html_elem.xpath('.//text()').extract()])

    def parse(self, response):
        for listing in response.css('article.listing-maxi'):
            item = ApartmentItem()
            item['link'] = response.urljoin(listing.css('a.listing-link::attr(href)').extract_first())
            item['price_per_month'] = self.parse_price_pcm(self.get_text(listing.css('.listing-price')))
            item['location'] = self.get_text(listing.css('.listing-location span'))
            request = scrapy.Request(response.urljoin(item['link']), callback=self.parse_details)
            request.meta['item'] = item
            yield request
        next_page_url = response.xpath('//li[@class="next"]/a/@href').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_details(self, response):
        item = response.meta['item']
        item['description'] = self.get_text(response.css('p.ad-description'))
        item['pictures'] = response.css('#vip-tabs-images li img::attr(src)').extract()
        if not 'share' in item['description']:
            yield item

