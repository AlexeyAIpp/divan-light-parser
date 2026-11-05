import scrapy


class DivanLightSpider(scrapy.Spider):
    name = "divan_light"
    allowed_domains = ["divan.ru"]
    start_urls = ["https://www.divan.ru/category/svet"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "ROBOTSTXT_OBEY": True,
        "FEED_EXPORT_ENCODING": "utf-8-sig",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_products = set()

    def parse(self, response):
        # Находим карточки товаров.
        lights = response.css('[data-testid="product-card"]')

        for light in lights:
            name = light.css(".ProductName::text").get()
            price = light.css('[data-testid="price"]::text').get()
            href = light.css("div._I5qQa_name a::attr(href)").get()

            if not name or not price or not href:
                continue

            url = response.urljoin(href)

            # Не сохраняем один товар повторно.
            if url in self.seen_products:
                continue

            self.seen_products.add(url)

            yield {
                "name": name.strip(),
                "price": price.strip(),
                "url": url,
            }

        # Находим ссылки на другие страницы раздела освещения.
        page_links = response.css(
            'a[href*="/category/svet/page-"]::attr(href)'
        ).getall()

        for href in set(page_links):
            yield response.follow(href, callback=self.parse)