#!/usr/bin/env python3
"""
Sora2プロンプトエンジニアリングモジュール

書籍情報とシナリオから最適なSora2プロンプトを生成
sample_sora.pyのプロンプト構造を参考に、詳細なシーン構成を生成
"""

from typing import Dict, Any, Optional


# グローバルスタイル定義（sample_sora.pyと同様）
GLOBAL_STYLE = (
    "Cinematic, high quality, professional. "
    "Slow, deliberate camera moves; no jitter, no fast zooms, no jump cuts. "
    "Clean subject silhouette, gentle filmic contrast, subtle grain. "
    "Crisp motion, minimal motion blur."
)


def create_sora2_prompt(
    scenario: Dict[str, Any],
    aspect_ratio: str = "16:9",
    visual_style: str = "Photorealistic",
    duration: int = 10,
    part: Optional[int] = None,
    total_parts: int = 1,
    narration_text: Optional[str] = None
) -> str:
    """
    シナリオからSora2用の動画生成プロンプトを作成（シンプル版）

    Args:
        scenario: シナリオ情報
            - book_name: 書籍名
            - selected_pattern: 選択されたパターン
            - summary: プロモーションシナリオ
        aspect_ratio: アスペクト比
        visual_style: ビジュアルスタイル
        duration: 動画の長さ（秒）
        part: パート番号（2分割の場合: 1 or 2）
        total_parts: 総パート数（デフォルト1、2分割の場合は2）
        narration_text: ナレーションテキスト（日本語可）

    Returns:
        Sora2プロンプト
    """
    book_name = scenario.get('book_name', '書籍')
    pattern = scenario.get('selected_pattern', {})

    # ナレーションテキストを使用（指定がなければデフォルトのsummary）
    if narration_text:
        summary = narration_text
    else:
        summary = pattern.get('summary', '')

    # ナレーションを削除して連続したテキストにする
    summary_cleaned = summary.replace('\n', '').replace('\r', '')

    # ビジュアルスタイルに応じたスタイル記述
    style_map = {
        "Photorealistic": "photorealistic, cinematic",
        "Picture book": "illustrated picture book style",
        "3D cartoon": "3D cartoon style",
        "Retro comics": "retro comic book style",
        "Anime": "2D anime style",
        "Pixel art": "pixel art style",
        "Cinematic": "cinematic film production",
        "Hyper cartoon": "hyper-expressive cartoon",
        "Illustration": "illustration style",
        "Dreamtale": "dreamlike, surreal",
        "Skytale": "skytale style",
        "80s film": "1980s film aesthetic",
        "Minimalist": "minimalist design",
        "Horror": "horror atmosphere",
        "Sketchbook": "sketchbook style"
    }

    style_desc = style_map.get(visual_style, "professional")

    # シンプルなプロンプト構築
    if total_parts > 1 and part is not None:
        # マルチパート生成の場合
        prompt = (
            f"Create a {duration}-second book promotional video for '{book_name}' (Part {part}/{total_parts}). "
            f"Style: {style_desc}. Aspect ratio: {aspect_ratio}. "
            f"Cinematic, professional quality. Smooth camera movements. "
            f"No real person's identifiable face; use symbolic/abstract representations. "
            f"Audio: Generate Japanese voice-over with natural emotive voice. Add subtle cinematic BGM. "
            f"Duck BGM under voice by ~8 dB.\n\n"
            f"Voice-over (Japanese): {summary_cleaned}"
        )
    else:
        # 単一動画の場合
        prompt = (
            f"Create a {duration}-second book promotional video for '{book_name}'. "
            f"Style: {style_desc}. Aspect ratio: {aspect_ratio}. "
            f"Cinematic, professional quality. Smooth camera movements. "
            f"No real person's identifiable face; use symbolic/abstract representations. "
            f"Audio: Generate Japanese voice-over with natural emotive voice. Add subtle cinematic BGM. "
            f"Duck BGM under voice by ~8 dB.\n\n"
            f"Voice-over (Japanese): {summary_cleaned}"
        )

    return prompt


