# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs  # 打开文件(open) 文件编码

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi  # 异步
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter  # 可直接导出json文件
# __all__ = ['BaseItemExporter', 'PprintItemExporter', 'PickleItemExporter',
#            'CsvItemExporter', 'XmlItemExporter', 'JsonLinesItemExporter',
#            'JsonItemExporter', 'MarshalItemExporter']


class TestspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False)  # ensure_ascii=False 能显示中文
        self.file.write(lines)
        return item

    def spider_closed(self, spider):  # 调用结束后自动执行
        self.file.close()


class JsonExporterPipeline(object):
    # 调用scrapy提供的JsonItemExporter导出json文件
    def __init__(self):
        self.file = open('article_export.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value.get("path", "NOT_FOUND_ImageUrl")
                item["front_image_path"] = image_file_path
            return item


class MysqlPipeline(object):
    # 同步操作 数据库写入速度小于爬取的速度
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '1213', 'spider_test',
                                    charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
                insert into jobbole_article(title, url, create_date, fav_nums, url_object_id, comment_nums, praise_nums,
                 tags, content) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"],
                                         item["url_object_id"], item["comment_nums"], item["praise_nums"],
                                         item["tags"], item["content"]))
        self.conn.commit()
        return item

class MysqlTwistedPipeline(object):
    # 异步
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 初始化的时候就会调用
        dbparms = dict(
        host = settings["MYSQL_HOST"],
        password = settings["MYSQL_PASSWORD"],
        db = settings["MYSQL_DBNAME"],
        user = settings["MYSQL_USER"],
        charset='utf8',
        cursorclass = MySQLdb.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    def handle_error(self, failure, item, spider):
        # 处理异步 插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    insert into jobbole_article(title, url, create_date, fav_nums, url_object_id, comment_nums, praise_nums,
                     tags, content, front_image_url, front_image_path) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
        cursor.execute(insert_sql, (item["title"], item["url"], item["create_date"], item["fav_nums"],
                                    item["url_object_id"], item["comment_nums"], item["praise_nums"],
                                    item["tags"], item["content"], item.get("front_image_url"), item.get("front_image_path")))
