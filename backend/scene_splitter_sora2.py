#!/usr/bin/env python3
"""
シーン分割モジュール（Sora2版）

シナリオを複数のシーンに分割し、各シーンに70-80文字のナレーションを割り当てる
"""

from pathlib import Path
from typing import Dict, Any, List
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()


def split_into_scenes_for_sora2(
    scenario: Dict[str, Any],
    num_scenes: int = 3,
    chars_per_scene: int = 75
) -> List[Dict[str, Any]]:
    """
    シナリオを複数のシーンに分割（Sora2用、ナレーション70-80文字/シーン）

    Args:
        scenario: 選択されたシナリオデータ
        num_scenes: 分割するシーン数（デフォルト3）
        chars_per_scene: 1シーンあたりの文字数（デフォルト75）

    Returns:
        シーンのリスト（各シーンにナレーションと秒数を含む）
    """

    # Gemini API設定
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY環境変数が設定されていません")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    # シナリオテキスト
    summary = scenario["selected_pattern"]["summary"]
    book_name = scenario["book_name"]

    prompt = f"""
以下の書籍紹介シナリオを、{num_scenes}つのシーンに分割してください。

## 書籍名
{book_name}

## シナリオ（全文）
{summary}

---

## 重要な制約

**コンテンツ制限（必須）:**
- **実在人物名は使用不可**（公人・一般人問わず）
- 著作権キャラクターは不可
- 18歳未満向けコンテンツのみ
- 実在人物が登場する場合は「主人公」「彼」「彼女」などの代名詞に置き換える

**ナレーション文字数:**
- 各シーンのナレーションは **40～50文字** に収める
- シーン1と2は「続きがある」ように終わらせる
- シーン3のみ結末を感じさせる

**3シーン構成の設計:**
1. **シーン1（導入）**: 問題提起や設定紹介。「戦いが始まる」「旅立つ」など続きを予感させる
2. **シーン2（展開）**: 困難や葛藤。「敗北を知る」「試練に立ち向かう」など緊張感を残す
3. **シーン3（結末）**: タイトル表示を意識。「物語が動き出す」「感動の結末へ」など完結感

---

## タスク

{num_scenes}つのシーンに分割し、各シーンに以下を含めてください：

1. **scene_number**: シーン番号 (1-3)
2. **narration**: ナレーションテキスト（40～50文字、実在人物名なし）
3. **duration_seconds**: 12（固定）

## 出力形式

JSON形式で出力してください。

{{
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "導入。続きを予感させる終わり方（40-50文字）",
      "duration_seconds": 12
    }},
    {{
      "scene_number": 2,
      "narration": "展開。緊張感を残す終わり方（40-50文字）",
      "duration_seconds": 12
    }},
    {{
      "scene_number": 3,
      "narration": "結末。完結感のある終わり方（40-50文字）",
      "duration_seconds": 12
    }}
  ]
}}

**重要:**
- 各ナレーションは必ず40～50文字
- 実在人物名は絶対に使用しない
- シーン1,2は「続く...」という雰囲気を出す
"""

    print(f"  🤖 Gemini APIでシーン分割中（{num_scenes}シーン、{chars_per_scene}文字/シーン）...")
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json",
        },
    )

    result = json.loads(response.text)
    scenes = result["scenes"]

    # 文字数チェック
    for scene in scenes:
        char_count = len(scene['narration'])
        print(f"  シーン{scene['scene_number']}: {char_count}文字")

    print(f"  ✓ {len(scenes)}シーンに分割完了")

    return scenes
