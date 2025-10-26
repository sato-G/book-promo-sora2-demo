#!/usr/bin/env python3
"""
Sora2プロンプトエンジニアリングモジュール

書籍情報とシナリオから最適なSora2プロンプトを生成
sample_sora.pyのプロンプト構造を参考に、詳細なシーン構成を生成
"""

from typing import Dict, Any, List, Optional


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
    シナリオからSora2用の動画生成プロンプトを作成

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
    pattern_name = pattern.get('pattern_name', '標準')

    # ナレーションテキストを使用（指定がなければデフォルトのsummary）
    if narration_text:
        summary = narration_text
    else:
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

    # ナレーション付き指示（sample_sora.py形式）
    has_narration = summary and len(summary) > 10
    narration_instruction = ""
    if has_narration:
        narration_instruction = (
            " Audio: Generate Japanese voice-over narration as instructed; "
            "natural, emotive Japanese voice (professional narrator quality). "
            "Add subtle cinematic BGM (no vocals); automatically duck BGM under voice by ~8 dB."
        )

    # ヘッダー構築
    if total_parts > 1 and part is not None:
        # マルチパート生成の場合
        header = (
            f"Create part {part} of {total_parts} for a book promotional video for '{book_name}'. "
            f"This segment length: {duration} seconds. Aspect {aspect_ratio}. "
            f"Style: {style_desc}. {GLOBAL_STYLE} "
            f"The video should convey the book's essence and make viewers want to read it. "
            f"Do not depict any real person's identifiable face; use symbolic/abstract representations. "
            f"No brand logos or trademarks. "
            f"{'Opening sequence. Start with strong hook.' if part == 1 else 'Continuation from previous segment. Build toward conclusion.'}"
            f"{narration_instruction}"
        )
    else:
        # 単一動画の場合
        header = (
            f"Create a single book promotional video for '{book_name}'. "
            f"Total length: {duration} seconds. Aspect {aspect_ratio}. "
            f"Style: {style_desc}. {GLOBAL_STYLE} "
            f"The video should convey the book's essence and make viewers want to read it. "
            f"Do not depict any real person's identifiable face; use symbolic/abstract representations. "
            f"No brand logos or trademarks."
            f"{narration_instruction}"
        )

    # シナリオをシーンに分割して構成
    scenes = _split_scenario_into_scenes(summary, num_scenes, per_scene, book_name, part, total_parts, has_narration)

    # プロンプト組み立て
    prompt_parts = [header] + scenes

    return "\n".join(prompt_parts)


def _split_scenario_into_scenes(
    summary: str,
    num_scenes: int,
    per_scene: float,
    book_name: str,
    part: Optional[int] = None,
    total_parts: int = 1,
    has_narration: bool = False
) -> List[str]:
    """
    シナリオを複数シーンに分割

    日本語のシナリオを英語の視覚的記述に変換してシーン構成を作成

    Args:
        summary: プロモーションシナリオ（日本語可）
        num_scenes: シーン数
        per_scene: 1シーンあたりの秒数
        book_name: 書籍名
        part: パート番号（2分割の場合）
        total_parts: 総パート数
        has_narration: ナレーションを含むか

    Returns:
        シーン記述のリスト（英語+日本語ナレーション）
    """
    scenes = []

    # 日本語シナリオをシーンごとに分割
    narration_parts = []
    if has_narration and summary:
        # 改行を削除して連続したテキストにする
        summary_cleaned = summary.replace('\n', '').replace('\r', '')

        # 文を分割
        sentences = [s.strip() for s in summary_cleaned.split('。') if s.strip()]
        sentences_per_scene = max(1, len(sentences) // num_scenes)

        for i in range(num_scenes):
            start_idx = i * sentences_per_scene
            end_idx = start_idx + sentences_per_scene if i < num_scenes - 1 else len(sentences)
            narration_text = '。'.join(sentences[start_idx:end_idx])
            if narration_text:
                narration_text += '。'
            narration_parts.append(narration_text)

    # 基本的なシーン構成（書籍プロモーション用）
    if total_parts == 2:
        # 2パート構成の場合
        if part == 1:
            # Part 1: 導入〜中盤
            scene_templates = [
                f"Opening scene (~{per_scene:.1f}s): Cinematic establishing shot. Camera slowly pushes in on symbolic imagery representing the book's core theme. Warm, inviting lighting. Strong opening hook.",
                f"Scene 2 (~{per_scene:.1f}s): Visual metaphor sequence. Smooth camera movement revealing key thematic elements. Professional color grading.",
                f"Scene 3 (~{per_scene:.1f}s): Emotional beat. Close-up details that capture the essence and mood. Dynamic but controlled camera work.",
                f"Scene 4 (~{per_scene:.1f}s): Building momentum. Wide to medium shots showing scope. Transition toward Part 2."
            ]
        else:
            # Part 2: 中盤〜クライマックス
            scene_templates = [
                f"Continuation (~{per_scene:.1f}s): Picking up momentum. Seamless visual flow from previous segment. Intensifying atmosphere.",
                f"Scene 2 (~{per_scene:.1f}s): Key emotional moment. Powerful visual metaphor. High impact framing.",
                f"Scene 3 (~{per_scene:.1f}s): Climactic sequence. Dynamic camera work building to conclusion.",
                f"Final scene (~{per_scene:.1f}s): Title reveal. Camera pulls back to show book title '{book_name}' elegantly displayed. Strong ending with call-to-action feel."
            ]
    else:
        # 単一動画の場合
        scene_templates = [
            f"Opening scene (~{per_scene:.1f}s): Cinematic establishing shot. Camera slowly pushes in on symbolic imagery representing the book's core theme. Warm, inviting lighting. Subtle motion.",
            f"Scene 2 (~{per_scene:.1f}s): Visual metaphor sequence. Smooth camera movement revealing key thematic elements. Professional color grading. Gentle transitions.",
            f"Scene 3 (~{per_scene:.1f}s): Emotional beat. Close-up details that capture the essence and mood. Dynamic but controlled camera work.",
            f"Scene 4 (~{per_scene:.1f}s): Building momentum. Wide to medium shots showing scope and impact. Cinematic framing.",
            f"Final scene (~{per_scene:.1f}s): Title reveal. Camera pulls back to show book title '{book_name}' elegantly displayed. Fade to clean end frame."
        ]

    # num_scenesに合わせてテンプレートを選択し、ナレーションを追加
    for i in range(num_scenes):
        if i < len(scene_templates):
            scene_text = scene_templates[i]
        else:
            scene_text = f"Scene {i+1} (~{per_scene:.1f}s): Smooth cinematic shot with professional composition."

        # ナレーションを追加（sample_sora.py形式）
        # 各シーンのナレーションは50文字以内に制限（長すぎると404エラー）
        if has_narration and i < len(narration_parts) and narration_parts[i]:
            narration = narration_parts[i]
            # 長すぎる場合は最初の50文字のみ使用
            if len(narration) > 50:
                # 句点で区切って最初の文だけ使用
                first_sentence = narration.split('。')[0] + '。'
                if len(first_sentence) > 50:
                    first_sentence = narration[:47] + '...'
                narration = first_sentence
            scene_text += f"\nVoice-over (Japanese): {narration}"

        scenes.append(scene_text)

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
