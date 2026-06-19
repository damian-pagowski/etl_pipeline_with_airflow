import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from airflow.models.dag import DAG
from airflow.decorators import task
from datetime import datetime

from tasks.extract import scrape_wikipedia_events
from tasks.extract_api import fetch_commodity_prices
from tasks.transform import merge_datasets, analyze_vader_sentiment

default_args = {
    'owner': 'Damian Pagowski',
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    dag_id='commodity_sentiment_dag',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
    tags=['learning', 'commodities']
) as dag:

    @task(task_id='scrape_news_from_wikipedia')
    def scrape_news():
        print("Started Wikipedia scraping...")
        extracted_records = scrape_wikipedia_events(2025)
        print(f"Captured {len(extracted_records)} raw records.")
        return scrape_wikipedia_events(2025)[:5] # 5 just for testing

    @task(task_id='fetch_market_prices')
    def fetch_prices():
        # Gold ('GC=F') for the year 2025
        return fetch_commodity_prices(ticker='GC=F', start_year=2025)[:5] # 5 just for testing
    
    @task(task_id='merge_and_clean_data')
    def transform_data(news, prices):
        return merge_datasets(news, prices)
    
    @task(task_id='calculate_vader_sentiment')
    def sentiment_analysis(merged_list):
        return analyze_vader_sentiment(merged_list)
    
    raw_news = scrape_news()
    raw_prices = fetch_prices()
    clean_combined_data = transform_data(raw_news, raw_prices)
    final_analyzed_data = sentiment_analysis(clean_combined_data)

if __name__ == "__main__":    
    try:
        preview_data = scrape_news.function()
        preview_data_gold = fetch_prices.function()
        p_merged = transform_data.function(preview_data, preview_data_gold)

        print("\n---Task Ran Successfully---")
        print("Sample Data Captured:")
        # for record in preview_data:
        #     # print(f"  - Date: {record['date']} | Headline Preview: {record['headline'][:60]}...")
        #     print(record)
        # for record in preview_data_gold:
        #     # print(f"  - Date: {record['date']} | Price: {record['close_price']} | Volume: {record['volume']}")
        #     print(record)

        p_final = sentiment_analysis.function(p_merged)

        print("\n--- Local Pipeline Test Successful ---")
        print(f"Total rows produced: {len(p_final)}")
        if p_final:
            print("\nVerification Sample:")
            print(p_final[0])
            
    except Exception as e:
        print(f"\Code threw an error: {e}")
