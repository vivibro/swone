# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs #避免编码过程中繁杂工作
import json
from scrapy.exporters import JsonItemExporter


class JsonExporterPipelines(object):
    # 调用scrapy提供的json exporter  导出Json文件
    def __init__(self):
        self.file = open('article.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding='utf-8',ensure_ascii =False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        # 停止导出
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class SwonePipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    # 自定义Json文件的导出
    def __init__(self):
        # 初始化中打开json文件  以写的方式
        self.file = codecs.open('article.json','w',encoding='utf-8')
    def process_item(self, item, spider):
        # 处理item的关键地方
        # 参数2：编码有中文或者有其他编码会出错 所以要false
        lines = json.dumps(dict(item),ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item
    # 结束的之后自动调用此函数 关闭打开的文件
    def spider_closed(self,spider):
        self.file.close()

class SwoneImagePipeline(ImagesPipeline):
    #重载 获取文件实际下载地址的函数
    def item_completed(self, results, item, info):
        for ok,value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path
        return item  #切记要把item返回出去  因为下一个pipelines要处理这个item

        pass