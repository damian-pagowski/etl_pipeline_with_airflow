# Commodity Sentiment Data Pipeline

This project is a automated data engineering pipeline built to analyze how global news events correlate with commodity prices, specifically focusing on Gold. It extracts news summaries from Wikipedia and daily financial market records from Yahoo Finance, merges them chronologically, runs a text sentiment analysis, and stores the clean data into a PostgreSQL database.

## System Architecture

The pipeline follows a standard Extract, Load, Transform structure managed by Apache Airflow:

1. Extraction (Parallel Tracking)
- News Scraper: Uses BeautifulSoup to parse Wikipedia's major news summary pages for the current year.
- Price Fetcher: Uses the yfinance API to retrieve raw daily close prices and trading volumes for Gold (GC=F).

2. Transformation & Alignment
- Chronological Merge: Combines the datasets by date. Because the stock market closes on weekends and holidays but news continues, the pipeline uses a custom forward-fill logic to pair weekend news with Friday's closing market price. It also uses a backward-fill fallback to handle New Year's Day boundaries gracefully.
- Text Cleaning: Uses regular expressions to strip out typographical artifacts like Wikipedia citation brackets (e.g., [1], [2]) and normalizes whitespace characters.
- Relevance Filtering: Filters out non-commodity news rows (like sports or pop culture) by evaluating headlines against a list of macroeconomic keywords.
- Sentiment Analysis: Passes the clean, un-mutated text into the VADER NLP scoring engine. VADER evaluates the headline and returns a compound sentiment score ranging from -1.0 (highly negative) to +1.0 (highly positive).

3. Loading
- Database Injection: Converts numbers from complex NumPy data types into native Python formats to satisfy database constraints. It then batches the clean tuples into a standalone PostgreSQL database table using an upside-deduplication clause (ON CONFLICT DO NOTHING) to ensure the table stays clean if the pipeline is run repeatedly.

## Directory Structure

- dags/commodity_sentiment_dag.py: The central Airflow file defining task dependencies and the data flow graph.
- tasks/extract.py: Logic for web scraping historical data from Wikipedia.
- tasks/extract_api.py: Logic for fetching financial market information via APIs.
- tasks/transform.py: Core logic for chronological sorting, data alignment, citation stripping, text filtering, and sentiment scoring.
- tasks/load.py: Module handling database table creation, configuration setups, and data writing operations.

## Database Schema

The target PostgreSQL table `gold_sentiment_analysis` contains the following structured fields:

- id (SERIAL): Auto-incrementing unique row identifier.
- date (DATE): The tracking date of the news and market records.
- headline (TEXT): Cleaned, citation-free Wikipedia headline summary.
- gold_close_price (NUMERIC): Closing price of gold on that specific trading state.
- gold_volume (BIGINT): Trading volume (zeroed out on non-market days).
- sentiment_score (NUMERIC): The VADER compound score between -1.0 and 1.0.
- sentiment_label (VARCHAR): Text category representing positive, negative, or neutral tone.
- inserted_at (TIMESTAMP): The automatic ingestion record tracking time.