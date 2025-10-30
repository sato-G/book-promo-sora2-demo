#!/usr/bin/env python3
"""
Sora2 Image-to-Video シンプルテストスクリプト（依存関係最小）

使い方:
  python3 test_image2video_simple.py "data/AI用素材/AI用素材_1.jpg" "Camera slowly zooms in" 8

注意: 秒数は 4, 8, 12 のみサポートされています
"""

import os
import sys
import requests
import time
from pathlib import Path
from PIL import Image


def resize_image_for_sora(image_path, target_width=1280, target_height=720):
    """
    画像をSora2の要求サイズにリサイズ
    """
    img = Image.open(image_path)

    # 既に正しいサイズの場合はそのまま返す
    if img.size == (target_width, target_height):
        return image_path

    print(f"📐 画像リサイズ: {img.size} → {target_width}x{target_height}")

    # アスペクト比を保ちながらリサイズ
    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # 一時ファイルに保存
    temp_path = Path("data/output/temp_resized.jpg")
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    img_resized.save(temp_path, quality=95)

    return temp_path


def generate_video_from_image_simple(image_path, prompt, duration=8):
    """
    画像から動画を生成（シンプル版）
    """
    # 秒数のバリデーション
    if duration not in [4, 8, 12]:
        print(f"❌ 秒数は 4, 8, 12 のいずれかを指定してください（指定値: {duration}）")
        return None

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEYが設定されていません")
        return None

    image_path = Path(image_path)
    if not image_path.exists():
        print(f"❌ 画像が見つかりません: {image_path}")
        return None

    # 画像をリサイズ
    resized_image_path = resize_image_for_sora(image_path)

    # 出力ディレクトリの準備
    output_dir = Path("data/output/image2video")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    output_path = output_dir / f"video_{timestamp}.mp4"

    print("=" * 80)
    print("🎬 Sora2 Image-to-Video")
    print("=" * 80)
    print(f"📁 画像: {image_path.name}")
    print(f"📝 プロンプト: {prompt}")
    print(f"⏱️  長さ: {duration}秒")
    print()

    try:
        # APIエンドポイント
        api_url = "https://api.openai.com/v1/videos"
        headers = {"Authorization": f"Bearer {api_key}"}

        # multipart/form-dataで送信
        with open(resized_image_path, 'rb') as f:
            files = {'input_reference': (resized_image_path.name, f, 'image/jpeg')}
            data = {
                'model': 'sora-2',
                'prompt': prompt,
                'size': '1280x720',
                'seconds': str(duration)
            }

            print("📤 API呼び出し中...")
            response = requests.post(api_url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
                return None

            result = response.json()
            video_id = result.get('id')
            print(f"✓ ジョブ開始 (ID: {video_id})")

        # ポーリング
        print("⏳ 生成完了を待機中...")
        max_wait = 600
        elapsed = 0

        while elapsed < max_wait:
            status_response = requests.get(f"{api_url}/{video_id}", headers=headers)

            if status_response.status_code != 200:
                print(f"❌ Status check error: {status_response.status_code}")
                return None

            status_data = status_response.json()
            status = status_data.get('status')

            print(f"   Status: {status} ({elapsed}s)")

            if status == 'completed':
                print("✓ 生成完了！")
                break
            elif status == 'failed':
                print(f"❌ 失敗: {status_data.get('error')}")
                return None

            time.sleep(10)
            elapsed += 10

        if elapsed >= max_wait:
            print("❌ タイムアウト")
            return None

        # ダウンロード
        print("📥 ダウンロード中...")
        download_url = f"{api_url}/{video_id}/content"
        video_response = requests.get(download_url, headers=headers)

        if video_response.status_code != 200:
            print(f"❌ ダウンロードエラー: {video_response.status_code}")
            return None

        with open(output_path, 'wb') as f:
            f.write(video_response.content)

        print(f"✅ 保存完了: {output_path}")
        print("=" * 80)
        return output_path

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("使い方: python3 test_image2video_simple.py <画像パス> <プロンプト> [duration]")
        print()
        print("例:")
        print('  python3 test_image2video_simple.py "data/AI用素材/AI用素材_1.jpg" "Camera slowly zooms in" 8')
        print()
        print("利用可能な画像:")
        image_dir = Path("data/AI用素材")
        if image_dir.exists():
            for img in sorted(image_dir.glob("*.jpg")):
                print(f"  - {img}")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2]
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 8

    result = generate_video_from_image_simple(image_path, prompt, duration)

    if result:
        print(f"\n✅ 成功！動画: {result}")
    else:
        print("\n❌ 失敗しました")
        sys.exit(1)