def create_scene_prompt_for_sora2(
    book_name: str,
    scene_narration: str,
    visual_style: str = "Photorealistic",
    aspect_ratio: str = "16:9",
    duration: int = 12,
    scene_number: int = 1,
    total_scenes: int = 3
) -> str:
    """
    シーン単位のSora2プロンプトを作成（テスト成功パターン厳守）

    重要な制限事項:
    - 実在人物名は使用不可（公人も含む）
    - 著作権キャラクター・音楽は不可
    - 18歳未満向けコンテンツのみ
    - ナレーションは元のシナリオテキストをそのまま使用

    Args:
        book_name: 書籍名（実在人物名を含まない）
        scene_narration: シーンのナレーション（元のシナリオから分割）
        visual_style: ビジュアルスタイル
        aspect_ratio: アスペクト比
        duration: 動画の長さ（秒、通常12）
        scene_number: シーン番号（1-3）
        total_scenes: 総シーン数（デフォルト3）

    Returns:
        Sora2プロンプト
    """
    # ビジュアルスタイルをSora2が理解できる形式に変換
    style_map = {
        "Photorealistic": "photorealistic cinematic",
        "Picture book": "illustrated picture book",
        "3D cartoon": "3D animated",
        "Retro comics": "retro comic book",
        "Anime": "anime",
        "Pixel art": "pixel art",
        "Cinematic": "cinematic",
        "Hyper cartoon": "expressive cartoon",
        "Illustration": "illustrated",
        "Dreamtale": "dreamlike",
        "Skytale": "atmospheric",
        "80s film": "1980s film",
        "Minimalist": "minimalist",
        "Horror": "dark atmospheric",
        "Sketchbook": "sketchy artistic"
    }

    style_desc = style_map.get(visual_style, "cinematic")
    narration_cleaned = scene_narration.replace('\n', '').replace('\r', '')

    # test_sora2.py Test 2の成功パターンを使用
    # アスペクト比とビジュアルスタイルを反映
    prompt = f"""Book promotional video, {duration} seconds, {style_desc} style, {aspect_ratio}.
Japanese voice-over with background music.

Voice-over (Japanese): {narration_cleaned}"""

    return prompt


def create_simple_prompt(
    book_name: str,
    summary: str,
    visual_style: str = "Photorealistic"
) -> str:
    """
    シンプルなプロンプトを生成（最小限の情報）

    Args:
        book_name: 書籍名
        summary: 要約
        visual_style: ビジュアルスタイル

    Returns:
        シンプルなSora2プロンプト
    """
    style_map = {
        "Photorealistic": "cinematic, photorealistic",
        "Anime": "anime style",
        "Illustration": "illustrated",
        "3D Render": "3D rendered",
        "Minimalist": "minimalist"
    }

    style = style_map.get(visual_style, "professional")

    prompt = f"""A {style} promotional video for the book "{book_name}".

{summary}

Make it engaging and professional, designed to attract readers."""

    return prompt.strip()


def enhance_prompt_with_details(
    base_prompt: str,
    target_audience: str = None,
    mood: str = None,
    specific_scenes: str = None
) -> str:
    """
    ベースプロンプトに追加の詳細情報を付与

    Args:
        base_prompt: ベースプロンプト
        target_audience: ターゲット読者層
        mood: ムード・雰囲気
        specific_scenes: 特定のシーン指定

    Returns:
        拡張されたプロンプト
    """
    enhancements = []

    if target_audience:
        enhancements.append(f"Target Audience: {target_audience}")

    if mood:
        enhancements.append(f"Mood: {mood}")

    if specific_scenes:
        enhancements.append(f"Key Scenes: {specific_scenes}")

    if enhancements:
        enhanced = base_prompt + "\n\nAdditional Details:\n" + "\n".join(enhancements)
        return enhanced

    return base_prompt


def get_prompt_examples() -> Dict[str, str]:
    """
    プロンプトの例を返す（参考用）

    Returns:
        プロンプト例の辞書
    """
    return {
        "fiction": """Create a cinematic book trailer for a mystery novel.

Opening with a foggy street at night, camera slowly pans down a cobblestone alley.
Shadows move mysteriously. Quick cuts of: an old detective's office with scattered papers,
a vintage typewriter, a flickering street lamp.
Transition to close-up of a handwritten note with cryptic message.
Atmosphere: tense, mysterious, noir aesthetic.
Ending: fade to book cover reveal.""",

        "non_fiction": """Create a professional promotional video for a business/self-help book.

Opening: sunrise over a modern cityscape, symbolizing new beginnings.
Visual journey through: person reading the book in various inspiring locations,
notebook with key insights being written, people in collaborative meetings,
growth charts and success imagery.
Mood: inspiring, motivational, forward-looking.
Style: clean, modern, professional with warm tones.""",

        "children": """Create a colorful animated promotional video for a children's book.

Vibrant, playful animation style. Whimsical characters come to life from the pages.
Magical sparkles and transitions. Bright, happy colors.
Show children laughing and engaged with the story.
Mood: joyful, magical, fun.
Ending: book cover with animated elements dancing around it."""
    }
