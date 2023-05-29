from typing import Any, Mapping

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.firefox.options import Options 
import time

from courier_scraper_utilities import scrape_story


#### Before you experiment with the code below, it's probably a good idea to look through courier_scraper_utilities.python
#### That file contains the logic for actually scraping stories

#### Now it's time to begin actual scraping. If you navigate to a courier website, e.g. "cardinalpine.com"
#### And you scroll down to the bottom of the story feed and click the "LOAD MORE STORIES" link
#### You'll find that the page will load 8 additional stories
#### Given that behavior, we should set up a loop that will iteratively scrape stories, load more stories, scrape stories, load more stories, and so on


# We'll use "number_of_stories_seen" to form our loop condition.  
# If we press "load more stories" but the number of stories in the feed doesn't increment above "number_of_stories_seen, we're presumably done. 
# I say presumably, because I'm not sure how long we can keep loading stories without breaking the page
# And even if we can keep loading for a while, I'm not sure doing so wil capture every story Cardinal & Pine has published
# You'll want to do some sanity checks to ensure this approach really can capture all the stories. 

# If it happens to work, great! If not, we'll have to devise something new :)
# Feel free to reach out if you'd like to talk strategy. For now, take this script as more of a scraping tutorial than a perfect methodology for logging all stories
# Some of the "fun" of scraping comes from figuring out how to get the content you want

number_of_stories_seen = 0  # And without further ado, the variable in question 

# This is a CSS selector. # See https://saucelabs.com/resources/blog/selenium-tips-css-selectors for more info
# Each story element in the feed is contained in a div with the class "item"
# We can select it with this CSS selector syntax
story_container_css_selector = "div.item"

feed_container_class = "recent-posts"  # This is the HTML class of the div containing the story feed 

more_button_css_selector = "load-more-button"

story_url_css_selector = "a.item-title" # Another CSS selector that we'll use to find story URLs 

all_stories_metadata = []

##### Load landing page for individual Courier Site

# the interface for turning on headless mode 
options = Options() 
options.add_argument("-headless") 

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)  # Ensure we have the latest GeckoDriver (used to run Firefox)

# landing_page_url = "https://cardinalpine.com/"  # The landing page (hopefully) contains a dynamic list of all the stories we need to scrape from that outlet 
# driver.get(landing_page_url)  # Navigate to the landing page  

urls = ["https://cardinalpine.com/"]#, "https://vadogwood.com/", "https://keystonenewsroom.com/", "https://upnorthnewswi.com/", "https://gandernewsroom.com/", "https://theamericanonews.com/floricua/", "https://coppercourier.com/"]
# Iowa Starting Line 2 doesn't match overall design

for url in urls:
    driver.get(url)
    number_of_stories_seen = 0
    # I dislike the "while True" syntax, but it's standard in Python
    # See https://peps.python.org/pep-0315/ and https://twitter.com/raymondh/status/1528772337306419200
    # We'll break the loop when we reach our exit condition
    while True:
        #### Find the "recent stories" feed
        feed_container_element = driver.find_element(By.CLASS_NAME, feed_container_class)  # We'll capture that div in a python variable for easy access
        
        # Capture all of the story container divs in our feed
        # Note that we're using "find_elements" here, not "find_element" like we used above. 
        # find_elements will return all of the elements matching our selection criterion. find_element only returns the first
        story_container_elements = feed_container_element.find_elements(By.CSS_SELECTOR, story_container_css_selector)  
        
        # If we've seen all the stories in the feed, we're done. Break the loop
        number_of_stories_in_feed = len(story_container_elements)
        # print(number_of_stories_in_feed)
        if number_of_stories_in_feed == number_of_stories_seen:
            print(f"No more stories in feed. Processed {number_of_stories_seen} stories total")
            break 
        
        print(f"{number_of_stories_in_feed} stories in feed")
        # Stories load 8 at a time. We should always scrape the most recently loaded 8 stories. 
        for story_container_element in story_container_elements[-8:]:
            # Find the "a" tag containing the story link
            # Then extract its "href" attribute, AKA the story's URL
            story_url = story_container_element.find_element(By.CSS_SELECTOR, story_url_css_selector).get_attribute("href")
            
            # Do the actual scraping
            story_metadata = scrape_story(driver, story_url)  
            
            # Store the current story's metadata in our larger data structure
            all_stories_metadata.append(story_metadata) 
            
            # increment our stories seen counter
            number_of_stories_seen += 1
        
        # After each set of 8 stories, we'll need to load more. 
        # Remove the break below and find a way to click on the "load more stories" link
        # You may need to make sure the link is visible before you click it (scroll to it)
        # break
        more_button_element = driver.find_element(By.CLASS_NAME, more_button_css_selector)
        more_button_element.click()
        time.sleep(2)
    print("Total stories scraped", number_of_stories_seen)




### eventually you'll want to write that all_stories_metadata array to a database
### when you're designing a schema for the database, you might consider creating one table for outlets, one for stories, and another for authors
### although if you have a solution you like better, feel free to go that way.  
### And again, email or drop a message if you have questions.


### I've put all this code into a single script
### Feel free to break it into functions/odules
### Or use feature flags so that you can keep most of the code in one file but experiment with certain functionality (say, storing stuff in the database)
### Without running the scraper bits
### Check out https://www.atlassian.com/continuous-delivery/principles/feature-flags if you've never worked with feature flags
### Your code will look like:
###
###  RUN_SCRAPER = False  # don't wanna run the scraping code
###  SAVE_TO_DATABASE = True  # do want to run the database code
###
### if RUN_SCRAPER:
###     {scraper_code...}
###     ...
###     ...
### if SAVE_TO_DATABASE:
###     {database_saving_code...}
###     ...
###     ...
