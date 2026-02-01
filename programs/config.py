import os
from google import genai

# --- 環境変数 ---
API_KEY = os.environ.get("GEMINI_API_KEY")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

# --- 保存先設定 ---
# GitHub ActionsやLambdaでは一時ディレクトリを使用
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- モデル設定 ---
RESEARCH_MODEL = "models/gemini-3-pro-preview" 
IMAGE_MODEL = "models/gemini-3-pro-image-preview"

# --- Geminiクライアント初期化 ---
client = None
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print(f"⚠️ Client Init Error: {e}")

# --- ニュースソース ---
GENERAL_SOURCES = [
    {"url": "https://business.nikkei.com/rss/sns/nb.rdf", "type": "NikkeiBP"},
    {"url": "https://business.nikkei.com/rss/sns/nb-x.rdf", "type": "NikkeiBP"},
    {"url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml", "type": "Yahoo"},
    {"url": "https://news.yahoo.co.jp/rss/topics/business.xml", "type": "Yahoo"},
    {"url": "https://news.yahoo.co.jp/rss/topics/entertainment.xml", "type": "Yahoo_Entame"},
    {"url": "https://news.yahoo.co.jp/rss/topics/it.xml", "type": "Yahoo_IT"},
]
GLOBAL_AI_SOURCES = [
    {"url": "https://openai.com/news/rss.xml", "type": "OpenAI"},
    {"url": "https://deepmind.google/blog/rss.xml", "type": "GoogleDeepMind"}, 
    {"url": "https://feeds.feedburner.com/blogspot/gJZg", "type": "GoogleAI"},
    {"url": "https://huggingface.co/blog/feed.xml", "type": "HuggingFace"},
]
TECH_BLOG_SOURCES = [
    {"url": "https://www.ai-shift.co.jp/techblog/feed", "type": "AIShift_CA"},
    {"url": "https://medium.com/feed/@kyakuno", "type": "AX_Company"},
    {"url": "https://www.publickey1.jp/atom.xml", "type": "Publickey"},
    {"url": "https://engineering.mercari.com/blog/feed.xml", "type": "Mercari"},
    {"url": "https://blog.recruit.co.jp/data/index.xml", "type": "Recruit"},
    {"url": "https://techblog.lycorp.co.jp/ja/feed/index.xml", "type": "LINE_Yahoo"},
    {"url": "https://engineering.dena.com/index.xml", "type": "DeNA"},
    {"url": "https://engineers.ntt.com/feed", "type": "NTT_Com"},
]
ALL_SOURCES = GENERAL_SOURCES + GLOBAL_AI_SOURCES + TECH_BLOG_SOURCES