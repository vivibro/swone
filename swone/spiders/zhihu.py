# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime

# 处理不完整域名 引入parse  兼容python2
try:
    import urlparse as parse
except:
    from urllib import parse

from scrapy.loader import ItemLoader

from swone.items import  ZhihuQuestionItem,ZhihuAnswerItem

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers = {
        'HOST':"https://www.zhihu.com",
        'Referer':"https://www.zhihu.com",
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.168 Safari/537.36'
    }
    # 查看 更多回答 的逻辑入口
    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&sort_by=default"

    def parse(self, response):
        '''
        提取出html页面中所有的url，并跟踪这些url进行下一步爬取
        如果提取的url中格式为/question/xxx ,就下载之后进入解析函数
        '''
        # 提取所有a::attr(href)下面的信息进入all_url
        all_url = response.css("a::attr(href)").extract()
        # 因为知乎的网址不完整 需要引入parse方法补全网址
        all_url = [parse.urljoin(response.url,url) for url in all_url]
        # 过滤url中有效的url
        all_url = filter(lambda x:True if x.startswith("https")else False,all_url)
        # 提取question的url
        for url in all_url:
            # 正则需要匹配两种模式，带answer以及直接id结尾的
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*",url)
            if match_obj:
                # 如果提取到question相关页面就yield出去交给下载器来进行提取处理
                # url以及id
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                # 目标url 通过yield一个scrapy对象
                yield scrapy.Request(request_url,headers=self.headers,callback=self.parse_question)
            else:
                # 如果不是question页面就继续进一步跟踪
                yield scrapy.Request(url,headers=self.headers,callback=self.parse)
            # 这一段逻辑同样可以复制在parse_question里面去,question里面一样有很多url


    def parse_question(self,response):
        # 处理question页面，从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:
            # 处理新版本页面
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                # url以及id
                question_id = int(match_obj.group(2))

            itme_loader = ItemLoader(item=ZhihuQuestionItem(),response=response)

            itme_loader.add_css("title","h1.QuestionHeader-title::text")
            itme_loader.add_css("content",".QuestionHeader-detail")
            itme_loader.add_value("url",response.url)
            itme_loader.add_value("zhihu_id",question_id)
            itme_loader.add_css("answer_num",".List-headerText span::text")
            itme_loader.add_css("comments_num",".QuestionHeader-Comment button::text")
            itme_loader.add_css("watch_user_num",".NumberBoard-itemValue::text")
            # .表示晚代取找所有符合要求的 >表示仅找儿子代
            itme_loader.add_css("topics",".QuestionHeader-topics .Popover::text")
            # itme_loader.add_css("topics", ".TopicLink Popover::text") 方法二

            question_item = itme_loader.load_item()

        else:
            # 处理老版本页面
            if "QuestionHeader-title" in response.text:
                # 处理新版本页面
                match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
                if match_obj:
                    # url以及id
                    question_id = int(match_obj.group(2))


                itme_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
                itme_loader.add_value("url", response.url)
                itme_loader.add_value("zhihu_id", question_id)
                # todo
        # 去请求answer，用预设好的入口开始,通过format处理填写正确的起始页面
        yield scrapy.Request(self.start_answer_url.format(question_id,5,0),headers=self.headers,callback=parse_answer)
        # 交给pipeline
        yield question_item


    def parse_answer(self,response):
        # 处理answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        totals = ans_json["paging"]["totals"]
        next_url = ans_json["paging"]["next"]

        # 提取具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            # anthor_id可能存在没有 匿名回答的 所以需要写一个if else
            answer_item["anthor_id"] = answer["author"]["id"] if "id" in answer["anthor"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item


        if not is_end:
            # 如果没有end就继续请求后续的页面
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)


    # scrapy爬取的入口是start_requests，因为需要登录后才能看到里面的数据，所以要重写入口逻辑
#     FormReqest用来处理表单数据，参数需要填写url，表单数据formdata，
    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/login/phone_num',headers=self.headers,callback=self.login)]


    def login(self,response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"',response_text,re.DOTALL)
        if match_obj:
            xsrf = match_obj.group(1)

        if xsrf:

            return [scrapy.FormRequest(
                url="https://www.zhihu.com/login/phone_num",
                formdata ={
                    "_xsrf":xsrf,
                    "phone_num":"489489489",
                    "password":"123123123"
                },
                header=self.headers,
                # 每一个request需要做下一步的处理都需要设置好一个callback不需要做下一步就会进入parse
                callback=self.check_login
            )]

    # 验证服务器返回数据判断是否登录成功
    def check_login(self,response):
        text_json = json.load(response.text)
        if "msg" in text_json and text_json["msg"] == "登陆成功":
            for url in self.start_urls:
                # dont_filter过滤重复网页
                yield scrapy.Request(url,dont_filter=True,headers=self.headers)

