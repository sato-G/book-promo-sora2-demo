#!/usr/bin/env python3
"""
シーン分割→Sora2生成→結合のフルフローテスト

test_sora2.pyの成功パターンに厳密に従う
3シーン作成 → 結合
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))
from backend import video_composer

load_dotenv()

# テストナレーション（3シーン、各50文字前後、架空の内容）
narrations = [
    "この物語は、一人の少年が冒険に出る話です。彼は勇気を持って、未知の世界へと旅立ちます。",  # Test 2成功パターン
    "困難な道のりの中で、少年は多くの仲間と出会い、共に成長していきます。絆の力が試される。",
    "最後の試練を乗り越えた時、少年は真のヒーローへと変わる。感動の冒険物語がここに完結する。"
]

def generate_scene_video(narration, scene_num, output_dir):
    """test_sora2.py Test 2の成功パターンを厳密に使用"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    print(f"\n{'='*60}")
    print(f"シーン {scene_num}: {narration} ({len(narration)}文字)")
    print(f"{'='*60}")

    # test_sora2.py Test 2の成功パターンを厳密にコピー
    prompt = f"""Book promotional video, 12 seconds, cinematic style, 16:9.
Japanese voice-over with background music.

Voice-over (Japanese): {narration}"""

    print(f"Prompt:\n{prompt}\n")
    print("🎬 Sora2で生成中...")

    try:
        video = client.videos.create_and_poll(
            model="sora-2",
            prompt=prompt,
            seconds="12",
            size="1280x720"
        )

        print(f"✓ 生成完了 (Video ID: {video.id})")

        # ダウンロード
        print("📥 ダウンロード中...")
        content = client.videos.download_content(video.id)

        output_path = output_dir / f"scene_{scene_num}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)

        print(f"✓ 保存: {output_path}")
        return output_path

    except Exception as e:
        print(f"✗ エラー: {e}")
        return None

def main():
    print("="*60)
    print("シーン分割→Sora2生成→結合 フルフローテスト")
    print("="*60)
    print(f"\nシーン数: {len(narrations)}")
    print(f"合計時間: {len(narrations) * 12}秒")
    print(f"合計文字数: {sum(len(n) for n in narrations)}文字")

    # 出力ディレクトリ
    output_dir = Path("test_scene_output")
    output_dir.mkdir(exist_ok=True)

    # 各シーンを生成
    scene_videos = []

    for i, narration in enumerate(narrations, 1):
        video_path = generate_scene_video(narration, i, output_dir)
        if video_path:
            scene_videos.append(video_path)
        else:
            print(f"✗ シーン {i} の生成に失敗")
            return

    print(f"\n✅ 全{len(scene_videos)}シーンの生成完了！")

    # 動画を結合
    print("\n" + "="*60)
    print("動画結合中...")
    print("="*60)

    try:
        final_video = video_composer.concatenate_videos(
            scene_videos,
            output_file=output_dir / "final_combined.mp4"
        )

        print(f"\n🎉 完成！")
        print(f"📹 最終動画: {final_video}")

        # ファイルサイズ確認
        size_mb = final_video.stat().st_size / (1024 * 1024)
        print(f"📊 ファイルサイズ: {size_mb:.2f} MB")

    except Exception as e:
        print(f"✗ 結合エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
