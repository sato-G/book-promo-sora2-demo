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
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Sora2で動画を生成

    Args:
        prompt: 動画生成プロンプト
        book_name: 書籍名（ファイル名用）
        aspect_ratio: アスペクト比 ("16:9", "9:16", "1:1")
        duration: 動画の長さ（秒）
        output_dir: 出力ディレクトリ（Noneの場合は自動生成）

    Returns:
        生成結果の辞書
        {
            'video_file': Path,
            'prompt': str,
            'aspect_ratio': str,
            'duration': int,
            'generation_id': str
        }
    """
    client = OpenAI(api_key=get_api_key())

    # 出力ディレクトリの準備
    if output_dir is None:
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "data" / "output" / "sora2_videos"

    output_dir.mkdir(parents=True, exist_ok=True)

    # ファイル名の準備
    safe_book_name = "".join(c for c in book_name if c.isalnum() or c in (' ', '-', '_')).strip()
    timestamp = int(time.time())
    output_filename = f"{safe_book_name}_{timestamp}.mp4"
    output_path = output_dir / output_filename

    try:
        # Sora2 API呼び出し
        # Note: 2025年1月時点でSora2 APIは限定プレビュー中
        # 実際のAPI仕様に合わせて調整が必要

        # OpenAI APIのSora2エンドポイント (正しいメソッド名)
        response = client.video.generations.create(
            model="sora-turbo-2024-12-20",
            prompt=prompt,
            size=aspect_ratio,  # または "1920x1080" 形式
            duration=duration
        )

        # 動画ファイルを保存
        # APIレスポンスの形式に応じて調整
        if hasattr(response, 'data'):
            video_data = response.data
        elif hasattr(response, 'url'):
            # URLから動画をダウンロード
            import requests
            video_response = requests.get(response.url)
            video_data = video_response.content
        else:
            video_data = response

        with open(output_path, 'wb') as f:
            f.write(video_data)

        result = {
            'video_file': output_path,
            'prompt': prompt,
            'aspect_ratio': aspect_ratio,
            'duration': duration,
            'generation_id': getattr(response, 'id', str(timestamp)),
            'status': 'success'
        }

        return result

    except Exception as e:
        # エラー時はダミー動画を返す（開発用）
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
