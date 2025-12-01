import os
import re
import requests
from time import sleep
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from db.mongo_db import MongoDBClient
from scraper.generic_scraper import GenericScraper
from utils.logger import logger

class NewsScraper(GenericScraper):
    def __init__(self, collection_name, scrape_num_articles=1):
        """
        Initialize the NewsScraper with necessary parameters.
        """
        self.headers    = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://www.google.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.44'
        }

        self.collection_name        = collection_name
        self.scrape_num_articles    = scrape_num_articles
        self.mongo_client           = MongoDBClient()


    @staticmethod
    def extract_article(card):
        """
        Extract article information from the raw HTML.
        """
        try:
            headline = card.find('h4', 's-title').text
        except AttributeError:
            headline = card.find('h3').text if card.find('h3') else "No Headline"

        try:
            source = card.find("span", 's-source').text
        except AttributeError:
            source = "Yahoo Finance"

        try:
            posted = card.find('span', 's-time').text.replace('·', '').strip()
        except AttributeError:
            posted = "Unknown"

        try:
            description = card.find('p', 's-desc').text.strip()
        except AttributeError:
            description = headline

        try:
            raw_link = card.find('a').get('href')
            unquoted_link = requests.utils.unquote(raw_link)
            pattern = re.compile(r'RU=(.+)\/RK')
            match = re.search(pattern, unquoted_link)
            clean_link = match.group(1) if match else unquoted_link
        except AttributeError:
            clean_link = "No Link"

        return {
            'headline': headline,
            'source': source,
            'posted': posted,
            'description': description,
            'link': clean_link,
            'synced': False
        }

    def scrape_articles(self, search_query):
        """
        Scrape news articles for a specific search query using Google News RSS.
        """
        url = f'https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en'
        articles = []
        
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            
            for item in items[:self.scrape_num_articles]:
                article = {
                    'headline': item.title.text,
                    'source': item.source.text if item.source else "Google News",
                    'posted': item.pubDate.text if item.pubDate else "Unknown",
                    'description': item.description.text if item.description else item.title.text,
                    'link': item.link.text,
                    'synced': False
                }
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error scraping Google News RSS: {e}")

        # Insert articles into MongoDB
        if articles:
            self.mongo_client.insert_many(self.collection_name, articles)
            logger.info(f"Inserted {len(articles)} articles into MongoDB.")

        return articles

    def scrape_all_tickers(self, tickers):
        """
        Scrape news articles for a list of tickers.
        """
        for ticker in tickers:
            logger.info(f"Scraping news for ticker: {ticker}")
            try:
                self.scrape_articles(ticker)
            except Exception as e:
                logger.error(f"Error while scraping news for {ticker}: {e}")


if __name__ == "__main__":

    # Initialize the scraper
    scraper = NewsScraper(
        collection_name = os.getenv("COLLECTION_NAME"),
        scrape_num_articles = int(os.getenv("SCRAPE_NUM_ARTICLES", 1))
    )

    # List of tickers to scrape
    nifty_50_tickers = [
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
        "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BHARTIARTL.NS", "BPCL.NS",
        "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
        "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
        "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS",
        "INFY.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", "MARUTI.NS",
        "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS",
        "SBIN.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SUNPHARMA.NS", "TATACONSUM.NS",
        "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS",
        "WIPRO.NS"
    ]

    # Scrape all tickers
    scraper.scrape_all_tickers(nifty_50_tickers)
