#!/usr/bin/env python3
"""
Sora2プロンプトエンジニアリングモジュール

書籍情報とシナリオから最適なSora2プロンプトを生成
"""

from typing import Dict, Any


def create_sora2_prompt(
    scenario: Dict[str, Any],
    aspect_ratio: str = "16:9",
    visual_style: str = "Photorealistic"
) -> str:
    """
    シナリオからSora2用の動画生成プロンプトを作成

    Args:
        scenario: シナリオ情報
            - book_name: 書籍名
            - selected_pattern: 選択されたパターン
            - summary: 要約
        aspect_ratio: アスペクト比
        visual_style: ビジュアルスタイル

    Returns:
        Sora2プロンプト
    """
    book_name = scenario.get('book_name', '書籍')
    pattern = scenario.get('selected_pattern', {})
    pattern_name = pattern.get('pattern_name', '標準')
    summary = pattern.get('summary', '')

    # ビジュアルスタイルの説明を生成
    style_descriptions = {
        "Photorealistic": "photorealistic, cinematic, high-quality film production",
        "Anime": "anime style, vibrant colors, Japanese animation aesthetic",
        "Illustration": "illustrated, artistic, hand-drawn aesthetic",
        "3D Render": "3D rendered, modern CGI, polished digital art",
        "Minimalist": "minimalist, clean design, simple geometric shapes"
    }

    style_desc = style_descriptions.get(visual_style, "professional, high-quality")

    # アスペクト比による構図の調整
    composition_hints = {
        "16:9": "wide cinematic composition, landscape orientation",
        "9:16": "vertical mobile-first composition, portrait orientation",
        "1:1": "square composition, balanced framing"
    }

    composition = composition_hints.get(aspect_ratio, "")

    # プロンプトテンプレート
    prompt = f"""Create a professional book promotional video in {style_desc} style.

Book Title: {book_name}
Promotional Angle: {pattern_name}

Video Concept:
{summary}

Technical Requirements:
- Style: {visual_style}
- Composition: {composition}
- Mood: Engaging, professional, emotionally compelling
- Pacing: Dynamic with smooth transitions
- Target: Attract potential readers and capture the essence of the book

Visual Elements:
- Opening shot that immediately captures attention
- Visual metaphors related to the book's themes
- Smooth camera movements (pans, zooms, dolly shots)
- Professional color grading
- Compelling visual storytelling

The video should feel like a high-end book trailer that makes viewers want to read the book immediately."""

    return prompt.strip()


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
