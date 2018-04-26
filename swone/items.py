# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SwoneItem(scrapy.Item):
    blog_title = scrapy.Field()
    blog_date = scrapy.Field()
    url = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()  #本地路径
    vote_up = scrapy.Field()
    comment_num = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    blog_bookmark = scrapy.Field()






    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

