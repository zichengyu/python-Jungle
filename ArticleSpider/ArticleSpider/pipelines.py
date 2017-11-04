# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
from twisted.internet.defer import Deferred


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open("article.json", 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '123456', 'article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            REPLACE INTO article_spider.jobbole_article(title, create_date, url, url_object_id, 
            front_image_url, front_image_path, comment_nums, fav_nums, praise_nums, tags, content) 
            VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s);
        """
        # 可能导致阻塞
        self.cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["url_object_id"],
                                         item["front_image_url"], item["front_image_path"], item["comment_nums"],
                                         item["fav_nums"], item["praise_nums"], item["tags"], item["content"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    # 使用异步容器将数据库插入异步化
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        # 读settings.py文件获取配置 可使用scrapy Django item自动插入数据库
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            # port=settings["MYSQL_PORT"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将MySQL插入变为异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    REPLACE INTO article_spider.jobbole_article(title, create_date, url, url_object_id, 
                    front_image_url, front_image_path, comment_nums, fav_nums, praise_nums, tags, content) 
                    VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s);
                """
        # 可能导致阻塞
        cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["url_object_id"],
                                    item["front_image_url"], item["front_image_path"], item["comment_nums"],
                                    item["fav_nums"], item["praise_nums"], item["tags"], item["content"]))


class JsonExporterPipeline(object):
    # 调用scrapy提供的json exporter导出json文件
    def __init__(self):
        self.file = open('articleexporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item=item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    #生成图片的本地保存路径
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path

        return item
        pass
