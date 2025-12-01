from scraper.news_scraper import NewsScraper
import os
from dotenv import load_dotenv

load_dotenv()

def test_scrape():
    print("🕷️ Starting Test Scrape...")
    collection = os.getenv("COLLECTION_NAME", "news_articles")
    print(f"   Target Collection: {collection}")
    
    scraper = NewsScraper(collection_name=collection, scrape_num_articles=1)
    
    ticker = "AAPL"
    print(f"   Scraping {ticker}...")
    try:
        articles = scraper.scrape_articles(ticker)
        print(f"   ✅ Found {len(articles)} articles.")
        for a in articles[:2]:
            print(f"      - {a['headline']} ({a['link']})")
    except Exception as e:
        print(f"   ❌ Scrape failed: {e}")

if __name__ == "__main__":
    test_scrape()
