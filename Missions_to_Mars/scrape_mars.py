# Dependencies
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import time
import pandas as pd

def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # First Variable
    # URL of page to be scraped
    url = 'https://mars.nasa.gov/news/'
    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')

    # collects title and paragraph
    news_title = soup.find("div", class_="content_title").a.text.strip()
    news_p = soup.find('div', class_="rollover_description_inner").text

    # Second Variable
    # URL of page to be scraped, query is broken out because base URL is used later.
    url = 'https://www.jpl.nasa.gov'
    query = '/spaceimages/?search=&category=Mars'

    # Visits and navigates to correct page to collect URL
    browser.visit(url+query)
    browser.click_link_by_partial_text('FULL IMAGE')
    browser.click_link_by_partial_text('more info')

    # Create BeautifulSoup object; parse with 'html.parser'
    html = browser.html
    soup = bs(html, 'html.parser')

    # Collects image URL
    figure = soup.find('figure', class_='lede').a['href']
    featured_image_url = url+figure

    # Third Variable
    # URL of page to be scraped
    url = 'https://twitter.com/marswxreport?lang=en'

    # Retrieve page with the requests module
    response = requests.get(url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')

    # collects latest tweet, splits and cleans data for more readable tweet.
    mars_weather = soup.find('div', class_='js-tweet-text-container').p.text
    mars_weather = mars_weather.split('pic')[0]
    mars_weather = mars_weather.replace("\n"," ")

    # Fourth Variable
    # URL of page to be scraped
    url = "https://space-facts.com/mars/"

    # Use Pandas to "read_html" to parse the URL
    tables = pd.read_html(url)
    #Find Mars Facts DataFrame in the lists of DataFrames
    facts_df = tables[0]

    # builds table in html for further use.
    facts_df.columns = ['Description', 'Value']
    html_table = facts_df.to_html(index=False)
    
    # Fifth Variable
    # URL of page to be scraped, query is broken out because base URL is used later.
    url = "https://astrogeology.usgs.gov"
    query = "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"


    # Visits url to begin scraping
    browser.visit(url+query)
    html = browser.html
    soup = bs(html, 'html.parser')

    # collects the four hemisphere html strings to begin URL collects
    hemispheres = soup.find_all('div', class_='item')
    hemisphere_image_urls = []

    for hemisphere in hemispheres: 
        
        # Collects title
        title = hemisphere.find('h3').text
        
        # Builds URL to find full resolution image
        img = hemisphere.find('a', class_='itemLink product-item')['href']
        browser.visit(url + img)
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # finds and builds URL for full resolution image
        img_url = url + soup.find('img', class_='wide-image')['src']
        
        # appends to dictionary
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
        
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "html_table": html_table,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data