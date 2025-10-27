#!/usr/bin/env python3
"""
動画結合モジュール

複数のSora2生成動画を結合して1つの長い動画を作成
moviepyを使用（Streamlit Cloud対応）
"""

from pathlib import Path
from typing import List, Optional
import time
import tempfile

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
    print("✓ moviepy imported successfully")
except ImportError as e:
    MOVIEPY_AVAILABLE = False
    print(f"⚠️ moviepy import failed: {e}")


def concatenate_videos(
    video_files: List[Path],
    output_file: Optional[Path] = None
) -> Path:
    """
    複数の動画を結合して1つの動画にする（Streamlit Cloud対応）

    Args:
        video_files: 結合する動画ファイルのリスト（順番通り）
        output_file: 出力ファイルパス（指定しない場合は/tmpに自動生成）

    Returns:
        結合された動画ファイルのパス
    """
    if not video_files:
        raise ValueError("At least one video file is required")

    # 出力パスの決定（Streamlit Cloud対応: /tmpを使用）
    if output_file is None:
        # Streamlit Cloudでは/tmpディレクトリを使用
        temp_dir = Path(tempfile.gettempdir()) / "sora2_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        output_file = temp_dir / f"concatenated_{timestamp}.mp4"
    else:
        # output_fileが指定されている場合も親ディレクトリを作成
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

    # moviepyを優先的に使用（Streamlit Cloud対応）
    if MOVIEPY_AVAILABLE:
        try:
            print(f"🎬 moviepyで動画を結合中... ({len(video_files)}個のファイル)")

            # 動画クリップをロード
            clips = [VideoFileClip(str(f)) for f in video_files]

            # 結合
            final_clip = concatenate_videoclips(clips, method="compose")

            # Streamlit Cloud対応: 一時ディレクトリに音声ファイルを出力
            temp_audio = Path(tempfile.gettempdir()) / f"temp-audio-{int(time.time())}.m4a"

            # 出力
            final_clip.write_videofile(
                str(output_file),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(temp_audio),
                remove_temp=True,
                logger=None,  # ログ出力を抑制
                verbose=False,
                threads=4
            )

            # クリーンアップ
            for clip in clips:
                clip.close()
            final_clip.close()

            print(f"✓ 結合完了: {output_file}")
            return output_file

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"⚠️ moviepyでの結合に失敗: {e}")
            print(f"詳細:\n{error_details}")
            # moviepyが失敗した場合はエラーを上げる（Streamlit Cloudはffmpegなし）
            raise RuntimeError(
                f"moviepyでの動画結合に失敗しました。\n\n"
                f"エラー: {e}\n\n"
                f"詳細:\n{error_details}\n\n"
                f"Streamlit Cloudではffmpegが利用できないため、moviepyのインストールとImageMagickの設定を確認してください。"
            )

    # moviepyが利用できない場合
    import sys
    raise RuntimeError(
        "moviepyがインストールされていません。\n\n"
        "対処方法:\n"
        "1. requirements.txtにmoviepy>=1.0.3があることを確認\n"
        "2. Streamlit Cloudでアプリを再起動\n"
        "3. pip install moviepy を実行\n\n"
        f"Python version: {sys.version}\n"
        f"Available packages: moviepy が見つかりません\n\n"
        "注: Streamlit Cloudではffmpegが利用できないため、moviepyが必須です。"
    )
