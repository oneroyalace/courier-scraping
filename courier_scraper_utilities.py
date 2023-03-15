from typing import Any, Mapping

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager



## constant variables used in `scrape_story` below
story_title_selector = "h1.entry-title"
story_author_selector = "span.post-author"
story_section_selector = "a.post-category"

""" Extracts metadata from the story at `url` 
Args:
    driver: The Selenium Firefox WebDriver instance
    url: A url that hopefully points to a story
Returns:
    A dictionary containing metadata on the story. You'll probably want to catpure more metadata than I did. 
    I imagine we might want the full text of the story, etc, etc
"""
def scrape_story(driver: WebDriver, url: str) -> Mapping[str, Any]:
    print("scraping story", url)
    open_url_in_new_tab(driver, url)  # Open the story in a new tab
    
    story_title = driver.find_element(By.CSS_SELECTOR, story_title_selector).text  # Since we want raw metadata, we're accessing the elements' text attributes
    story_author = driver.find_element(By.CSS_SELECTOR, story_author_selector).text
    story_section = driver.find_element(By.CSS_SELECTOR, story_section_selector).text
    story_text = "" #...
    
    # ...
    # capture additional metadata
    # ...
    story_metadata = {
        "title": story_title,
        "author": story_author,
        "section": story_section,
        "url": url,
        #... additional metadata
    }
    close_current_tab(driver)  # close the story tab and return to the landing page tab
    return story_metadata


""" Opens a new selenium driver  tab and navigates to the url provided
Args:
    driver: The Selenium Firefox WebDriver instance
    url: The url to navigate to
Returns:
    None
"""
def open_url_in_new_tab(driver: WebDriver, url: str) -> None:
    driver.switch_to.new_window() # opens a new tab
    new_tab_handle = driver.window_handles[-1]  # grab the last browser handle (which we just opened)
    driver.switch_to.window(new_tab_handle)
    driver.get(url)


""" Closes the current selenium driver tab and switches context to the first open tab
Args:
    driver: The Selenium Firefox WebDriver instance
Returns:
    None
"""
def close_current_tab(driver: WebDriver) -> None:
    driver.close()
    main_tab_handle = driver.window_handles[0]
    driver.switch_to.window(main_tab_handle)



