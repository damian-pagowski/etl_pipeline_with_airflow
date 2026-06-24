# Commodity Sentiment Data Pipeline

This project is an automated data engineering pipeline built to analyze how global news events correlate with commodity prices, specifically focusing on Gold. It extracts news summaries from Wikipedia and daily financial market records from Yahoo Finance, merges them chronologically, runs sentiment analysis on the headlines, and stores the enriched data into a PostgreSQL database orchestrated by Apache Airflow.

## Background

This project is an evolution of a college assignment completed as part of the Introductory Programming for Data Science module at Atlantic Technological University. The original project investigated the correlation between news sentiment and commodity prices using a Jupyter notebook — it included data cleaning, NLTK VADER sentiment analysis, Pearson correlation analysis, hypothesis testing, and Matplotlib visualisations.

This version focuses on the data engineering side: the notebook pipeline has been refactored into a production-style ETL pipeline orchestrated by Apache Airflow, with data persisted in PostgreSQL and the full stack containerised with Docker.

## System Architecture

The pipeline follows a standard Extract, Transform, Load structure managed by Apache Airflow:

**1. Extraction (Parallel Tasks)**
- News Scraper: Uses BeautifulSoup to parse Wikipedia's major news summary pages for the current year.
- Price Fetcher: Uses the yfinance API to retrieve raw daily close prices and trading volumes for Gold (GC=F).

**2. Transformation & Alignment**
- Chronological Merge: Combines the datasets by date. Because the stock market closes on weekends and holidays but news continues, the pipeline uses custom forward-fill logic to pair weekend news with Friday's closing market price. A backward-fill fallback handles New Year's Day boundaries gracefully.
- Text Cleaning: Uses regular expressions to strip Wikipedia citation brackets (e.g., [1], [2]) and normalises whitespace.
- Sentiment Analysis: Passes cleaned text into the VADER NLP scoring engine. VADER returns a compound sentiment score ranging from -1.0 (highly negative) to +1.0 (highly positive).

**3. Loading**
- Database Injection: Converts NumPy data types into native Python formats and batches clean tuples into PostgreSQL using an `ON CONFLICT DO NOTHING` clause to ensure idempotent runs.

## Tech Stack

- Apache Airflow 3.2.0 — pipeline orchestration
- PostgreSQL 15 — data storage
- Redis — Celery message broker
- Python 3.13 — pipeline logic
- yfinance — Yahoo Finance API wrapper
- BeautifulSoup — web scraping
- NLTK VADER — sentiment analysis
- Docker & Docker Compose — containerisation

## Directory Structure

```
commodity-sentiment-pipeline/
├── dags/
│   ├── commodity_sentiment_dag.py    # DAG definition and task dependencies
│   └── tasks/
│       ├── extract.py                # Wikipedia scraping logic
│       ├── extract_api.py            # yfinance price fetching
│       ├── transform.py              # merge, clean, sentiment analysis
│       └── load.py                   # PostgreSQL table creation and data insertion
├── docker-compose.yml                # Full stack container definitions
├── requirements.txt                  # Pipeline Python dependencies
├── .env                              # Environment variables (not committed)
├── .gitignore
└── README.md
```

## Database Schema

Table: `gold_sentiment_analysis`

| Column | Type | Description |
|---|---|---|
| id | SERIAL | Auto-incrementing unique identifier |
| date | DATE | Date of the news and market record |
| headline | TEXT | Cleaned Wikipedia headline |
| gold_close_price | NUMERIC | Gold closing price on that trading day |
| gold_volume | BIGINT | Trading volume (0 on non-market days) |
| sentiment_score | NUMERIC | VADER compound score (-1.0 to 1.0) |
| sentiment_label | VARCHAR | positive / negative / neutral |
| inserted_at | TIMESTAMP | Ingestion timestamp |

## Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM allocated to Docker
- Ports 8080 and 5433 available on your machine

## Setup & Running

**1. Clone the repository**
```bash
git clone https://github.com/damian-pagowski/commodity-sentiment-pipeline
cd commodity-sentiment-pipeline
```

**2. Create your .env file**
```bash
cp .env.example .env
```
Edit `.env` with your database credentials:
```
DB_HOST=pipeline-db
DB_NAME=sentiment_analysis_db
DB_USER=devuser
DB_PORT=5432
DB_PASSWORD=your_password
```

**3. Initialise Airflow (run once)**
```bash
docker-compose up airflow-init
```
Wait for the init container to exit with code 0 before proceeding.

**4. Start all services**
```bash
docker-compose up -d
```

**5. Access the Airflow UI**
```
URL:      http://localhost:8080
```

**6. Connect to the pipeline database (e.g. DBeaver)**
```
Host:     localhost
Port:     5433
Database: sentiment_analysis_db
Username: devuser
Password: your_password
```

## Common Commands

**Start all services:**
```bash
docker-compose up -d
```

**Stop all services (preserves data):**
```bash
docker-compose stop
```

**Stop and remove containers (preserves data volumes):**
```bash
docker-compose down
```

**Stop and remove everything including data volumes (fresh start):**
```bash
docker-compose down -v
```

**View logs for a specific service:**
```bash
docker-compose logs airflow-scheduler --follow
docker-compose logs airflow-dag-processor --follow
docker-compose logs pipeline-db --follow
```

**Restart a single service:**
```bash
docker-compose restart airflow-dag-processor
```

**Check container status:**
```bash
docker-compose ps
```

## Author

Damian Pagowski