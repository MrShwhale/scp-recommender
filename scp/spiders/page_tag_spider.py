import scrapy
import re
from scrapy.selector import Selector
from scp.items import Page, User, Rating

DOMAIN = "https://scp-wiki.wikidot.com"
TAG_PREFIX = f"{DOMAIN}/system:page-tags/tag/"

# Token from scp_crawler
MAIN_TOKEN = "123456"

# These 4 tags cover just about every page that I want to consider
TAG_TYPES = ["scp", "tale", "hub", "goi-format"]

# Used to get a list of articles on the SCP wiki
class PageTagsSpider(scrapy.Spider):
    name = "ratings"
    allowed_domains = ["scp-wiki.wikidot.com"]

    start_urls = [TAG_PREFIX + suffix for suffix in TAG_TYPES]

    # Use to store the ids of users which have been found already
    users = set()

    def parse(self, response):
        self.logger.info("Parsing tag page: %s", response.url)

        # There must be a way to do this with only typing this path once in the Xpath but idk
        PAGE_LIST_ITEM_XPATH = "//div[@class='pages-list-item']/div/a"

        # That zip statement splits it into groups of 2, which allows for link and title to be consumed at once
        for link, title in zip(*(iter(response.xpath(f"{PAGE_LIST_ITEM_XPATH}/@href|{PAGE_LIST_ITEM_XPATH}/text()").getall()),) * 2):
            # self.logger.info("Adding %s to list ", element)
            yield scrapy.FormRequest(
            url = f"https://scp-wiki.wikidot.com{link}",
            method = "GET",
            callback = self.parse_id,
            cb_kwargs = {"url": link, "title": title}
        )

    def parse_id(self, response, url, title):
        self.logger.info("Reading the info about %s", url)

        id_pattern = re.compile(r"WIKIREQUEST\.info\.pageId = (\d+);")

        id_pattern_match = id_pattern.search(response.text)
        if id_pattern_match is None:
            # Something bad happened
            self.logger.error("pageId not found!")
            return None
        else:
            page_id = id_pattern_match.group(1)

        if page_id is None:
            # Something bad happened
            self.logger.error("pageId match not found!")
            yield None
        
        # Take a short break to yield an Item here
        yield Page(page_id=page_id, title=title, url=url)
        
        # Now, make the rating request with that id information
        yield scrapy.FormRequest(
            url = "https://scp-wiki.wikidot.com/ajax-module-connector.php",
            method = "POST",
            formdata = {
                "pageId": page_id,
                "moduleName": "pagerate/WhoRatedPageModule",
                "wikidot_token7": MAIN_TOKEN
            },
            cookies = {
                "wikidot_token7": MAIN_TOKEN
            },
            callback = self.parse_rating,
            cb_kwargs = {"page_id":page_id}
        )

    def parse_rating(self, response, page_id):
        self.logger.info("Parsing the rating of pageId %s (%s)", page_id, response.url)
        body = response.json()["body"]
        information = Selector(text=body).xpath("//a[not(img)] | //span[@style='color:#777']/text()").getall()

        url_pattern = re.compile("http://www\\.wikidot\\.com/user:info/(.+?)\"")
        uid_pattern = re.compile(r"userInfo\((\d+)\)")
        uname_pattern = re.compile(r">(.+)</a>")
        rating_pattern = re.compile(r"^\s+(\+|-)\s+$")

        for user_raw, rating in zip(*(iter(information),) * 2):
            name_match = uname_pattern.search(user_raw)
            if name_match is None:
                # If the raw is a rating, then this should be a deleted user
                if rating_pattern.fullmatch(user_raw):
                    break

                self.logger.error("Couldn't find a name in <%s>\n", user_raw)
                from scrapy.shell import inspect_response
                inspect_response(response, self)
                continue
            else:
                name = name_match.group(1)

            url_match = url_pattern.search(user_raw)
            if url_match is None:
                self.logger.error("Couldn't find a url in <%s>\n", user_raw)
                continue
            else:
                user_url = url_match.group(1)

            uid_match = uid_pattern.search(user_raw)
            if uid_match is None:
                self.logger.error("Couldn't find an id in <%s>\n", user_raw)
                continue
            else:
                user_id = uid_match.group(1)

            rating = rating.strip()
            if user_id not in self.users:
                self.logger.info("New user with id %s and name %s", user_id, name)
                yield User(user_id=user_id, name=name, url=user_url)

            rating_val = 1 if rating == "+" else -1

            self.logger.info("User %s gave page %s rating %s", name, page_id, rating_val)
            yield Rating(user_id=user_id, page_id=page_id, rating=rating_val)
