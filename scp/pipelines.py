# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

from itemadapter.adapter import ItemAdapter

OUTPUT_PATH = "./output"

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open(f"{OUTPUT_PATH}/items.jsonl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item

class CSVWriterPipeline:
    def open_spider(self, spider):
        self.file = open(f"{OUTPUT_PATH}/items.jsonl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item
