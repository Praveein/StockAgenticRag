from fastapi import APIRouter, HTTPException, Query
from rag_graphs.stock_data_rag_graph.graph.graph import app as stock_data_graph
from rag_graphs.stock_charts_graph.graph.graph import app as stock_charts_graph
router = APIRouter()
#
import io
import base64
import pandas as pd

@router.get("/{ticker}/price-stats")
def price_stats(
    ticker: str,
    operation: str  = Query(..., description="Operation to perform: 'highest', 'lowest', 'average'"),
    price_type: str = Query(..., description="Price type: 'open', 'close', 'low', 'high'"),
    duration :str   = Query(..., description="Duration (days): '1', '7', '14', '30'"),
):
    """
    Get stock price statistics for a specific ticker.

    Args:
        ticker (str): Stock ticker symbol.
        operation (str): Operation to perform (e.g., 'highest', 'lowest', 'average').
        price_type (str): Type of price (e.g., 'open', 'close', 'low', 'high').
        duration (int): Number of days

    Returns:
        dict: Stock data with the requested statistics.
    """

    try:
        human_query = f"What is the {operation} value of {price_type} for '{ticker}' over last {duration} day(s) ?"

        res         = stock_data_graph.invoke({"question": human_query})
        return {
            "ticker": ticker,
            "operation": operation,
            "price_type": price_type,
            "duration": duration,
            "result": res['generation']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/history")
def stock_history(
    ticker: str,
    duration: str = Query(..., description="Duration (days): '7', '14', '30', '90'"),
):
    """
    Get raw historical stock data.
    """
    try:
        human_query = f"Select date, open, high, low, close, volume for '{ticker}' for the last {duration} days order by date desc"
        
        # Use stock_charts_graph as it returns raw SQL results without LLM summarization
        res = stock_charts_graph.invoke({"question": human_query})
        df = res.get('sql_results')
        
        if hasattr(df, 'to_dict'):
            return df.to_dict(orient='records')
        return df
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticker}/chart")
def chart(
    ticker: str,
    price_type: str = Query(..., description="Price type: 'open', 'close', 'low', 'high'"),
    duration :str   = Query(..., description="Duration (days): '1', '7', '14', '30'"),
    format: str     = Query("json", description="Format: 'json' or 'png'"),

):
    """
    Get stock price statistics and return a histogram/chart for a specific ticker.

    Args:
        ticker (str): Stock ticker symbol.
        price_type (str): Type of price (e.g., 'open', 'close', 'low', 'high').
        duration (int): Number of days

    Returns:
        dict: Stock data with the requested statistics.
    """

    try:
        human_query = f"All unique values of 'date' and {price_type} for '{ticker}' for last {duration} day(s)"

        res = stock_charts_graph.invoke({"question": human_query})
        df = res.get('sql_results')
        try:
            import pandas as pd
            if isinstance(df, pd.DataFrame) and not df.empty:
                date_col = next((c for c in df.columns if c.lower() == 'date'), df.columns[0])
                value_col = price_type if price_type in df.columns else df.columns[-1]
                # Ensure dates are datetime objects and sorted
                df[date_col] = pd.to_datetime(df[date_col])
                df = df.sort_values(by=date_col)

                series = [
                    {"date": row[date_col].strftime('%Y-%m-%d'), "value": float(row[value_col])}
                    for _, row in df.iterrows()
                ]
                if format.lower() == "png":
                    try:
                        import matplotlib.pyplot as plt
                        import matplotlib.dates as mdates
                        import io, base64
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        
                        dates = df[date_col].tolist()
                        values = df[value_col].tolist()
                        
                        ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=4)
                        
                        ax.set_title(f"{ticker} {price_type} ({duration}d)", fontsize=12)
                        ax.set_xlabel("Date", fontsize=10)
                        ax.set_ylabel(price_type, fontsize=10)
                        
                        # Format x-axis dates
                        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                        plt.xticks(rotation=45, ha='right')
                        
                        # Add grid
                        ax.grid(True, linestyle='--', alpha=0.7)
                        
                        buf = io.BytesIO()
                        plt.tight_layout()
                        fig.savefig(buf, format='png', dpi=100)
                        buf.seek(0)
                        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
                        return {
                            "ticker": ticker,
                            "price_type": price_type,
                            "duration": duration,
                            "image_base64": img_b64
                        }
                    except Exception:
                        # Fallback to JSON if plotting fails
                        return {
                            "ticker": ticker,
                            "price_type": price_type,
                            "duration": duration,
                            "series": series
                        }
                else:
                    return {
                        "ticker": ticker,
                        "price_type": price_type,
                        "duration": duration,
                        "series": series
                    }
            else:
                return {
                    "ticker": ticker,
                    "price_type": price_type,
                    "duration": duration,
                    "result": df
                }
        except Exception:
            return {
                "ticker": ticker,
                "price_type": price_type,
                "duration": duration,
                "result": df
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
