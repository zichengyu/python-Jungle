# -*- coding: utf-8 -*-
import scrapy
<<<<<<< HEAD
import re
=======
>>>>>>> 292e8b763378e60db40e221cff55068102a26409


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
<<<<<<< HEAD
    start_urls = ['http://blog.jobbole.com/112783/']

    def parse(self, response):
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·','').strip()
        praise_nums = response.xpath("//span[contains(@class, 'vote-post-up')]/h10/text()").extract()[0]
        fav_nums = response.xpath("//span[contains(@class, 'bookmark-btn')]/text()").extract()[0]
        match_re = re.match(r".*(\d+).*", fav_nums)
        if match_re:
            fav_nums = match_re.group(1)

        comment_num = response.xpath("//a[@href='#article-comment']/span").extract()[0]
        match_re = re.match(r".*(\d+).*", comment_num)
        if match_re:
            comment_num = match_re.group(1)

        contetn = response.xpath("//div[@class='entry']").extract()[0]

        print(contetn)
        pass

=======
    start_urls = ['http://blog.jobbole.com/']

    def parse(self, response):
        pass
>>>>>>> 292e8b763378e60db40e221cff55068102a26409
