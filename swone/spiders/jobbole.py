# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from swone.items import SwoneItem

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1.获取文章列表页中的文章url并交给scrypy下载后并进行解析
        2.获取下一页的url，下载完成后交给parse
        :param response:
        :return:
        '''
        # post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        # url如果不是一个完整的地址 需要拼接当前网页的话 需要response.url + post_url
        # parse.join(response.url,post_url)
        # 改写1，不获取网址 仅获取该node
        post_nodes = response.css("#archive .post .post-thumb a")

        # for post_url in post_urls:
        #     yield Request(url = parse.urljoin(response.url,post_url),meta = {"front_image_url"},callback = self.parse_detail)
        # 改写 1
        for post_node in post_nodes:
        # 二次提取其中的image和url
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url = parse.urljoin(response.url,post_url),meta = {"front_image_url":image_url},callback = self.parse_detail)


        # 提取下一页给scrapy下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first()

        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)

    def parse_detail(self,response):
        #提取文章的具体字段

        #实例化items
        swone_items = SwoneItem()

        # 通过css选择器提取字段
        # 标题
        # class为entry-header的节点       类选择器::    提取
        blog_title = response.css(".entry-header h1::text").extract()[0]
        # 日期
        blog_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].replace("·","").strip()
        # 点赞
        vote_up = response.css("span.vote-post-up  h10::text").extract()[0]
        # 封面图url
        front_image_url = response.meta.get("front_image_url","")
        # 字典查询方法get不会抛出异常 参数1：key  参数2：默认值

        # 收藏
        # blog_bookmark = re.match(".*?(\d+).*",response.css("span.bookmark-btn::text").extract()[0]).group(1)
        # 需要考虑无法匹配到数字的情况，需要有一个默认值0
        blog_bookmark = response.css("span.bookmark-btn::text").extract()[0]
        match_bb = re.match(".*?(\d+).*",blog_bookmark)
        if match_bb:
            blog_bookmark = int(match_bb.group(1))
        else:
            blog_bookmark = 0
        #评论
        # comment = re.match(".*?(\d+).*", response.css("a[href='#article-comment'] span::text").extract()[0]).group(1)
        comment_num = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_cn = re.match(".*?(\d+).*",comment_num)
        if match_cn:
            comment_num = int(match_cn.group(1))
        else:
            comment_num = 0


        # 正文
        content = response.css('div.entry').extract()[0]
        #标签
        tags = response.css('.entry-meta-hide-on-mobile a::text').extract()
        tags = [element for element in tags if not element.strip().endswith("评论")]
        #                                                             endwith("评论"）
        tags = ",".join(tags)


        # 赋值到实例变量
        swone_items["blog_title"] = blog_title
        swone_items["blog_date"] = blog_date
        swone_items["url"] = response.url
        swone_items["front_image_url"] = [front_image_url]
        swone_items["vote_up"] = vote_up
        swone_items["comment_num"] = comment_num
        swone_items["tags"] = tags
        swone_items["content"] = content
        swone_items["blog_bookmark"] = blog_bookmark

        # 传递到pipelines中去
        yield swone_items






        # xpath
        # # 标题
        # blog_title = response.xpath('//*[@id="post-113793"]/div[1]/h1/text()').extract()[0]
        # # 日期
        # blog_date = response.xpath('//*[@id="post-113793"]/div[2]/p/text()').extract()[0].replace("·","").strip()
        # # 收藏
        # blog_bookmark = re.match(".*?(\d+).*",response.xpath('//span[contains(@class , "bookmark-btn")]/text()').extract()[0]).group(1)
        # # 评论
        # href_style = re.match(".*?(\d+).*",response.xpath('//*[@id="post-113793"]/div[3]/div[12]/a/span/text()').extract()[0]).group(1)
        # # 正文
        # content = response.xpath('//*[@id="post-113793"]/div[3]/').extract()[0]
        # # 标签
        # tag_list = response.xpath('//*[@id="post-113793"]/div[2]/p/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # #                                                             endwith("评论"）
        # tag_list = ",".join(tag_list)

