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

ID_PATTERN = re.compile(r"WIKIREQUEST\.info\.pageId = (\d+);")
URL_PATTERN = re.compile("http://www\\.wikidot\\.com/user:info/(.+?)\"")
UID_PATTERN = re.compile(r"userInfo\((\d+)\)")
UNAME_PATTERN = re.compile(r">(.+)</a>")
RATING_PATTERN = re.compile(r"^\s+(\+|-)\s+$")
PAGE_LIST_ITEM_XPATH = "//div[@class='pages-list-item']/div/a"

# Used to get a list of articles on the SCP wiki
class PageTagsSpider(scrapy.Spider):
    name = "ratings"
    allowed_domains = ["scp-wiki.wikidot.com"]

    # Use to store the ids of users which have been found already
    users = set()

    def start_requests(self):
        return [
                scrapy.FormRequest( url = tag_page, method = "GET", callback=self.parse_tag_page) 
                for tag_page in [TAG_PREFIX + suffix for suffix in TAG_TYPES]
                ]

    # Parsing starts here
    def parse_tag_page(self, response):
        self.logger.info("Parsing tag page: %s", response.url)

        # TODO if you ever feel up to it, refactor this whole function. It's awful
        # Get a list of the links and page titles (with links preceeding the title of the page)
        parsed_response = response.xpath(f"{PAGE_LIST_ITEM_XPATH}/@href|{PAGE_LIST_ITEM_XPATH}/text()").getall()

        # This zip statement takes 2 elements of parsed_response at a time, which allows for link and title to be consumed at once
        for link, title in zip(*(iter(parsed_response),) * 2):
            yield scrapy.FormRequest(
            url = f"https://scp-wiki.wikidot.com{link}",
            method = "GET",
            callback = self.parse_id,
            cb_kwargs = {"url": link, "title": title}
        )

    # Called on each page found on a tag page
    def parse_id(self, response, url, title):
        self.logger.info("Reading the info about %s", url)

        id_pattern_match = ID_PATTERN.search(response.text)
        if id_pattern_match is None:
            # Something bad happened
            self.logger.error("pageId not found!")
            return None
        else:
            page_id = id_pattern_match.group(1)

        if page_id is None:
            # Something bad happened
            self.logger.error("pageId match not found!")
            return None
        
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

    # Also called for each page called on a tag page, after parse_id
    def parse_rating(self, response, page_id):
        self.logger.info("Parsing the rating of pageId %s (%s)", page_id, response.url)
        body = response.json()["body"]
        information = Selector(text=body).xpath("//a[not(img)] | //span[@style='color:#777']/text()").getall()

        for user_raw, rating in zip(*(iter(information),) * 2):
            # Check for a user name
            name_match = UNAME_PATTERN.search(user_raw)
            if name_match is None:
                # If the raw is a rating, then this should be a deleted user
                if RATING_PATTERN.fullmatch(user_raw):
                    break

                self.logger.error("Couldn't find a name in <%s>\n", user_raw)
                from scrapy.shell import inspect_response
                inspect_response(response, self)
                continue
            else:
                name = name_match.group(1)

            # Check for a user URL
            url_match = URL_PATTERN.search(user_raw)
            if url_match is None:
                self.logger.error("Couldn't find a url in <%s>\n", user_raw)
                continue
            else:
                user_url = url_match.group(1)

            # Check for a user id
            uid_match = UID_PATTERN.search(user_raw)
            if uid_match is None:
                self.logger.error("Couldn't find an id in <%s>\n", user_raw)
                continue
            else:
                user_id = uid_match.group(1)

            # If the user id has not seen before, add it in
            if user_id not in self.users:
                self.logger.info("New user with id %s and name %s", user_id, name)
                self.users.add(user_id)
                yield User(user_id=user_id, name=name, url=user_url)

            # Convert from rating string to rating value
            rating = rating.strip()
            rating_val = 1 if rating == "+" else -1

            self.logger.info("User %s gave page %s rating %s", name, page_id, rating_val)
            yield Rating(user_id=user_id, page_id=page_id, rating=rating_val)
