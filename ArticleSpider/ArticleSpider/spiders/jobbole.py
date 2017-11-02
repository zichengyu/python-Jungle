# -*- coding: utf-8 -*-
import re
from urllib import parse

import scrapy
from scrapy.http import Request


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
        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        for post_url in post_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)
            #print(post_url)
        #提取下一页交给scrapy下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
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
        title1 = response.css(".entry-header h1::text").extract_first()
        create_date1 = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace('·', '').strip()
        praise_nums1 = response.css(".vote-post-up h10::text").extract_first().strip()
        fav_nums1 = response.css("span.bookmark-btn::text").extract_first()
        match_re = re.match(r".*(\d+).*", fav_nums1)
        if match_re:
            fav_nums1 = int(match_re.group(1))
        else:
            fav_nums1 = 0

        comment_num1 = response.css('a[href="#article-comment"] span::text').extract_first()
        match_re = re.match(r".*(\d+).*", comment_num1)
        if match_re:
            comment_num1 = int(match_re.group(1))
        else:
            comment_num1 = 0

        content1 = response.css("div.entry").extract_first()
        tag1 = response.css("p.entry-meta-hide-on-mobile a::text").extract_first()
        tag_list = [element for element in tag1 if not element.strip().endswith('\0')]
        tag_list = ",".join(tag_list)
        pass
