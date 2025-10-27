#!/usr/bin/env python3
"""
シーン分割モジュール（Sora2版）

シナリオを複数のシーンに分割（元のテキストを正確に保持）
"""

from typing import Dict, Any, List

def split_into_scenes_for_sora2(
    scenario: Dict[str, Any],
    num_scenes: int = 3,
    chars_per_scene: int = 75  # 互換性のため残すが未使用
) -> List[Dict[str, Any]]:
    """
    シナリオを複数のシーンに分割（元のテキストを正確に3分割）

    Args:
        scenario: 選択されたシナリオデータ
        num_scenes: 分割するシーン数（デフォルト3）
        chars_per_scene: 1シーンあたりの文字数（未使用、互換性のため残す）

    Returns:
        シーンのリスト（各シーンにナレーションと秒数を含む）
    """

    # シナリオテキスト
    summary = scenario["selected_pattern"]["summary"]

    print(f"  📝 元のシナリオ: {len(summary)}文字")
    print(f"  ✂️ {num_scenes}シーンに分割中...")

    # テキストをクリーニング（改行・空白を整理）
    text = summary.replace('\n', '').strip()

    # 文で分割（。で区切る）
    sentences = [s.strip() + '。' for s in text.split('。') if s.strip()]

    print(f"  📄 文の数: {len(sentences)}")

    # 3シーンに分割（文単位で切りの良いところで分ける）
    total_sentences = len(sentences)

    if total_sentences >= 3:
        # 文の数を3で分割
        part_size = total_sentences // num_scenes

        # シーン1: 最初の1/3
        scene1_sentences = sentences[:part_size]
        # シーン2: 次の1/3
        scene2_sentences = sentences[part_size:part_size*2]
        # シーン3: 残り全て
        scene3_sentences = sentences[part_size*2:]
    else:
        # 文が3つ未満の場合は、できるだけ均等に分ける
        scene1_sentences = [sentences[0]] if len(sentences) > 0 else []
        scene2_sentences = [sentences[1]] if len(sentences) > 1 else []
        scene3_sentences = sentences[2:] if len(sentences) > 2 else []

    # 各シーンのナレーションを作成
    scenes = [
        {
            "scene_number": 1,
            "narration": ''.join(scene1_sentences),
            "duration_seconds": 12
        },
        {
            "scene_number": 2,
            "narration": ''.join(scene2_sentences),
            "duration_seconds": 12
        },
        {
            "scene_number": 3,
            "narration": ''.join(scene3_sentences),
            "duration_seconds": 12
        }
    ]

    # 文字数チェック
    for scene in scenes:
        char_count = len(scene['narration'])
        print(f"  シーン{scene['scene_number']}: {char_count}文字 - {scene['narration'][:30]}...")

    print(f"  ✓ {len(scenes)}シーンに分割完了（元のテキストを正確に保持）")

    return scenes
