# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter.adapter import ItemAdapter
from scp.items import User, Rating, Page
import json

OUTPUT_PATH = "./output"

class ItemWriter:
    def open_spider(self, spider):
        self.user_file = open(f"{OUTPUT_PATH}/users.csv", "w")
        self.page_file = open(f"{OUTPUT_PATH}/pages.csv", "w")
        self.ratings_file = open(f"{OUTPUT_PATH}/ratings.jsonl", "w")
        self.log_file = open(f"{OUTPUT_PATH}/log.txt", "w")

    def close_spider(self, spider):
        self.user_file.close()
        self.page_file.close()
        self.ratings_file.close()
        self.log_file.close()

    def process_item(self, item, spider):
        # Write to different files depending on what type of item this is
        item_dict = ItemAdapter(item).asdict()
        if isinstance(item, User):
            self.user_file.write(f"{item_dict['user_id']},{item_dict['name']},{item_dict['url']}\n")
        elif isinstance(item, Page):
            self.page_file.write(f"{item_dict['page_id']},{item_dict['title']},{item_dict['url']}\n")
        elif isinstance(item, Rating):
            self.ratings_file.write(f"{json.dumps(item_dict)}\n")
        else:
            self.log_file.write(f"Item not found:{type(item)}. Content: {item_dict}\n")
