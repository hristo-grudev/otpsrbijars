import scrapy
from scrapy import Selector

from scrapy.loader import ItemLoader
from ..items import OtpsrbijarsItem
from itemloaders.processors import TakeFirst

base = r"https://www.otpsrbija.rs/wp-json/api/v1/alerts?page={}&year=&month="
class OtpsrbijarsSpider(scrapy.Spider):
	name = 'otpsrbijars'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		data = response.json()
		raw_data = data["content"]["content"]
		post_links = Selector(text=raw_data).xpath('//div[@class="blog__item"]')
		for post in post_links:
			url = post.xpath('.//a/@href').get()
			date = post.xpath('./span[@class="blog__date"]/text()').get()
			if date:
				date = date.split(':')[1]
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		if data["hasMore"]:
			self.page += 1
			next_page = base.format(self.page)
			yield response.follow(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="blog-details__text"]//text()[normalize-space() and not(ancestor::h1 | ancestor::span[@class="date"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=OtpsrbijarsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
