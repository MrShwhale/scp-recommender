# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from itemadapter.adapter import ItemAdapter
from scp.items import User, Rating, Page

OUTPUT_PATH = "./output"

def csvify(*things):
    string = "\n"
    for thing in things:
        string += f"\"{str(thing)}\","

    return string[:-1]

class ItemWriter:
    def open_spider(self, spider):
        # Open the files
        self.user_file = open(f"{OUTPUT_PATH}/users.csv", "w")
        self.page_file = open(f"{OUTPUT_PATH}/pages.csv", "w")
        self.ratings_file = open(f"{OUTPUT_PATH}/ratings.csv", "w")
        self.log_file = open(f"{OUTPUT_PATH}/log.txt", "w")

        # Add the headers
        self.user_file.write("userId,userName,url")
        self.page_file.write("pageId,title,url")
        self.ratings_file.write("userId,pageId,rating")

    def close_spider(self, spider):
        self.user_file.close()
        self.page_file.close()
        self.ratings_file.close()
        self.log_file.close()

    def process_item(self, item, spider):
        # Write to different files depending on what type of item this is
        item_dict = ItemAdapter(item).asdict()
        if isinstance(item, User):
            self.user_file.write(csvify(item_dict['user_id'], item_dict['name'].replace('\"', '\"\"'), item_dict['url']))
        elif isinstance(item, Page):
            self.page_file.write(csvify(item_dict['page_id'], item_dict['title'].replace('\"', '\"\"'), item_dict['url']))
        elif isinstance(item, Rating):
            self.ratings_file.write(csvify(item_dict['user_id'], item_dict['page_id'], item_dict['rating']))
        else:
            self.log_file.write(f"Item not found:{type(item)}. Content: {item_dict}\n")
