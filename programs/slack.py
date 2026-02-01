import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .config import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID

def post_to_slack(main_text, image_path, thread_text=None):
    print("Step 5: Slack投稿 (SDK版)...")
    
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        print("⚠️ Slack設定不足")
        return

    # 公式クライアントを初期化
    client = WebClient(token=SLACK_BOT_TOKEN)
    main_ts = None

    try:
        # --- A. 画像ありの場合 ---
        if image_path and os.path.exists(image_path):
            print("   -> 画像をアップロード中...")
            
            # files_upload_v2 は新しいアップロード方式に自動対応しています
            response = client.files_upload_v2(
                channel=SLACK_CHANNEL_ID,
                file=image_path,
                initial_comment=main_text,
                title="Daily News"
            )
            
            if response.get("ok"):
                # 画像メッセージのタイムスタンプ(ts)を取り出す
                file_data = response.get("file")
                shares = file_data.get("shares", {}).get("public", {})
                
                if SLACK_CHANNEL_ID in shares:
                    main_ts = shares[SLACK_CHANNEL_ID][0]['ts']
                print("✅ メイン投稿完了 (画像)")
            else:
                print(f"❌ 画像投稿失敗: {response.get('error')}")

        # --- B. テキストのみの場合 ---
        else:
            print("   -> テキストのみ投稿中...")
            response = client.chat_postMessage(
                channel=SLACK_CHANNEL_ID,
                text=main_text
            )
            if response.get("ok"):
                main_ts = response.get("ts")
                print("✅ メイン投稿完了 (テキスト)")
            else:
                print(f"❌ 投稿失敗: {response.get('error')}")

        # --- 2. スレッド投稿 (全ログ) ---
        if main_ts and thread_text:
            print("   -> スレッドにログを投稿中...")
            client.chat_postMessage(
                channel=SLACK_CHANNEL_ID,
                text=thread_text,
                thread_ts=main_ts
            )
            print("✅ スレッド投稿完了")

    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
    except Exception as e:
        print(f"❌ Slack Error: {e}")