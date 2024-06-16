BOT_NAME = "scp_recommender_scraper"

SPIDER_MODULES = ["scp.spiders"]
NEWSPIDER_MODULE = "scp.spiders"

# Run in debug by default
DEBUG_MODE = True

LOG_ENABLE = True
LOG_LEVEL = "DEBUG" if DEBUG_MODE else "INFO"
LOG_FILE = "./output/scrapy.log"

USER_AGENT = "MrShwhale (https://github.com/MrShwhale/scp-recommender)"

ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = CONCURRENT_REQUESTS

COOKIES_ENABLED = True

ITEM_PIPELINES = {
    "scp.pipelines.ItemWriter": 300,
}

EXTENSIONS = {
    "scrapy.extensions.closespider.CloseSpider": 300,
}

CLOSESPIDER_PAGECOUNT = 100 if DEBUG_MODE else 0

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
