from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options 

import re
import psycopg2

from courier_scraper_utilities import scrape_story, make_request

# Creating headless driver
options = Options() 
options.add_argument("-headless") 
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

# Feature flag for database
save_to_database = False

# Setting up some essential variables
#   per_page is the number of story urls we want to request
#   page represents which nth group of per_page story urls we need
#       ex. per_page = 300, page = 2 will return stories 300 - 599 and page = 1 will return stories 0 - 299
#   nonce is like a key and changes every day at midnight PST
#       Thankfully, it is stored in script tags on the website so we can obtain it automatically
#       and it is also the same accross all courier sites
courier_urls = ["https://cardinalpine.com", "https://gandernewsroom.com", "https://upnorthnewswi.com", "https://coppercourier.com", "https://vadogwood.com", "https://keystonenewsroom.com", "https://theamericanonews.com/floricua"]
# Iowa Starting Line, https://iowastartingline.com/, doesn't follow the same design
page = 1
per_page = 300
driver.get(courier_urls[0])
nonce_element = driver.find_element(By.ID, 'site-script-js-extra').get_attribute("innerHTML")
nonce = re.search(r'(?:_nonce\"\:\")(\w+)(?:\"\})', nonce_element).group(1)

# Connecting to database
if save_to_database:
    conn = psycopg2.connect(database=os.environ.get('COURIER_DB_NAME'),
                            host=os.environ.get('COURIER_DB_HOST'),
                            user=os.environ.get('COURIER_DB_USER'),
                            password=os.environ.get('COURIER_DB_PASSWORD'),
                            port=os.environ.get('COURIER_DB_PORT'))
    cursor = conn.cursor()

# Creating txt file for urls of articles that didn't scrape successfully
log = open("courierscraper.log", "w")

for courier_url in courier_urls:
    # Getting the first per_page stories
    response = make_request(nonce, page, per_page, courier_url + "/wp-admin/admin-ajax.php")
    story_urls = re.findall(r'(?:<a class=\\\"item-title\\\" href=\\\")(\S+)(?:\\\/\\\">)', response.text)
    stories_total = int(re.search(r'(?:\"total\"\:)([0-9]+)(?:,\")', response.text).group(1))
    stories_scraped = 0

    log.write(f"Start scraping {url}. Stories expected: {stories_total}\n")
    print('**' * 20)
    print(f'Started. Stories expected: {stories_total}')
    print('**' * 20)

    while True:
        if len(story_urls) == 0:
            log.write(f"Finished scraping {courier_url}. Stories scraped: {stories_scraped}/{stories_total}")
            print('**' * 20)
            print(f'Finished. Stories scraped: {stories_scraped}/{stories_total}')
            print('**' * 20)
            break
        else:
            for story_url in story_urls:
                clean_url = re.sub(r"\\", "", story_url)

                try:
                    story_metadata = scrape_story(driver, clean_url)
                    stories_scraped += 1
                except TimeoutException:
                    # Sometimes the stories won't load properly. Then we can try to scrape for a second time
                    # If that still fails, the story page likely doesn't follow the normal format and we'll log it
                    try:
                        print("Scrape failed, trying again")
                        story_metadata = scrape_story(driver, clean_url)
                        stories_scraped += 1
                    except TimeoutException:
                        print("Scrape failed again, moving on to next story")
                        log.write(f"Scrape failed for {clean_url}\n")

                # Quitting and re-initializing the driver to recover cache space
                if stories_scraped % 50 == 0:
                    print("Resetting driver")
                    driver.quit()
                    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

                if stories_scraped % 20 == 0:
                    print(f"Stories scraped: {stories_scraped}/{stories_total}")

        page += 1
        print("Requesting more story urls")
        response = make_request(nonce, page, per_page, url + "/wp-admin/admin-ajax.php")
        story_urls = re.findall(r'(?:<a class=\\\"item-title\\\" href=\\\")(\S+)(?:\\\/\\\">)', response.text)

driver.quit()
log.close()