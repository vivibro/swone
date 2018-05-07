# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs #避免编码过程中繁杂工作
import json
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


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

# 传入数据库
class MysqlPipeline(object):

    def __init__(self):
        # 链接数据库
        # self.conn = MySQLdb.connect('host','user','password','dbname',charset = 'utf8',use_unicode=True)
        self.conn = pymysql.connect('127.0.0.1', 'root', 'root', 'swone', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
            insert into jobbole_artcle(blog_title, url, blog_date, blog_bookmark,url_object_id,front_image_url,vote_up,tags,comment_num,content)
            VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s)
        '''
        self.cursor.execute(insert_sql, (item["blog_title"], item["url"], item["blog_date"], item["blog_bookmark"],item["url_object_id"],item["front_image_url"],item["vote_up"],item["tags"],item["comment_num"],item["content"]))
        self.conn.commit()

# 通过连接池来实现插入异步化
class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparms = dict(
            # 变量名写法固定
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用Twisted将mysql插入变成异步执行
        # 参数1 传入一个回调函数  使其方法异步
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider)#处理异常

    def handle_error(self,failure,item,spider):
        # 处理异步插入的异常
        # 如果不需要处理item及spider的相关数据  可以在上面的addErrorback参数列表中少加入相关参数
        print(failure)

    def do_insert(self,cursor,item):
        # 执行具体的插入
        insert_sql = '''
            insert into jobbole_artcle(blog_title, url, blog_date, blog_bookmark,url_object_id,front_image_url,vote_up,tags,comment_num,content)
            VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s)
        '''
        cursor.execute(insert_sql, (item["blog_title"], item["url"], item["blog_date"], item["blog_bookmark"],item["url_object_id"],item["front_image_url"],item["vote_up"],item["tags"],item["comment_num"],item["content"]))








