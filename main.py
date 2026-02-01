from programs.config import client
from programs.fetcher import fetch_rss_data
from programs.analyzer import analyze_articles, format_main_report, format_thread_list
from programs.generator import generate_image
from programs.slack import post_to_slack

def main():
    # 1. クライアント確認
    if not client:
        print("❌ API_KEY Error")
        return

    # 2. 収集 (24時間以内)
    articles = fetch_rss_data()
    if not articles:
        print("☕️ 記事がありませんでした")
        return

    # 3. 分析 (全件評価)
    evaluated_items = analyze_articles(articles)
    
    # 4. テキスト作成
    # メイン用: 重要ニュースの詳細 (画像と一緒に送るやつ)
    main_text = format_main_report(evaluated_items)
    # スレッド用: 全ニュースの簡易リスト (返信欄に送るやつ)
    thread_text = format_thread_list(evaluated_items)
    
    # 5. 画像生成
    image_path = generate_image(evaluated_items)
    
    # 6. Slack投稿 (メイン + スレッド)
    post_to_slack(main_text, image_path, thread_text)

if __name__ == "__main__":
    main()