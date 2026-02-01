import requests
import feedparser
import datetime
from .config import ALL_SOURCES

def is_within_target_period(entry):
    published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
    if not published_parsed: return True
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        pub_dt = datetime.datetime(*published_parsed[:6], tzinfo=datetime.timezone.utc)
        # 24時間以内
        return (now - pub_dt) <= datetime.timedelta(hours=24)
    except: return True

def fetch_rss_data():
    print("Step 1: RSS取得中 (24時間以内)...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    articles = []
    seen_links = set()
    
    for src in ALL_SOURCES:
        try:
            res = requests.get(src['url'], headers=headers, timeout=10)
            if res.status_code != 200: continue
            feed = feedparser.parse(res.content)
            
            for entry in feed.entries[:5]:
                if entry.link in seen_links: continue
                if not is_within_target_period(entry): continue
                
                summary = entry.get('summary', '') or entry.get('description', '')
                articles.append({
                    "id": len(articles),
                    "source": src['type'], 
                    "title": entry.title,
                    "url": entry.link,
                    "summary": summary[:150]
                })
                seen_links.add(entry.link)
        except Exception: continue
        
    print(f"✅ 取得記事数: {len(articles)} 件")
    return articles