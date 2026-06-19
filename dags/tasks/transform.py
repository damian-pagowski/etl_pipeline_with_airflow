import numpy as np
import nltk
import re

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure the VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)
    
def merge_datasets(news_data, price_data):
    """
    merges news headlines and market prices.
    Handles standard weekends via forward-filling, and the New Year's 'Day 1' edge case via backward-filling
    """
    print(f"Starting Edge-Case Aware Merge: {len(news_data)} headlines, {len(price_data)} prices.")
    
    price_map = {row['date']: row for row in price_data}
    all_dates = sorted(list(set(list(price_map.keys()) + [article['date'] for article in news_data])))
    
    sorted_prices = sorted(price_data, key=lambda x: x['date'])
    first_available_price = sorted_prices[0] if sorted_prices else None
    
    continuous_market_calendar = {}
    active_market_track = None  
    
    for current_date in all_dates:
        if current_date in price_map:
            active_market_track = price_map[current_date]        
        if active_market_track is None:
            continuous_market_calendar[current_date] = first_available_price
            continuous_market_calendar[current_date]['is_bfill'] = True 
        else:
            continuous_market_calendar[current_date] = active_market_track
            continuous_market_calendar[current_date]['is_bfill'] = False

    combined_records = []
    for article in news_data:
        date = article['date']
        market_state = continuous_market_calendar.get(date)
        
        if market_state:
            is_fallback = (date != market_state['date'])
            is_bfill = market_state.get('is_bfill', False)            
            if is_bfill:
                match_type = 'backward_fill_new_year'
            elif is_fallback:
                match_type = 'forward_fill_weekend'
            else:
                match_type = 'exact_trading_day'
                
            combined_records.append({
                'date': date,
                'headline': article['headline'].strip(),
                'gold_close_price': market_state['close_price'],
                'gold_volume': 0 if is_fallback else market_state['volume'],
                'data_match_type': match_type
            })
            
    print(f"Merged. Generated {len(combined_records)} rows.")
    return combined_records

def analyze_vader_sentiment(merged_data):
    """
    A separate, dedicated function that accepts the merged dataset,
    calculates VADER sentiment metrics, and structures the final rows.
    """
    print(f"Starting Sentiment Analysis Task: Processing {len(merged_data)} rows.")
    analyzer = SentimentIntensityAnalyzer()
    analyzed_records = []
    
    # RELEVANT_KEYWORDS = [
    #     'gold', 'silver', 'commodity', 'market', 'price', 'trade', 'inflation', 
    #     'tariff', 'bank', 'fed', 'reserve', 'economy', 'economic', 'dollar', 
    #     'currency', 'oil', 'stocks', 'crisis', 'sanction', 'war', 'deal', 'supply'
    # ]
    
    for row in merged_data:
        headline = row['headline']
        
        clean_headline = headline.replace('\n', ' ').strip()
        clean_headline = re.sub(r'\[\s*\d+\s*\]', '', clean_headline)        
        clean_headline = re.sub(r'\s+', ' ', clean_headline).strip()
        
        if not clean_headline or len(clean_headline) < 5:
            continue
        headline_lower = clean_headline.lower()
        # is_relevant = any(keyword in headline_lower for keyword in RELEVANT_KEYWORDS)
        # if not is_relevant:
        #     continue
            
        scores = analyzer.polarity_scores(clean_headline)
        compound_score = scores['compound']
        
        clean_price = float(row['gold_close_price'])
        clean_volume = int(row['gold_volume'])
        clean_sentiment = float(compound_score)
        
        analyzed_records.append({
            'date': row['date'],
            'headline': clean_headline,
            # 'gold_close_price': row['gold_close_price'],
            'gold_close_price': clean_price,
            # 'gold_volume': row['gold_volume'],
            'gold_volume': clean_volume,
            # 'sentiment_score': compound_score,
            'sentiment_score': clean_sentiment,
            'sentiment_label': 'positive' if compound_score >= 0.05 else ('negative' if compound_score <= -0.05 else 'neutral')
        })
        
    print(f"Sentiment Analysis Task completed. Enriched {len(analyzed_records)} rows.")
    return analyzed_records

if __name__ == "__main__": 
    news = [{'date': '2025-01-01', 'headline': 'Poland takes over the Presidency of the Council of the European Union , after the Hungarian presidency . [ 2 ] [ 3 ]'},
            {'date': '2025-01-01', 'headline': 'The first versions of the Popeye and Tintin characters have entered the Public domain .'},
            {'date': '2025-01-01', 'headline': 'Bulgaria and Romania completed the process of joining the Schengen Area , lifting land border controls. [ 4 ]'},
            {'date': '2025-01-01', 'headline': 'Liechtenstein becomes the 37th country to legalize same-sex marriage . [ 5 ]'},
            {'date': '2025-01-01', 'headline': 'Ukraine halts the transportation of many Russian gas supplies through the country following the expiration of a five-year transit deal, while also becoming a state party in the International Criminal Court . [ 6 ] [ 7 ]'}]
    prices = [{'date': '2025-01-02', 'close_price': np.float64(2658.9), 'volume': 1728},
            {'date': '2025-01-03', 'close_price': np.float64(2645.0), 'volume': 591},
            {'date': '2025-01-06', 'close_price': np.float64(2638.4), 'volume': 960},
            {'date': '2025-01-07', 'close_price': np.float64(2656.7), 'volume': 643},
            {'date': '2025-01-08', 'close_price': np.float64(2664.5), 'volume': 999}]
    result =  merge_datasets(news, prices)
    result_with_scores = analyze_vader_sentiment(result)
    
    print(result_with_scores)

