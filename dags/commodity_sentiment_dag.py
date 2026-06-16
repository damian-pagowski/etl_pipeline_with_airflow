import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from airflow.models.dag import DAG
from airflow.decorators import task
from datetime import datetime

from tasks.extract import scrape_wikipedia_events

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
        print("Starting Wikipedia scraping engine...")
        extracted_records = scrape_wikipedia_events(2025)
        print(f"Success! Captured {len(extracted_records)} raw records.")
        return extracted_records[:3]

    scraped_data_preview = scrape_news()



if __name__ == "__main__":
    print("\n--- Bypassing Airflow Internal API Sandbox for Debugging ---")
    
    try:
        preview_data = scrape_news.function()
        
        print("\n--- Task Ran Successfully Outside Airflow Core! ---")
        print("Sample Data Captured:")
        for record in preview_data:
            print(f"  - Date: {record['date']} | Headline Preview: {record['headline'][:60]}...")
            
    except Exception as e:
        print(f"\nYour Python logic threw an error: {e}")