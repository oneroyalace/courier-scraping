from typing import Any, Mapping, List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager

import requests

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
    # open_url_in_new_tab(driver, url)  # Open the story in a new tab
    driver.get(url)
    
    # story_title = driver.find_element(By.CSS_SELECTOR, story_title_selector).text  # Since we want raw metadata, we're accessing the elements' text attributes
    # story_author = driver.find_element(By.CSS_SELECTOR, story_author_selector).text
    # story_section = driver.find_element(By.CSS_SELECTOR, story_section_selector).text
    # story_text = "" #...

    story_title = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CSS_SELECTOR, story_title_selector)).text
    story_author = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CSS_SELECTOR, story_author_selector)).text
    story_section = WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CSS_SELECTOR, story_section_selector)).text
    
# driver.navigate("file:///race_condition.html")
# el = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.TAG_NAME,"p"))
# assert el.text == "Hello from JavaScript!"

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
    # close_current_tab(driver)  # close the story tab and return to the landing page tab
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


""" Makes a request asking for story urls
Args:
    nonce: Key needed to make request
    page: Number of story urls
    per_page: Which chunk of page story needed
    url: url of newsroom homepage
Returns:
    Array of length page with story urls
"""
def make_request(nonce: str, page: int, per_page: int, url: str) -> List[str]:
    querystring = {"":""}
    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\nload_more_posts\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"nonce\"\r\n\r\n{nonce}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"per_page\"\r\n\r\n{per_page}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"page\"\r\n\r\n{page}\r\n-----011000010111000001101001--\r\n"
    headers = {
        "cookie": "wordpress_google_apps_login=8c2e542fe10764cc0fda9d90052b1f26",
        "Content-Type": "multipart/form-data; boundary=---011000010111000001101001",
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    return requests.request("POST", url, data=payload, headers=headers, params=querystring)