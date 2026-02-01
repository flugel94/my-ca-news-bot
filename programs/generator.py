import os
import datetime
from .config import client, IMAGE_MODEL, OUTPUT_DIR

def generate_image(items):
    print("Step 4: 画像生成中...")
    if not items: return None
    
    # 全体の最高スコアでヘッダーを決める
    max_score = max([i['score'] for i in items]) if items else 0
    if max_score >= 9.0:
        header_text = "🚨 【緊急】 CA経営に関わる重大ニュース 🚨"
    elif max_score >= 7.6:
        header_text = "🔥 今日のCAトレンドニュース (重要) 🔥"
    else:
        header_text = "👀 今日のTopics (共有事項)"

    # カテゴリマッピングとカード生成
    cat_map = {"Japan": "🇯🇵 Japan", "AI": "🤖 AI & Tech", "CA Focus": "🏢 CA Focus"}
    cards_content = ""

    for cat_key in ["Japan", "AI", "CA Focus"]:
        # そのカテゴリに含まれる記事の中で、最もスコアが高いものを1つ選ぶ
        # (analyzer側で category キーを出力させている前提)
        item = next((i for i in items if cat_key in i.get('category', '')), None)
        cat_name = cat_map.get(cat_key, cat_key)

        if item:
            tag_str = item.get('ca_tag', '') or ""
            source_str = f"Source: {item['original']['source']}"
            cards_content += f"""
            [Card: {cat_name}]
            Score: {item['score']}
            Title: {item['original']['title']}
            Tag: {tag_str}
            Source: {source_str}
            Explanation: {item['reason']}
            Insight: {item.get('insight', '')}
            """
        else:
            cards_content += f"""
            [Card: {cat_name}]
            (特筆すべきニュースなし)
            """

    image_prompt = f"""
    Generate an infographic slide image based on the following content.

    【役割】プロのグラフィックデザイナー。
    【作成物】インフォグラフィック風のスライドデザイン(16:9)。
    【トーン＆マナー】Amebaのデザインシステム風（親しみやすい丸み×信頼感のある幾何学）。モダンで視認性が高い。
    【カラールール】背景:極薄グレー(F6F6F6)、アクセント:明るいグリーン(82BE28)、サブ:ビビッドイエロー(F5E100)。
    【スタイル】フラットデザイン、角丸の四角形、余白多め。

    【スライド構成】
    1. Header: "{header_text}"
    2. Content: 3 cards horizontally aligned (Japan, AI, CA Focus).

    【Content Data】
    {cards_content}

    【Design Rules】
    - Use the accent color (82BE28) for card headers.
    - Show Title in bold.
    - Show Tag in a small yellow badge.
    - Visualize "Explanation" and "Insight" clearly.
    - If a card has no news, dim it out.
    - ALL TEXT MUST BE LEGIBLE IN THE IMAGE.
    """

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=image_prompt
        )

        image_data = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if image_data:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"slide_{timestamp}.png"
            path = os.path.join(OUTPUT_DIR, filename)
            
            # GitHub Actions環境用にバイナリ書き込み (Pillow不要)
            with open(path, "wb") as f: 
                f.write(image_data)
            print(f"✨ 画像保存完了: {path}")
            return path
        else:
            print("❌ 画像が生成されませんでした。")
            
    except Exception as e:
        print(f"❌ Image Error: {e}")
        
    return None