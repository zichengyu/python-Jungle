# -*- coding: utf-8 -*-
import re
import datetime
from urllib import parse

import scrapy
from scrapy.http import Request

from ArticleSpider.items import JobBoleArticleItem
from ArticleSpider.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1、获取文章列表的文章，并交给scrapy去解析
        2、获取下一个页面的url，并交给scrapy去下载
        """
        # 解析列表页中的所有的url
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")

        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),meta={"front_image_url":image_url}, callback=self.parse_detail)
            #print(post_url)
        #提取下一页交给scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobBoleArticleItem()

        # 提取文章的具体信息
        # xpath解析
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        # create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·',                                                                                                           '').strip()
        # praise_nums = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        # fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        # fav_nums = response.css("span.bookmark-btn::text").extract()[0]
        # match_re = re.match(r".*(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = match_re.group(1)
        # comment_num = response.xpath("//a[@href='#article-comment']/span").extract()[0]
        # match_re = re.match(r".*(\d+).*", comment_num)
        # if match_re:
        #     comment_num = match_re.group(1)
        # contetn = response.xpath("//div[@class='entry']").extract()[0]
        # print(contetn)

        # css选择器
        front_image_url  =response.meta.get("front_image_url","") #文章封面图
        title = response.css(".entry-header h1::text").extract_first()
        create_date = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace('·', '').strip()
        praise_nums = response.css(".vote-post-up h10::text").extract_first().strip()
        fav_nums = response.css("span.bookmark-btn::text").extract_first()
        match_re = re.match(r".*(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.css('a[href="#article-comment"] span::text').extract_first()
        match_re = re.match(r".*(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        content = response.css("div.entry").extract_first()
        tags = response.css("p.entry-meta-hide-on-mobile a::text").extract_first()
        tag_list = [element for element in tags if not element.strip().endswith('\0')]
        tag_list = ",".join(tag_list)

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        article_item["url"] = response.url
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

        yield article_item #传到pipelines.py
