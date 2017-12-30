from scrapy import Spider
from NewsAgency.items import NewsagencyItem
from scrapy.http.request import Request


class NewsAgencySpider(Spider):

    name = "news_agency"
    allowed_domains = ["wikipedia.org"]

    start_urls = [
        "https://en.wikipedia.org/wiki/News_agency",
    ]

    # rules = (
    #     Rule(LinkExtractor(allow=()), callback="parse", follow=True),
    # )

    custom_settings = {
        # specifies exported fields and order
        'FEED_EXPORT_FIELDS': ["name", "link", "language"],
    }

    def parse(self, response):
        links = response.xpath('//div[@style="-moz-column-width: 25em; -webkit-column-width: 25em; column-width: 25em;"]//li//a')
        URL = "https://en.wikipedia.org"
        for selector in links:
            url = selector.css("a::attr(href)").extract_first()
            ref = URL + url
            request = Request(ref, callback=self.parse_agency)
            yield request

    def parse_agency(self, response):
        item = NewsagencyItem()
        urls = []

        item["name"] = response.xpath('//h1[@class="firstHeading"]//i/text()').extract_first()
        if item["name"] is None:
            item["name"] = response.xpath('//h1[@class="firstHeading"]/text()').extract_first()

        url = response.xpath('//table[contains(@class, "infobox")]/tr//a[contains(@class, "external")]')
        item["link"] = url.css("a::attr(href)").extract_first()
        for sel in url:
            if sel.css("a::attr(href)").extract_first() == item["link"]:
                continue
            else:
                urls.append(sel.css("a::attr(href)").extract_first())

        external_links = response.xpath('//div[@class="mw-parser-output"]/ul//a[contains(@class, "external")]')
        for link in external_links:
            ref = link.css("a::attr(href)").extract_first()
            if ref in urls or str(item["link"]) in ref:
                continue
            else:
                urls.append(ref)
        item["language"] = urls

        yield item
