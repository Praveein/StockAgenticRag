import streamlit as st
import requests
import pandas as pd
import base64
import altair as alt
from io import BytesIO
from PIL import Image

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Stocks Insights AI Agent", layout="wide")

st.title("📈 Stocks Insights AI Agent")

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Stock Data", "News"])

if page == "Stock Data":
    st.header("Stock Data & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol", value="RELIANCE").upper()
        st.caption("Try Indian stocks like: RELIANCE, TCS, INFY, HDFCBANK")
    
    # Tabs for different stock operations
    tab1, tab2, tab3 = st.tabs(["Price Statistics", "Charts", "Raw Data"])
    
    with tab1:
        st.subheader("Price Statistics")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            operation = st.selectbox("Operation", ["average", "highest", "lowest"])
        with c2:
            price_type = st.selectbox("Price Type", ["close", "open", "high", "low"], key="stats_price_type")
        with c3:
            duration = st.selectbox("Duration (days)", ["1", "7", "14", "30"], key="stats_duration")
            
        if st.button("Get Statistics"):
            with st.spinner("Fetching data..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/stock/{ticker}/price-stats",
                        params={
                            "operation": operation,
                            "price_type": price_type,
                            "duration": duration
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Data fetched successfully!")
                        st.json(data)
                        
                        # Display result prominently
                        if "result" in data:
                            st.info(f"Result: {data['result']}")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    with tab2:
        st.subheader("Stock Charts")
        
        c1, c2 = st.columns(2)
        with c1:
            chart_price_type = st.selectbox("Price Type", ["close", "open", "high", "low"], key="chart_price_type")
        with c2:
            chart_duration = st.selectbox("Duration (days)", ["7", "14", "30", "90"], key="chart_duration")
            
        if st.button("Generate Chart"):
            with st.spinner("Generating chart..."):
                try:
                    # Request JSON format for better interactive plotting
                    response = requests.get(
                        f"{API_BASE_URL}/stock/{ticker}/chart",
                        params={
                            "price_type": chart_price_type,
                            "duration": chart_duration,
                            "format": "json"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "series" in data:
                            # Interactive chart using Altair for better control
                            df = pd.DataFrame(data["series"])
                            if not df.empty:
                                df["date"] = pd.to_datetime(df["date"])
                                df = df.sort_values("date")
                                
                                st.subheader(f"{ticker} - {chart_price_type}")
                                
                                # Create Altair chart with dynamic scaling (zero=False)
                                chart = alt.Chart(df).mark_line(point=True).encode(
                                    x=alt.X('date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d')),
                                    y=alt.Y('value:Q', title='Price', scale=alt.Scale(zero=False)),
                                    tooltip=[
                                        alt.Tooltip('date:T', title='Date', format='%Y-%m-%d'),
                                        alt.Tooltip('value:Q', title='Price')
                                    ]
                                ).properties(
                                    height=400
                                ).interactive()
                                
                                st.altair_chart(chart, use_container_width=True)
                            else:
                                st.warning("No data available for chart.")
                        elif "image_base64" in data:
                             # Fallback to PNG if backend returns it
                            image_data = base64.b64decode(data["image_base64"])
                            image = Image.open(BytesIO(image_data))
                            st.image(image, caption=f"{ticker} {chart_price_type} ({chart_duration} days)", use_column_width=True)
                        else:
                            st.write(data)
                            
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    with tab3:
        st.subheader("Raw Historical Data")
        
        raw_duration = st.selectbox("Duration (days)", ["7", "14", "30", "90"], key="raw_duration")
        
        if st.button("Fetch Data"):
            with st.spinner("Fetching raw data..."):
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/stock/{ticker}/history",
                        params={"duration": raw_duration}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            df = pd.DataFrame(data)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.warning("No data found.")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

elif page == "News":
    st.header("📰 Stock News Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        ticker = st.text_input("Ticker Symbol", value="RELIANCE", key="news_ticker").upper()
        topic = st.text_input("Specific Topic (Optional)", placeholder="e.g., earnings, lawsuit")
        
        if st.button("Analyze News"):
            with st.spinner("Analyzing news... (this may take a moment)"):
                try:
                    params = {}
                    if topic:
                        params["topic"] = topic
                        
                    response = requests.get(
                        f"{API_BASE_URL}/news/{ticker}",
                        params=params
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state['news_result'] = data
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
    
    with col2:
        if 'news_result' in st.session_state:
            data = st.session_state['news_result']
            st.success(f"Analysis for {data.get('ticker', ticker)}")
            
            result_text = data.get("result", "No result returned.")
            st.markdown(result_text)
            
            # If there are source documents or other metadata, display them
            if "sources" in data:
                with st.expander("View Sources"):
                    st.write(data["sources"])

st.sidebar.markdown("---")
st.sidebar.info("Ensure the FastAPI backend is running on port 8000.")
