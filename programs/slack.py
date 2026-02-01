import os
import requests
from .config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID

def post_to_slack(text, image_path):
    print("Step 5: Slack投稿...")
    
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        print("⚠️ Slack設定不足 (環境変数を確認してください)")
        return

    url = "https://slack.com/api/files.upload"
    
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                res = requests.post(
                    url, 
                    files={'file': f}, 
                    data={
                        'channels': SLACK_CHANNEL_ID, 
                        'initial_comment': text, 
                        'title': "Today's News"
                    },
                    headers={'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
                )
        else:
            requests.post(
                "https://slack.com/api/chat.postMessage",
                json={'channel': SLACK_CHANNEL_ID, 'text': text},
                headers={'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
            )
        print("✅ 完了")
        
    except Exception as e:
        print(f"❌ Slack Error: {e}")