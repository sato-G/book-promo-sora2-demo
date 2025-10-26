#!/usr/bin/env python3
"""
Sora2 API統合モジュール

OpenAI Sora2 APIを使用して動画を生成
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import time

from openai import OpenAI


def get_api_key() -> str:
    """OpenAI APIキーを取得"""
    # Streamlit Cloudの場合
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets['OPENAI_API_KEY']
    except:
        pass

    # 環境変数から取得
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables or Streamlit secrets")

    return api_key


def generate_video(
    prompt: str,
    book_name: str,
    aspect_ratio: str = "16:9",
    duration: int = 10,
    output_dir: Optional[Path] = None,
    model: str = "sora-2"
) -> Dict[str, Any]:
    """
    Sora2で動画を生成

    Args:
        prompt: 動画生成プロンプト
        book_name: 書籍名（ファイル名用）
        aspect_ratio: アスペクト比 ("16:9", "9:16", "1:1")
        duration: 動画の長さ（秒） - 4, 8, 12のみ指定可能
        output_dir: 出力ディレクトリ（Noneの場合は自動生成）
        model: 使用モデル ("sora-2" or "sora-2-pro")

    Returns:
        生成結果の辞書
        {
            'video_file': Path,
            'prompt': str,
            'aspect_ratio': str,
            'duration': int,
            'generation_id': str,
            'status': 'success' | 'error',
            'error': str (エラー時のみ)
        }
    """
    client = OpenAI(api_key=get_api_key())

    # durationの検証（4, 8, 12のみ）
    allowed_durations = [4, 8, 12]
    if duration not in allowed_durations:
        # 最も近い値を選択
        duration = min(allowed_durations, key=lambda x: abs(x - duration))
        print(f"⚠️ Duration adjusted to {duration}s (only 4, 8, 12 are allowed)")

    # 出力ディレクトリの準備
    if output_dir is None:
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "data" / "output" / "sora2_videos"

    output_dir.mkdir(parents=True, exist_ok=True)

    # アスペクト比をサイズに変換
    # sora-2: 720x1280, 1280x720 のみ
    # sora-2-pro: 1024x1792, 1792x1024 もサポート
    if "pro" in model.lower():
        size_map = {
            "16:9": "1792x1024",
            "9:16": "1024x1792",
            "1:1": "1024x1024"
        }
    else:
        size_map = {
            "16:9": "1280x720",
            "9:16": "720x1280",
            "1:1": "720x1280"  # 1:1は非対応なので縦型を使用
        }
    size = size_map.get(aspect_ratio, "720x1280")

    # ファイル名の準備
    safe_book_name = "".join(c for c in book_name if c.isalnum() or c in (' ', '-', '_')).strip()
    timestamp = int(time.time())
    output_filename = f"{safe_book_name}_{timestamp}.mp4"
    output_path = output_dir / output_filename

    try:
        # Sora2 API呼び出し (create_and_poll で非同期生成+ポーリング)
        print("🎬 Sora2で動画生成中...")
        print(f"   Model: {model}")
        print(f"   Aspect Ratio: {aspect_ratio} → Size: {size}")
        print(f"   Duration: {duration}s")

        video = client.videos.create_and_poll(
            model=model,
            prompt=prompt,
            seconds=str(duration),  # "8", "10", "12"
            size=size
        )

        print(f"✓ 動画生成完了 (Video ID: {video.id})")

        # 動画をダウンロード
        print("📥 動画をダウンロード中...")
        content = client.videos.download_content(video.id)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)

        print(f"✓ 保存完了: {output_path}")

        result = {
            'video_file': output_path,
            'prompt': prompt,
            'aspect_ratio': aspect_ratio,
            'duration': duration,
            'generation_id': video.id,
            'status': 'success'
        }

        return result

    except Exception as e:
        # エラー時
        error_result = {
            'video_file': None,
            'prompt': prompt,
            'aspect_ratio': aspect_ratio,
            'duration': duration,
            'generation_id': None,
            'status': 'error',
            'error': str(e)
        }

        return error_result


def check_generation_status(generation_id: str) -> Dict[str, Any]:
    """
    動画生成のステータスをチェック

    Args:
        generation_id: 生成ID

    Returns:
        ステータス情報
    """
    client = OpenAI(api_key=get_api_key())

    try:
        # 生成ステータスを取得
        # 実際のAPI仕様に合わせて調整
        status = client.videos.retrieve(generation_id)

        return {
            'id': generation_id,
            'status': status.status,  # 'pending', 'processing', 'completed', 'failed'
            'progress': getattr(status, 'progress', None),
            'url': getattr(status, 'url', None)
        }

    except Exception as e:
        return {
            'id': generation_id,
            'status': 'error',
            'error': str(e)
        }
