import yfinance as yf

def fetch_commodity_prices(ticker: str, start_year: int):
    print(f"Connecting to Yahoo Finance API for ticker: {ticker}...")
    
    # Define time window
    start_date = f"{start_year}-01-01"
    end_date = f"{start_year}-12-31"
    
    # Fetch data
    ticker_data = yf.Ticker(ticker)
    df = ticker_data.history(start=start_date, end=end_date)
    
    records = []
    for date, row in df.iterrows():
        records.append({
            'date': date.strftime('%Y-%m-%d'),
            'close_price': round(row['Close'], 2),
            'volume': int(row['Volume'])
        })
        
    print(f"Retrieved {len(records)} records for {ticker}.")
    return records