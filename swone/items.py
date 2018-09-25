# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader

def add_swone(value):
    return value+"-swone"

class SwoneItem(scrapy.Item):
    blog_title = scrapy.Field(
        # 预处理
        input_processor = MapCompose(add_swone),
        # 后处理
        output_processor = TakeFirst
    )
    # 如果所有的output操作都是TakeFirst 可以重写Itemloder。

class my_ItemLoader(ItemLoader):
    default_output_processor = TakeFirst
    # 这样爬虫中也不能继承原生的ItemLoader，需要继承这个loader

    # blog_date = scrapy.Field()
    # url = scrapy.Field()
    # url_object_id = scrapy.Field() #md5
    # front_image_url = scrapy.Field()
    # # front_image_path = scrapy.Field()  #本地路径
    # vote_up = scrapy.Field()
    # comment_num = scrapy.Field()
    # tags = scrapy.Field()
    # content = scrapy.Field()
    # blog_bookmark = scrapy.Field()

class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题 Item
    # 直接能从问题页面可以获取到的
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

class ZhihuAnswerItem(scrapy.Item):
    # 知乎的回答 Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    anthor_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()


