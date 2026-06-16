from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import PythonOperator

## imports business related
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import sqlite3
import matplotlib.pyplot as plt
import nltk
import scipy.stats as stats

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
##

# 1. Define your modular pipeline tasks as standard Python functions
def extract_website_data():
    print("Executing BeautifulSoup scraping module...")
    # Your university scraping logic goes here later
    return {"status": "success", "source": "web_scraper"}

def extract_api_data():
    print("Consuming raw metrics from API endpoints...")
    # Your requests library logic goes here later
    return {"status": "success", "source": "api_client"}

def transform_and_clean():
    print("Running Pandas processing and schema validation...")
    # Your data cleaning logic goes here later
    pass

def load_to_postgres():
    print("Opening target connection pool and loading records into PostgreSQL...")
    # Your database insert logic goes here later
    pass

# 2. Define your pipeline configuration using the modern Airflow context manager
with DAG(
    dag_id="university_data_pipeline_v1",
    description="Refactored MSc Data Science ETL pipeline supporting database ingestion",
    schedule=None,              # Trigger manually from the UI for development
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "Damian",
        "retries": 2,           # Fault tolerance: retry failing scrapers automatically
        "retry_delay": timedelta(minutes=2),
    }
) as dag:

    # 3. Instantiate your execution tasks
    task_scrape = PythonOperator(
        task_id="scrape_web_source",
        python_callable=extract_website_data
    )

    task_api = PythonOperator(
        task_id="consume_api_endpoints",
        python_callable=extract_api_data
    )

    task_transform = PythonOperator(
        task_id="transform_and_clean_data",
        python_callable=transform_and_clean
    )

    task_load = PythonOperator(
        task_id="load_into_postgresql",
        python_callable=load_to_postgres
    )

    # 4. Define the execution order (Scrape and API run parallel, then transform, then load)
    [task_scrape, task_api] >> task_transform >> task_load