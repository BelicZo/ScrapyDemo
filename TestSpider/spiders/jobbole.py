# -*- coding: utf-8 -*-
import re
from urllib import parse
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
# import urlparse

from TestSpider.items import JobBoleArticleItem
from TestSpider.utils.common import get_md5
from TestSpider.items import ArticleItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载, 下载完成后交给parse
        :param response:
        :return:
        """
        post_nodes = response.css("#archive div.floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        # 提取下一页
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first('')
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobBoleArticleItem()

        # 提取文章的具体字段

        # /html/body/div[3]/div[3]/div[1]/div[1]
        # //*[@id="post-110287"]/div[1]/h1
        # / html / body / div[3] / div[3] / div[1] / div[1] / h1
        """
        # xpath
        re_selector = response.xpath('//*[@id="post-110287"]/div[1]/h1/text()')
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()")
        parise_nums = int(response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0])
        flavor_nums = int(response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0][:-2].strip())
        comment_nums = int(response.xpath("//a[@href='#article-comment']/span/text()").extract()[0][:-2].strip())
        content =  response.xpath("//div[@class='entry']").extract()[0]
        """

        """
        # css 选择器
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        title = response.css(".entry-header h1::text").extract_first()
        create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().strip(' ·')
        praise_nums = int(response.css('.vote-post-up h10::text').extract_first())
        fav_nums = response.css(".bookmark-btn::text").extract_first()
        match_re = re.compile(".*?(\d+).*")
        if match_re.match(fav_nums):
            fav_nums = int(match_re.match(fav_nums).group(1))
        else:
            fav_nums = 0
        comment_nums = response.css("a[href='#article-comment'] span::text").extract_first()
        if match_re.match(comment_nums):
            comment_nums = int(match_re.match(comment_nums).group(1))
        else:
            comment_nums = 0
        content = response.css("div.entry").extract_first()
        tags = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tags if not element.strip().endswith("评论")]
        tags = ','.join(tag_list)

        article_item["title"] = title
        article_item["url"] = response.url
        article_item["url_object_id"] = get_md5(response.url)
        import datetime
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["fav_nums"] = fav_nums
        article_item["comment_nums"] = comment_nums
        article_item["tags"] = tags
        article_item["content"] = content
        """

        # 通过item loader加载item
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [response.meta.get("front_image_url", "")])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_value("url", response.url)
        # item_loader.add_xpath()

        article_item = item_loader.load_item()

        yield article_item
        pass
