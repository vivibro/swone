# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline

class SwonePipeline(object):
    def process_item(self, item, spider):
        return item

class SwoneImagePipeline(ImagesPipeline):
    #重载 获取文件实际下载地址的函数
    def item_completed(self, results, item, info):
        for ok,value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path
        return item  #切记要把item返回出去  因为下一个pipelines要处理这个item

        pass