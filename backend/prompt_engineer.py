#!/usr/bin/env python3
"""
Sora2プロンプトエンジニアリングモジュール

書籍情報とシナリオから最適なSora2プロンプトを生成
sample_sora.pyのプロンプト構造を参考に、詳細なシーン構成を生成
"""

from typing import Dict, Any, List


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
    duration: int = 10
) -> str:
    """
    シナリオからSora2用の動画生成プロンプトを作成

    Args:
        scenario: シナリオ情報
            - book_name: 書籍名
            - selected_pattern: 選択されたパターン
            - summary: プロモーションシナリオ
        aspect_ratio: アスペクト比
        visual_style: ビジュアルスタイル
        duration: 動画の長さ（秒）

    Returns:
        Sora2プロンプト
    """
    book_name = scenario.get('book_name', '書籍')
    pattern = scenario.get('selected_pattern', {})
    pattern_name = pattern.get('pattern_name', '標準')
    summary = pattern.get('summary', '')

    # ビジュアルスタイルに応じたスタイル記述
    style_map = {
        "Photorealistic": "photorealistic, cinematic documentary style",
        "Picture book": "illustrated picture book style, warm hand-painted aesthetic",
        "3D cartoon": "3D cartoon, stylized character design, vibrant",
        "Retro comics": "retro comic book style, vintage halftone, bold linework",
        "Anime": "2D anime style, cel-shaded, hand-drawn aesthetic",
        "Pixel art": "pixel art, retro 16-bit style",
        "Cinematic": "cinematic film production, professional color grading",
        "Hyper cartoon": "hyper-expressive cartoon, exaggerated motion and poses",
        "Illustration": "illustration, artistic hand-drawn look",
        "Dreamtale": "dreamlike, surreal, ethereal atmosphere",
        "Skytale": "skytale style, abstract geometric patterns",
        "80s film": "1980s film aesthetic, vintage grain, nostalgic tones",
        "Minimalist": "minimalist, clean simple design, negative space",
        "Horror": "horror atmosphere, dark moody lighting, unsettling",
        "Sketchbook": "sketchbook style, hand-drawn pencil aesthetic"
    }

    style_desc = style_map.get(visual_style, "professional, high-quality")

    # シーン分割（durationに応じて2-5シーン）
    # 4秒: 2シーン, 8秒: 3シーン, 12秒: 4シーン
    if duration <= 4:
        num_scenes = 2
    elif duration <= 8:
        num_scenes = 3
    else:
        num_scenes = 4

    per_scene = duration / num_scenes

    # ヘッダー構築
    header = (
        f"Create a single book promotional video for '{book_name}'. "
        f"Total length: {duration} seconds. Aspect {aspect_ratio}. "
        f"Style: {style_desc}. {GLOBAL_STYLE} "
        f"The video should convey the book's essence and make viewers want to read it. "
        f"Do not depict any real person's identifiable face; use symbolic/abstract representations. "
        f"No brand logos or trademarks."
    )

    # シナリオをシーンに分割して構成
    scenes = _split_scenario_into_scenes(summary, num_scenes, per_scene, book_name)

    # プロンプト組み立て
    prompt_parts = [header] + scenes

    return "\n".join(prompt_parts)


def _split_scenario_into_scenes(
    summary: str,
    num_scenes: int,
    per_scene: float,
    book_name: str
) -> List[str]:
    """
    シナリオを複数シーンに分割

    日本語のシナリオを英語の視覚的記述に変換してシーン構成を作成

    Args:
        summary: プロモーションシナリオ（日本語可）
        num_scenes: シーン数
        per_scene: 1シーンあたりの秒数
        book_name: 書籍名

    Returns:
        シーン記述のリスト（英語）
    """
    # シンプルな英語シーン記述を生成
    # 日本語シナリオではなく、視覚的な指示のみを含める

    scenes = []

    # 基本的なシーン構成（書籍プロモーション用）
    scene_templates = [
        f"Opening scene (~{per_scene:.1f}s): Cinematic establishing shot. Camera slowly pushes in on symbolic imagery representing the book's core theme. Warm, inviting lighting. Subtle motion.",
        f"Scene 2 (~{per_scene:.1f}s): Visual metaphor sequence. Smooth camera movement revealing key thematic elements. Professional color grading. Gentle transitions.",
        f"Scene 3 (~{per_scene:.1f}s): Emotional beat. Close-up details that capture the essence and mood. Dynamic but controlled camera work.",
        f"Scene 4 (~{per_scene:.1f}s): Building momentum. Wide to medium shots showing scope and impact. Cinematic framing.",
        f"Final scene (~{per_scene:.1f}s): Title reveal. Camera pulls back to show book title '{book_name}' elegantly displayed. Fade to clean end frame."
    ]

    # num_scenesに合わせてテンプレートを選択
    for i in range(num_scenes):
        if i < len(scene_templates):
            scenes.append(scene_templates[i])
        else:
            scenes.append(f"Scene {i+1} (~{per_scene:.1f}s): Smooth cinematic shot with professional composition.")

    return scenes


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
