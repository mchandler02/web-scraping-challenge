from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import time
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

@app.route("/")
def index():
    listings = list(mongo.db.listings.find())
    article_title=listings[0]["redplanet_scrape"]["title"]
    article_text=listings[0]["redplanet_scrape"]["paragraph"]
    spaceimages_url = listings[0]["spaceimages_url"]
    mars_facts = listings[0]["mars_data"]
    hemisphere1_title = listings[0]["hemisphere_image_urls"][0]["title"]
    img1 = listings[0]["hemisphere_image_urls"][0]["img_url"]
    hemisphere1_image = f'https://marshemispheres.com/{img1}'
    hemisphere2_title = listings[0]["hemisphere_image_urls"][1]["title"]
    img2 = listings[0]["hemisphere_image_urls"][1]["img_url"]
    hemisphere2_image = f'https://marshemispheres.com/{img2}'
    hemisphere3_title = listings[0]["hemisphere_image_urls"][2]["title"]
    img3 = listings[0]["hemisphere_image_urls"][2]["img_url"]
    hemisphere3_image = f'https://marshemispheres.com/{img3}'
    hemisphere4_title = listings[0]["hemisphere_image_urls"][3]["title"]
    img4 = listings[0]["hemisphere_image_urls"][3]["img_url"]
    hemisphere4_image = f'https://marshemispheres.com/{img4}'

    return render_template("index.html", 
        article_title = article_title, 
        article_text = article_text,
        spaceimages_url = spaceimages_url,
        mars_facts = mars_facts,
        hemisphere1_title = hemisphere1_title,
        hemisphere1_image = hemisphere1_image,
        hemisphere2_title = hemisphere2_title,
        hemisphere2_image = hemisphere2_image,
        hemisphere3_title = hemisphere3_title,
        hemisphere3_image = hemisphere3_image,
        hemisphere4_title = hemisphere4_title,
        hemisphere4_image = hemisphere4_image)

@app.route("/scrape")
def scraper():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless = False)
    listings = mongo.db.listings
    listings_data = scrape(browser)
    listings.update({}, listings_data, upsert=True)
    browser.quit()

    return redirect("/", code=302)


def scrape(browser):
    scrape_dict = {}


    url = "https://redplanetscience.com/"
    browser.visit(url)
    html = browser.html
    soup = bs(html, "html.parser")
    title = soup.find_all("div", class_ = "content_title")[0].get_text()
    paragraph = soup.find_all("div", class_ = "article_teaser_body")[0].get_text()
    # browser.quit()
    # print(title)
    # print(paragraph)
    red_planet_dict={}
    red_planet_dict['title']=title
    red_planet_dict['paragraph']=paragraph
    scrape_dict['redplanet_scrape'] = red_planet_dict

    # executable_path = {'executable_path': ChromeDriverManager().install()}
    # browser = Browser('chrome', **executable_path, headless = False)

    url = "https://spaceimages-mars.com/"
    #print(url)
    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = bs(html, "html.parser")
    image_url = soup.find(class_ = "headerimage")["src"]
    #print(image_url)
    # browser.quit()
    featured_image_url = url+image_url
    # print(featured_image_url)
    scrape_dict['spaceimages_url']= featured_image_url

    url = "https://galaxyfacts-mars.com/"
    dfs = pd.read_html(url)
    # print(len(dfs))
    mars_data = dfs[0]
    # print(mars_data)

    html_mars_data = mars_data.to_html()
    # print(html_mars_data)
    scrape_dict['mars_data']=html_mars_data

    # executable_path = {'executable_path': ChromeDriverManager().install()}
    # browser = Browser('chrome', **executable_path, headless = False)

    url = "https://marshemispheres.com/"
    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = bs(html, "html.parser")
    items = soup.find_all("div", class_ = "item")
    hemisphere_image_urls = []

    for item in items:
        hemisphere_dict = {}
        hemisphere = item.find("div", class_ = "description").find("a").get_text().rsplit(' ', 1)[0]
        href = item.find("div", class_ = "description").find("a")["href"]
        full_url = url+href
        # print(full_url)
        browser.visit(full_url)
        time.sleep(1)
        html_item = browser.html

        soup_item = bs(html_item, "html.parser")
        image_url = soup_item.find(class_ = "wide-image")["src"]
        hemisphere_dict["title"] = hemisphere
        hemisphere_dict["img_url"] = image_url
        hemisphere_image_urls.append(hemisphere_dict)

    
    # print(hemisphere_image_urls)
    scrape_dict["hemisphere_image_urls"]=hemisphere_image_urls
    return scrape_dict


if __name__ == "__main__":
    app.run(debug=True)