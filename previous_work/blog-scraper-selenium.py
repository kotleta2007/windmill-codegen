import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Run this script with:
# rm blogs.jsonl; scrapy runspider blog-scraper-selenium.py -o blogs.jsonl

class ZapierBlogSeleniumSpider(scrapy.Spider):
    name = 'zapier_blog_selenium'
    start_urls = ['https://zapier.com/blog/all-articles/automation-inspiration/']
    
    def __init__(self):
        service = Service(executable_path=r'/usr/bin/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=service, options=options)

    def subparse(self, response):
        # Use Selenium to get the page with JavaScript executed
        self.driver.get(response)

        # Wait for the necessary elements to load (can adjust the time as necessary)
        self.driver.implicitly_wait(10)  # in seconds

        # Create a Selector from the Selenium response
        sel = Selector(text=self.driver.page_source)

        integrations_found = sel.xpath('//div[@data-testid="zap-template"]').getall()

        if integrations_found is None:
            return None
        if len(integrations_found) == 0:
            return None

        integrations_parsed = []
        for integration in integrations_found:
            integration_sel = Selector(text=integration)
            full_integration_description = integration_sel.xpath('//div[contains(@class, "titleArea")]//text()').get()
            apis_used = integration_sel.xpath('//div[contains(@class, "metaInfoArea")]//text()').get()

            integrations_parsed.append((full_integration_description, apis_used))

        return integrations_parsed

    def parse(self, response):
        # Use Selenium to get the page with JavaScript executed
        self.driver.get(response.url)

        # Wait for the necessary elements to load (can adjust the time as necessary)
        self.driver.implicitly_wait(10)  # in seconds

        # Create a Selector from the Selenium response
        sel = Selector(text=self.driver.page_source)

        blog_prefix = 'https://zapier.com'

        next_page = blog_prefix + sel.xpath('//a[contains(@aria-label, "Next page")]').xpath('@href').get() 

        for article in sel.xpath('//li[div/@data-testid]//a[@data-testid="articleCard-articleLink"]'):
            link = blog_prefix + article.xpath('@href').get()

            integrations_found = self.subparse(link)
            
            yield {
                'name': article.xpath('./p[1]/text()').get(),
                'link': link,
                'integrations_found': integrations_found,
            }
        
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def closed(self, reason):
        self.driver.quit()
