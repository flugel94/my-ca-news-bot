import json
import re
from google.genai import types
from .config import client, RESEARCH_MODEL

def analyze_articles(articles):
    if not articles: return []
    print("Step 2: AI分析中...")
    
    list_text = "\n".join([f"ID:{a['id']} | [{a['source']}] {a['title']}" for a in articles])
    
    # ★ご指定のプロンプト＋カテゴリ分類指示★
    prompt = f"""
    【ロール】
    あなたはCyberAgentの新入社員の教育担当者です。
    日本全体の動向や、CAに関わる事業領域、AIについての最新情報を端的にまとめ、
    新入社員に有意義な情報として伝え、ビジネスマンとしての成長を促します。

    【記事リスト】
    {list_text}

    【遵守事項】
    - タイトル・サマリーと乖離した内容（幻覚）を書くことは厳禁です。
    - **全記事を評価してください**（スレッドでの一覧表示のため）。

    【採点基準 (辛口デフレ版)】
    1. **0~4.9点 (除外)**: 通常のニュース、ゴシップ。「ふーん」で終わるレベル。
    2. **5.0~7.5点 (良記事)**: 現場で議論のネタになるレベル。
    3. **7.6~8.9点 (重要)**: CAの事業戦略に即座に影響を与えるもの。
    4. **9.0点以上 (激震)**: 経営に関わる特大ニュース。

    【CA事業タグ】
    - #Media, #AdTech, #Game, #AI_Lab, #Startup (関連薄ければnull)

    【出力形式: JSON】
    リスト内の **全ての記事** について出力してください。
    また、各記事が "Japan", "AI", "CA Focus" のどのカテゴリに属するかも判定してください。
    [
      {{
        "category": "Japan", 
        "target_id": 0,
        "verification_title": "...",
        "ca_tag": "#AdTech",
        "score": 6.5,
        "reason": "...",
        "insight": "..."
      }},
      ...
    ]
    """
    
    try:
        safety = [types.SafetySetting(category=c, threshold="BLOCK_NONE") for c in [
            types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, 
            types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            types.HarmCategory.HARM_CATEGORY_HARASSMENT, 
            types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT
        ]]
        
        res = client.models.generate_content(
            model=RESEARCH_MODEL, 
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=8192, temperature=0.0, safety_settings=safety)
        )
        
        raw = res.text
        if not raw: return []
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if not json_match: return []
        ai_results = json.loads(json_match.group(0))
        
        processed = []
        for res in ai_results:
            tid = res.get('target_id')
            if tid is None: continue
            original = next((a for a in articles if a["id"] == tid), None)
            if original: 
                processed.append({**res, "original": original})
        
        # スコア高い順にソート
        processed.sort(key=lambda x: x['score'], reverse=True)
        return processed
        
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        return []

# --- メイン投稿用 ---
def format_main_report(items):
    high_score = [i for i in items if i['score'] >= 5.0]
    
    if not high_score:
        return "☕️ 本日は、CA事業に直結する重要なニュースはありませんでした。（全リストはスレッドを参照）"

    max_score = high_score[0]['score']
    if max_score >= 9.0: header = "🚨 *【緊急】 CA経営に関わる重大ニュース* 🚨"
    elif max_score >= 7.6: header = "🔥 *今日のCAトレンドニュース (重要)* 🔥"
    else: header = "👀 *今日のTopics (共有事項)*"

    report = f"{header}\n\n"
    
    for item in high_score:
        tag = f" `{item.get('ca_tag')}`" if item.get('ca_tag') else ""
        icon = "⭐️" if item['score'] >= 7.6 else "topics"
        # カテゴリも表示
        cat = f"[{item.get('category', 'News')}] "
        
        report += f"{icon} {cat}*{item['original']['title']}* (Score: {item['score']}){tag}\n"
        report += f"{item['original']['url']}\n"
        report += f"> 📊 *Point*: {item['reason']}\n"
        if item.get('insight'):
            report += f"> 💡 *Insight*: {item['insight']}\n"
        report += "\n"
        
    return report

# --- スレッド返信用 ---
def format_thread_list(items):
    if not items: return None
    
    text = "📋 *本日のAI収集ニュース一覧 (全ログ)*\n\n"
    
    for item in items:
        if item['score'] >= 5.0: icon = "✅"
        else: icon = "⚪️"
        
        text += f"{icon} *[{item['score']}]* {item['original']['title']}\n"
        text += f"   Type: {item['original']['source']} | {item['original']['url']}\n"
        
        if item['score'] < 5.0:
             text += f"   (見送り理由: {item.get('reason', '-')})\n"
             
    return text