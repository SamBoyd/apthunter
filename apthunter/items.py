# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ApartmentItem(scrapy.Item):
    description = scrapy.Field()
    price_per_month = scrapy.Field()
    link = scrapy.Field()
    pictures = scrapy.Field()
    location = scrapy.Field()
