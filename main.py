from programs.config import client
from programs.fetcher import fetch_rss_data
from programs.analyzer import analyze_articles, format_report
from programs.generator import generate_image
from programs.slack import post_to_slack

def main():
    # 1. クライアント確認
    if not client:
        print("❌ API_KEY が設定されていません。終了します。")
        return

    # 2. 収集
    articles = fetch_rss_data()
    if not articles:
        print("☕️ 記事がありませんでした")
        return

    # 3. 分析
    evaluated_items = analyze_articles(articles)
    
    # 4. レポート作成
    report_text = format_report(evaluated_items)
    
    # 5. 画像生成
    image_path = generate_image(evaluated_items)
    
    # 6. Slack投稿
    post_to_slack(report_text, image_path)

if __name__ == "__main__":
    main()