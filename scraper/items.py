# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class JobItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    salary = scrapy.Field()
    additional_meta = scrapy.Field()
    posted_date = scrapy.Field()
    application_url = scrapy.Field()
