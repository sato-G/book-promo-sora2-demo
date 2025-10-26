#!/usr/bin/env python3
"""
動画結合モジュール

複数のSora2生成動画を結合して1つの長い動画を作成
moviepyを使用（Streamlit Cloud対応）
"""

from pathlib import Path
from typing import List, Optional
import time

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    # フォールバック用
    import subprocess


def concatenate_videos(
    video_files: List[Path],
    output_file: Optional[Path] = None,
    output_dir: Optional[Path] = None
) -> Path:
    """
    複数の動画を結合して1つの動画にする

    Args:
        video_files: 結合する動画ファイルのリスト（順番通り）
        output_file: 出力ファイルパス（指定しない場合は自動生成）
        output_dir: 出力ディレクトリ（output_fileが指定されていない場合）

    Returns:
        結合された動画ファイルのパス
    """
    if not video_files:
        raise ValueError("At least one video file is required")

    # 出力パスの決定
    if output_file is None:
        if output_dir is None:
            project_root = Path(__file__).parent.parent
            output_dir = project_root / "data" / "output" / "sora2_videos"

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        output_file = output_dir / f"concatenated_{timestamp}.mp4"

    # moviepyを優先的に使用（Streamlit Cloud対応）
    if MOVIEPY_AVAILABLE:
        try:
            print(f"🎬 moviepyで動画を結合中... ({len(video_files)}個のファイル)")

            # 動画クリップをロード
            clips = [VideoFileClip(str(f)) for f in video_files]

            # 結合
            final_clip = concatenate_videoclips(clips, method="compose")

            # 出力
            final_clip.write_videofile(
                str(output_file),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None  # ログ出力を抑制
            )

            # クリーンアップ
            for clip in clips:
                clip.close()
            final_clip.close()

            print(f"✓ 結合完了: {output_file}")
            return output_file

        except Exception as e:
            print(f"⚠️ moviepyでの結合に失敗: {e}")
            # ffmpegにフォールバック
            if not check_ffmpeg_available():
                raise RuntimeError(f"moviepyとffmpeg両方が利用できません: {e}")

    # ffmpegを使用（フォールバック）
    concat_list_file = output_file.parent / f"concat_list_{int(time.time())}.txt"

    try:
        import subprocess
        # concat用のリストファイルを作成
        with open(concat_list_file, 'w') as f:
            for video_file in video_files:
                # ffmpegのconcat形式: file 'path'
                f.write(f"file '{video_file.absolute()}'\n")

        # ffmpegで結合
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_list_file),
            '-c', 'copy',  # 再エンコードなし（高速）
            '-y',  # 上書き確認なし
            str(output_file)
        ]

        print(f"🎬 動画を結合中... ({len(video_files)}個のファイル)")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            # 再エンコード方式で再試行（codec互換性の問題対策）
            print("⚠️ コピーモードで失敗、再エンコードで再試行...")
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_list_file),
                '-c:v', 'libx264',  # H.264で再エンコード
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-y',
                str(output_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")

        print(f"✓ 結合完了: {output_file}")
        return output_file

    finally:
        # 一時ファイルを削除
        if concat_list_file.exists():
            concat_list_file.unlink()


def check_ffmpeg_available() -> bool:
    """
    ffmpegが利用可能かチェック

    Returns:
        ffmpegが使用可能な場合True
    """
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
