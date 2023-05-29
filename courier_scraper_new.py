from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options 

import re
import time

from courier_scraper_utilities import scrape_story, make_request

url = "https://cardinalpine.com/wp-admin/admin-ajax.php"

# nonce changes every day at midnight PST!
nonce = "45208465a2"
page = 1
per_page = 300

options = Options() 
options.add_argument("-headless") 

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

response = make_request(nonce, page, per_page, url)
story_urls = re.findall(r'(?:<a class=\\\"item-title\\\" href=\\\")(\S+)(?:\\\/\\\">)', response.text)
# Get total stories
stories_total = int(re.search(r'(?:\"total\"\:)([0-9]+)(?:,\")', response.text).group(1))
stories_scraped = 0

while True:
    if len(story_urls) == 0:
        print('**' * 20)
        print(f'Done. Stories scraped: {stories_scraped}')
        print('**' * 20)
        break
    else:
        for story in story_urls:
            if stories_total == stories_scraped:
                driver.quit()
                break
            
            story_metadata = scrape_story(driver, re.sub(r"\\", "", story))
            stories_scraped += 1

            if stories_scraped % 50 == 0:
                print("RESETING DRIVER")
                print(f"Stories scraped: {stories_scraped}")
                driver.quit()
                driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

            if stories_scraped % 10 == 0:
                print(f"Stories scraped: {stories_scraped}")

    page += 1
    print("REQUESTING MORE STORY URLS")
    print(f"Stories scraped: {stories_scraped}")
    response = make_request(nonce, page, per_page, url)
    story_urls = re.findall(r'(?:<a class=\\\"item-title\\\" href=\\\")(\S+)(?:\\\/\\\">)', response.text)
