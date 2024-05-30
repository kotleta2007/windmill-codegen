from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
import scrapy
from scrapy.selector import Selector

# Run this script with:
# rm apps.jsonl; scrapy runspider zapier-apps-scraper.py -o apps.jsonl

class ZapierAppsSeleniumSpider(scrapy.Spider):
    name = 'zapier_apps_selenium'
    start_urls = ['https://zapier.com/apps']
    
    def __init__(self):
        service = Service(executable_path=r'/usr/bin/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=service, options=options)
        self.integrations_found = self.get_all_integrations()

    def get_all_integrations(self):
        '''
        From the first page, create a list of all available integrations
        '''
        
        # Use Selenium to get the page with JavaScript executed
        self.driver.get(self.start_urls[0])

        # Wait for the necessary elements to load (can adjust the time as necessary)
        self.driver.implicitly_wait(10)  # in seconds

        while True:
            try:
                # Locate the <div> containing 'loadMore' in its class attribute
                # Then, find the first <button> inside this <div> and click it
                load_more_button = self.driver.find_element("xpath", "//div[contains(@class, 'loadMore')]//button[1]")
                load_more_button.click()

                # Wait for the content to load. Adjust sleep time as necessary based on observed load times & website behavior
                time.sleep(1)  
            except NoSuchElementException:
                # If no such button is found, assume all content has been loaded
                print("All content loaded.")
                break

        # Locate all <a> tags whose class contains 'CategoryAppCard'
        category_app_cards = self.driver.find_elements("xpath", "//a[contains(@class, 'CategoryAppCard')]")

        time.sleep(1)

        links = []
        for card in category_app_cards:
            print('CARD')
            
            link = card.get_attribute('href')
            name = card.find_element("xpath", ".//span[contains(@class, 'headingText')]//h3").get_attribute("innerHTML")
            
            links.append((link, name))
       
        return links

    def parse(self, response):
        for link in self.integrations_found:
            self.driver.get(link[0])
            while True:
            # for i in range(1):
                try:
                    # Locate the <div> containing 'loadMore' in its class attribute
                    # Then, find the first <button> inside this <div> and click it
                    load_more_button = self.driver.find_element("xpath", "//div[contains(@class, 'TriggerActionList__loadMore')]//button[1]")
                    load_more_button.click()
            
                    # Wait for the content to load. Adjust sleep time as necessary based on observed load times & website behavior
                    time.sleep(0.1)  

                except NoSuchElementException:
                    # If no such button is found, assume all content has been loaded
                    print("All content loaded.")
                    break

            # Now, all the triggers/actions are loaded.
            app_action_divs = self.driver.find_elements("xpath", "//div[contains(@class, 'AppAction')]")

            # Iterate over each app action div
            for app_action_div in app_action_divs:
                try:
                    # Find the first div with class containing 'summaryText'
                    summary_div = app_action_div.find_element("xpath", ".//div[contains(@class, 'summaryText')]")
        
                    # Find the 'h2' tag and 'p' tag within the summary div
                    summary_h2 = summary_div.find_element("xpath", ".//h2").text
                    summary_p = summary_div.find_element("xpath", ".//p").text
        
                    yield {
                        'link': link[0],
                        'name': link[1],
                        'integration': summary_h2,
                        'description': summary_p,
                    }
                except NoSuchElementException:
                    # print('Did not find anything')
                    pass
           
    def closed(self, reason):
        self.driver.quit()
