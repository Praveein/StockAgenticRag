from scraper.news_scraper import NewsScraper
from unittest.mock import patch, MagicMock

@patch("scraper.news_scraper.requests.get")
@patch("scraper.news_scraper.MongoDBClient.insert_many")
def test_scrape_articles(mock_insert, mock_get):
    mock_response = MagicMock()
    mock_response.text = """
    <div class="NewsArticle">
        <h4 class="s-title">Test Headline</h4>
        <span class="s-source">Test Source</span>
        <span class="s-time">1 hour ago</span>
        <p class="s-desc">Test Description</p>
        <a href="/r/_ylt=AwrKBIIy1zFm_EwY6NVXNyoA;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1733089140/RO=10/RU=https://finance.yahoo.com/news/apple-intelligence-everything-know-apples-200000854.html/RK=2/RS=bY_H.p.r.y_g.Q">Link</a>
    </div>
    """
    mock_get.return_value = mock_response
    scraper = NewsScraper(collection_name="test_collection", scrape_num_articles=1)
    articles = scraper.scrape_articles("AAPL")
    assert len(articles) == 1
    assert articles[0]["headline"] == "Test Headline"
    assert articles[0]["source"] == "Test Source"
    mock_insert.assert_called_once()
