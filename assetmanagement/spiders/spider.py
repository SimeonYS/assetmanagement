import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AassetmanagementItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class AassetmanagementSpider(scrapy.Spider):
	name = 'assetmanagement'
	start_urls = ['https://www.assetmanagement.hsbc.com.mx/es-mx/individual-investor/news-and-insights']

	def parse(self, response):
		post_links = response.xpath('//h3[@class="article-list__heading"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li/span[@class="pagination__button pagination__button--next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="page-heading__date"]//text()').get().strip()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="page-heading__introduction-text"]/font/font/text()').getall() + response.xpath('//div[@class="key-information-panel"]//text()').getall()
		if not content:
			content = response.xpath('//div[@class="col-sm-12 col-md-6 main"]//text()[not (ancestor::script or ancestor::div[@class="social-share-buttons"] or ancestor::div[@class="tags"] or ancestor::div[@class="article-actions"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=AassetmanagementItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
