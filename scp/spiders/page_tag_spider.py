import scrapy
from scp.items import LinkSet

DOMAIN = "https://scp-wiki.wikidot.com"
TAG_PREFIX = f"{DOMAIN}/system:page-tags/tag/"

# Token from scp_crawler
MAIN_TOKEN = "123456"

# These 4 tags cover just about every page that I want to consider
TAG_TYPES = ["scp", "tale", "hub", "goi-format"]


def get_page_id(url: str):
    return scrapy.FormRequest()

def get_rating_request(page_id: str):
    return scrapy.FormRequest(
        url = "https://scp-wiki.wikidot.com/ajax-module-connector.php",
        method = "POST",
        body = {
            "wikidot_token7": MAIN_TOKEN,
            "page_id": page_id,
            "moduleName": "pagerate/WhoRatedPageModule",
        },
        cookies = {
            "wikidot_token7": MAIN_TOKEN
        }
    )

def get_page_rating(url: str):
    # First, get the id of the page
    pass

# Used to get a list of articles on the SCP wiki
class PageTagsSpider(scrapy.Spider):
    name = "page-tags"
    allowed_domains = ["scp-wiki.wikidot.com"]

    start_urls = [TAG_PREFIX + suffix for suffix in TAG_TYPES]

    custom_settings = {
        "FEEDS":{
            './output/links.csv': {"format": "csv", "overwrite":True}
        }
    }


    def parse(self, response):
        self.logger.info("Parse function called on %s", response.url)
        linkList = []
        titleList = []

        # There must be a way to do this with only typing this path once in the Xpath but idk
        PAGE_LIST_ITEM_XPATH = "//div[@class='pages-list-item']/div/a"

        # That zip statement splits it into groups of 2, which allows for link and title to be consumed at once
        for link, title in zip(*(iter(response.xpath(f"{PAGE_LIST_ITEM_XPATH}/@href|{PAGE_LIST_ITEM_XPATH}/text()").getall()),) * 2):
            # self.logger.info("Adding %s to list ", element)
            linkList.append(link)
            titleList.append(title)

            # yield get_page_rating(page_link)


        pages = LinkSet()
        pages["links"] = linkList
        pages["titles"] = titleList
        
        return pages

# Use to get the ratings of a specific page
class PageRatingSpider(scrapy.Spider):
    name = "page-history"
    allowed_domains = ["scp-wiki.wikidot.com"]

    def start_requests(self):
        return [
        ]
            

    def parse(self, response):
        self.logger.info("Parsing rating information for %s", response.url)
        return None
