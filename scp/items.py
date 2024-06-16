import scrapy

class User(scrapy.Item):
    user_id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()

class Page(scrapy.Item):
    page_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    # If adapted include the below
    # tags = scrapy.Field()
    # author = scrapy.Field()

class Rating(scrapy.Item):
    user_id = scrapy.Field()
    page_id = scrapy.Field()
    rating = scrapy.Field()
