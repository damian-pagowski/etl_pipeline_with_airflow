import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_wikipedia_events(year: int) -> list:
    """
    Scrapes world events for a specific year from Wikipedia, organized by date.
    """
    url = f"https://en.wikipedia.org/wiki/{year}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Failed to load Wikipedia page for year {year}"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    records = []
    
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    for month in months:
        try:
            days_in_month = pd.Period(f"{year}-{month}", freq='M').days_in_month
        except Exception:
            continue
        for day in range(1, days_in_month + 1):
            try:
                anchor = soup.find('a', title=f"{month} {day}")
                if anchor is None:
                    continue

                parent = anchor.parent
                items = parent.find_all('li')

                for item in items:
                    text = item.get_text(separator=' ', strip=True)
                    # Clean out citation brackets like [1], [2], etc.
                    text = re.sub(r'\[\d+\]', '', text).strip()

                    if text:
                        # Create date string format YYYY-MM-DD
                        month_num = pd.Timestamp(f'{month} 1 {year}').month
                        date_str = pd.Timestamp(year=year, month=month_num, day=day).strftime('%Y-%m-%d')
                        
                        records.append({
                            'date': date_str,
                            'headline': text
                        })
            except Exception as e:
                print(f"Error scraping {month} {day}: {e}")
                continue
    print(f"Scraped {len(records)} news headers.")           
    return records