import os
import requests
from .config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID

def post_to_slack(main_text, image_path, thread_text=None):
    print("Step 5: Slack投稿...")
    
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        print("⚠️ Slack設定不足")
        return

    main_ts = None
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}

    # --- 1. メイン投稿 ---
    try:
        # A. 画像ありの場合
        if image_path and os.path.exists(image_path):
            url = "https://slack.com/api/files.upload"
            with open(image_path, 'rb') as f:
                res = requests.post(
                    url, 
                    files={'file': f}, 
                    data={
                        'channels': SLACK_CHANNEL_ID, 
                        'initial_comment': main_text, 
                        'title': "Daily News"
                    },
                    headers=headers
                )
            
            # 画像投稿のレスポンスからタイムスタンプ(ts)を取り出すのは少し特殊
            # file -> shares -> public -> channel_id -> [0] -> ts
            response = res.json()
            if response.get('ok'):
                file_shares = response.get('file', {}).get('shares', {}).get('public', {})
                if SLACK_CHANNEL_ID in file_shares:
                    main_ts = file_shares[SLACK_CHANNEL_ID][0]['ts']
                print("✅ メイン投稿完了 (画像)")
            else:
                print(f"❌ メイン投稿失敗: {response.get('error')}")

        # B. テキストのみの場合
        else:
            url = "https://slack.com/api/chat.postMessage"
            res = requests.post(
                url,
                json={'channel': SLACK_CHANNEL_ID, 'text': main_text},
                headers=headers
            )
            response = res.json()
            if response.get('ok'):
                main_ts = response.get('ts')
                print("✅ メイン投稿完了 (テキスト)")
            else:
                print(f"❌ メイン投稿失敗: {response.get('error')}")

        # --- 2. スレッド投稿 (全ログ) ---
        if main_ts and thread_text:
            print("   -> スレッドに詳細ログを投稿中...")
            reply_url = "https://slack.com/api/chat.postMessage"
            res_reply = requests.post(
                reply_url,
                json={
                    'channel': SLACK_CHANNEL_ID,
                    'text': thread_text,
                    'thread_ts': main_ts # 親メッセージのIDを指定
                },
                headers=headers
            )
            if res_reply.json().get('ok'):
                print("✅ スレッド投稿完了")
            else:
                print(f"❌ スレッド投稿失敗: {res_reply.json().get('error')}")

    except Exception as e:
        print(f"❌ Slack Error: {e}")