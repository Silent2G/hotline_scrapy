from scrapy.pipelines.images import ImagesPipeline
from scrapy.http.request import Request
import MySQLdb


class HotlineUaPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        yield Request(url=item['image_urls'][0], meta={"image_name": item["name"]})

    def file_path(self, request, response=None, info=None):
        image_name = request.meta["image_name"]
        return image_name  # return request.meta.get('filename', '')


class HotlineUaPipelineDB(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', 'b01020534',
                                    'scrapiPython', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            self.cursor.execute("""INSERT INTO laptops (id_shop, name, price, brand, description, min_price, max_price, photo_path, photo_name)  
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (2,
                                 item['title'].encode('utf-8'),
                                 item['price'],
                                 item['brand'].encode('utf-8'),
                                 item['description'].encode('utf-8'),
                                 item['min_price'],
                                 item['max_price'],
                                 item['image_urls'][0].encode('utf-8'),
                                 item['name'].encode('utf-8')))
            self.conn.commit()
        except MySQLdb.Error as e:
            print("Error: " + str(e))
        return item