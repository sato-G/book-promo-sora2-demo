#!/usr/bin/env python3
"""
Sora2 API動作確認スクリプト

ローカル環境でSora2の動作を確認
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_sora2_simple():
    """シンプルなプロンプトでテスト"""
    print("=" * 60)
    print("Test 1: シンプルな英語プロンプト（4秒）")
    print("=" * 60)

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    prompt = "A cat playing with a ball of yarn."

    print(f"Prompt: {prompt}")
    print("Generating video...")

    try:
        video = client.videos.create_and_poll(
            model="sora-2",
            prompt=prompt,
            seconds="4",
            size="1280x720"
        )

        print(f"✓ Success! Video ID: {video.id}")

        # ダウンロード
        print("Downloading...")
        content = client.videos.download_content(video.id)

        output_path = "test_simple.mp4"
        with open(output_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)

        print(f"✓ Saved to: {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sora2_japanese_narration():
    """日本語ナレーション付きプロンプトでテスト"""
    print("\n" + "=" * 60)
    print("Test 2: 日本語ナレーション付き（12秒）")
    print("=" * 60)

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # 参考記事のフォーマットを使用
    prompt = """Book promotional video, 12 seconds, cinematic style, 16:9.
Japanese voice-over with background music.

Voice-over (Japanese): この物語は、一人の少年が冒険に出る話です。彼は勇気を持って、未知の世界へと旅立ちます。"""

    print(f"Prompt:\n{prompt}\n")
    print("Generating video...")

    try:
        video = client.videos.create_and_poll(
            model="sora-2",
            prompt=prompt,
            seconds="12",
            size="1280x720"
        )

        print(f"✓ Success! Video ID: {video.id}")

        # ダウンロード
        print("Downloading...")
        content = client.videos.download_content(video.id)

        output_path = "test_japanese.mp4"
        with open(output_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)

        print(f"✓ Saved to: {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sora2_short_japanese():
    """短い日本語ナレーション（70文字程度）"""
    print("\n" + "=" * 60)
    print("Test 3: 短い日本語ナレーション70文字（12秒）")
    print("=" * 60)

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # 70文字のナレーション
    narration = "ボクシング界の怪物、井上尚弥。彼の強さの秘密は、圧倒的なスピードとパワー、そして冷静な戦略性にある。"

    prompt = f"""Book promo video for 'Monster'. 12s, cinematic, 16:9. Japanese voice-over with BGM.

Narration: {narration}"""

    print(f"Narration: {narration} ({len(narration)}文字)")
    print(f"\nPrompt:\n{prompt}\n")
    print("Generating video...")

    try:
        video = client.videos.create_and_poll(
            model="sora-2",
            prompt=prompt,
            seconds="12",
            size="1280x720"
        )

        print(f"✓ Success! Video ID: {video.id}")

        # ダウンロード
        print("Downloading...")
        content = client.videos.download_content(video.id)

        output_path = "test_70chars.mp4"
        with open(output_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)

        print(f"✓ Saved to: {output_path}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == '__main__':
    print("Sora2 API テスト開始\n")

    # APIキー確認
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("✗ Error: OPENAI_API_KEY not found in .env")
        exit(1)

    print(f"API Key: {api_key[:20]}...")
    print()

    # Test 1: シンプル
    result1 = test_sora2_simple()

    if result1:
        # Test 2: 日本語ナレーション
        result2 = test_sora2_japanese_narration()

        if result2:
            # Test 3: 70文字
            test_sora2_short_japanese()

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)
