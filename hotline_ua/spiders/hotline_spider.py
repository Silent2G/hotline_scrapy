import scrapy
import os
import hashlib


class HotlineSpider(scrapy.Spider):
    name = "hotline"
    allowed_domains = ['hotline.ua']
    counter = 1
    start_urls = ('https://hotline.ua/computer/noutbuki-netbuki/',)

    def parse_description_array(self, string_array):
        res = ""
        for string in string_array:
            string = string.strip()
            res = str(res + string + ' ')
        res = res.rstrip()
        return res

    def find_brand(self, string):
        res = string.find(' ')
        return string[:res]

    def image_key(self, url):
        index = hashlib.md5(os.urandom(32)).hexdigest()

        image_start_name = url.split('/')[-1]
        point_index = image_start_name.rindex('.')
        name = image_start_name[:point_index]
        extension = image_start_name[point_index:]

        res = str(name + '_' + index + extension)

        # if length of string more than 100
        if len(res) >= 100:
            res = res[:100]

        return res

    def parse(self, response):
        laptops = response.xpath("//*[@class='product-item']")

        for laptop in laptops:
            title = laptop.xpath(".//*[@class='info-description']/p/a/text()").extract_first()
            title = title.strip()
            title = title.rstrip()

            brand = self.find_brand(title)

            description = laptop.xpath(".//*[@class='info-description']").xpath(".//*[@class='text']/p/text()").extract()
            description = self.parse_description_array(description)

            price = laptop.xpath(".//*[@class='item-price stick-bottom']").xpath(".//*[@class='price-md']")\
                .xpath(".//*[@class='value']/text()").extract_first()
            if price:
                price = price.replace(u'\xa0', '')

            min_price = None
            max_price = None

            prices = laptop.xpath(".//*[@class='item-price stick-bottom']").xpath(".//*[@class='text-sm']/text()").extract()
            if len(prices) > 0:
                prices = prices[0]
                prices_clear = prices.replace(u'\xa0', '')
                prices_clear = prices_clear.replace('грн', '')

                hifen_index = prices_clear.find('–')

                min_price = prices_clear[:hifen_index]

                max_price = prices_clear[hifen_index + 1:]

            img_url = laptop.xpath(".//*[@class='item-img']").css("img::attr(src)").extract_first()
            img_url = str('https://hotline.ua' + img_url)

            if img_url == 'https://hotline.ua/public/i/img-265.gif':
                name = 'img-265.gif'
            else:
                name = self.image_key(img_url)

            yield {
                "title": title,
                "brand": brand,
                "description": description,
                "price": price,
                "min_price": min_price,
                "max_price": max_price,
                "image_urls": [img_url],
                "name": name
            }

        next_page = response.xpath("//*[@class='pagination']").xpath(".//*[@class='next']").css("a::attr(href)").extract_first()
        if next_page:
            yield scrapy.Request(url='https://hotline.ua/computer/noutbuki-netbuki/' + next_page)
