import scrapy

class LinkSet(scrapy.Item):
    links = scrapy.Field()
    titles = scrapy.Field()

class Page(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    votemap = scrapy.Field()
    # If adapted include the below
    # tags = scrapy.Field()
    # author = scrapy.Field()
