import asyncio

from db.postgres_db import PostgresDBClient
from utils.logger import logger
import yfinance as yf
from dotenv import load_dotenv
import os

class StockDataScraper:
    def __init__(self):
        self.db_client = self.initialize_db_client()
        self.db_available = True
        try:
            # Attempt a connection early; mark unavailable if it fails
            self.db_client.connect()
        except Exception as _:
            self.db_available = False
            logger.warning("PostgreSQL unavailable; stock data will not be persisted.")

    @staticmethod
    def initialize_db_client():
        """
        Initialize the PostgresDBClient using .env credentials.
        """
        load_dotenv()  # Load environment variables
        user = os.getenv("POSTGRES_USERNAME")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT", 5432)  # Default to 5432
        db_name = os.getenv("POSTGRES_DB")

        return PostgresDBClient(
            host=host,
            database=db_name,
            user=user,
            password=password,
            port=port,
        )

    def fetch_stock_data_sync(self, ticker, period='1mo'):
        """
        Synchronously fetches historical stock data for a given ticker.
        """
        ticker_data = yf.Ticker(ticker)
        return ticker_data.history(period=period)

    def _ensure_table_exists(self):
        ddl = (
            """
            CREATE TABLE IF NOT EXISTS stock_data (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) NOT NULL,
                date DATE NOT NULL,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume BIGINT
            );
            """
        )
        try:
            self.db_client.execute_query(ddl)
        except Exception as e:
            logger.error(f"Error ensuring stock_data table exists: {e}")
            raise

    def insert_data_into_db(self, ticker, historical_data):
        """
        Inserts historical stock data for a given ticker into the database using PostgresDBClient.
        """
        if not self.db_available:
            logger.info(f"Skipping DB insert for {ticker}: PostgreSQL unavailable.")
            return
        try:
            # Create table if missing
            self._ensure_table_exists()
            for date, row in historical_data.iterrows():
                # Normalize numpy/pandas types to native Python types for psycopg2
                data = {
                    "ticker": str(ticker),
                    "date": date.date(),
                    "open": float(row["Open"]) if row.get("Open") is not None else None,
                    "high": float(row["High"]) if row.get("High") is not None else None,
                    "low": float(row["Low"]) if row.get("Low") is not None else None,
                    "close": float(row["Close"]) if row.get("Close") is not None else None,
                    "volume": int(row["Volume"]) if row.get("Volume") is not None else None,
                }
                self.db_client.create("stock_data", data)
            logger.info(f"Data for {ticker} successfully inserted into the database.")
        except Exception as e:
            logger.error(f"Error inserting data for {ticker}: {e}")
            raise

    # Backwards-compatible alias for tests
    def insert_data_into_db_sync(self, ticker, historical_data):
        return self.insert_data_into_db(ticker, historical_data)

    def scrape_all_tickers(self, tickers):
        """
        Fetches and stores stock data for all tickers.
        """
        for ticker in tickers:
            try:
                logger.info(f"Scraping data for {ticker}...")
                historical_data = self.fetch_stock_data_sync(ticker)
                # Use sync alias for test compatibility
                self.insert_data_into_db_sync(ticker, historical_data)
            except Exception as e:
                logger.error(f"Error scraping data for {ticker}: {e}")

# Example usage
if __name__ == "__main__":
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

    scraper = StockDataScraper()
    scraper.scrape_all_tickers(nifty_50_tickers)
