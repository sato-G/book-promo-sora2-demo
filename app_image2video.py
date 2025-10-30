#!/usr/bin/env python3
"""
Sora2 Image-to-Video 簡易UI
画像とプロンプトから動画を生成
"""
import os
import streamlit as st
import requests
import time
from pathlib import Path
from PIL import Image
import tempfile
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()


def resize_image_for_sora(image_path, target_width=1280, target_height=720):
    """画像をSora2の要求サイズにリサイズ"""
    img = Image.open(image_path)

    if img.size == (target_width, target_height):
        return image_path

    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    temp_path = Path(tempfile.gettempdir()) / "sora2_temp_resized.jpg"
    img_resized.save(temp_path, quality=95)

    return temp_path


def generate_video_from_image(image_path, prompt, duration=8, progress_callback=None):
    """画像から動画を生成"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None, "OPENAI_API_KEYが設定されていません"

    # 秒数のバリデーション
    if duration not in [4, 8, 12]:
        return None, f"秒数は 4, 8, 12 のいずれかを指定してください（指定値: {duration}）"

    # 画像をリサイズ
    resized_image_path = resize_image_for_sora(image_path)

    try:
        api_url = "https://api.openai.com/v1/videos"
        headers = {"Authorization": f"Bearer {api_key}"}

        # 動画生成リクエスト
        with open(resized_image_path, 'rb') as f:
            files = {'input_reference': (Path(resized_image_path).name, f, 'image/jpeg')}
            data = {
                'model': 'sora-2',
                'prompt': prompt,
                'size': '1280x720',
                'seconds': str(duration)
            }

            response = requests.post(api_url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                return None, f"API Error: {response.status_code} - {response.text}"

            result = response.json()
            video_id = result.get('id')

            if progress_callback:
                progress_callback("ジョブ開始", 0)

        # ポーリング
        max_wait = 600
        elapsed = 0

        while elapsed < max_wait:
            status_response = requests.get(f"{api_url}/{video_id}", headers=headers)

            if status_response.status_code != 200:
                return None, f"Status check error: {status_response.status_code}"

            status_data = status_response.json()
            status = status_data.get('status')

            if progress_callback:
                progress = min(90, int((elapsed / 120) * 100))  # 最大90%まで
                progress_callback(f"生成中: {status}", progress)

            if status == 'completed':
                break
            elif status == 'failed':
                error_msg = status_data.get('error', {})
                return None, f"生成失敗: {error_msg}"

            time.sleep(10)
            elapsed += 10

        if elapsed >= max_wait:
            return None, "タイムアウト"

        # ダウンロード
        if progress_callback:
            progress_callback("ダウンロード中", 95)

        download_url = f"{api_url}/{video_id}/content"
        video_response = requests.get(download_url, headers=headers)

        if video_response.status_code != 200:
            return None, f"ダウンロードエラー: {video_response.status_code}"

        # 一時ファイルに保存
        temp_video = Path(tempfile.gettempdir()) / f"sora2_video_{video_id}.mp4"
        with open(temp_video, 'wb') as f:
            f.write(video_response.content)

        if progress_callback:
            progress_callback("完了", 100)

        return temp_video, None

    except Exception as e:
        return None, f"エラー: {str(e)}"


# Streamlit UI
st.set_page_config(
    page_title="Sora2 Image-to-Video",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Sora2 Image-to-Video Generator")
st.markdown("画像とプロンプトから動画を生成します")

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定")
    duration = st.selectbox(
        "動画の長さ（秒）",
        options=[4, 8, 12],
        index=1  # デフォルト8秒
    )

    st.markdown("---")
    st.markdown("""
    ### 📝 使い方
    1. 画像をアップロード
    2. プロンプトを入力
    3. 「動画を生成」をクリック
    4. 完成したら動画をダウンロード

    ### ⚠️ 注意
    - 生成には1-3分かかります
    - モデレーションで拒否される場合があります
    """)

# メインコンテンツ
uploaded_file = st.file_uploader(
    "画像をアップロード",
    type=['jpg', 'jpeg', 'png'],
    help="JPEG/PNG形式の画像をアップロードしてください"
)

if uploaded_file:
    # 画像プレビュー
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(uploaded_file, caption="アップロード画像", use_container_width=True)

    with col2:
        # プロンプト入力
        prompt = st.text_area(
            "プロンプト（英語推奨）",
            height=150,
            placeholder="例: Slow zoom in on the scene\nCamera moves forward slowly\nGentle camera movement",
            help="動画の動きを説明してください"
        )

        # プロンプト例
        with st.expander("💡 プロンプト例"):
            st.markdown("""
            - `Slow zoom in`
            - `Camera moves forward slowly`
            - `Gentle panning from left to right`
            - `The dinosaur roars and moves forward`
            - `Dramatic zoom out revealing the landscape`
            """)

    # 生成ボタン
    if st.button("🎬 動画を生成", type="primary", use_container_width=True):
        if not prompt:
            st.error("プロンプトを入力してください")
        else:
            # 一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # プログレスバー
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(message, progress):
                status_text.text(message)
                progress_bar.progress(progress)

            # 動画生成
            with st.spinner("動画を生成中..."):
                video_path, error = generate_video_from_image(
                    tmp_path,
                    prompt,
                    duration,
                    progress_callback=update_progress
                )

            # 一時ファイル削除
            os.unlink(tmp_path)

            if error:
                st.error(f"❌ {error}")
            else:
                st.success("✅ 動画生成完了！")

                # 動画プレビュー
                st.video(str(video_path))

                # ダウンロードボタン
                with open(video_path, 'rb') as f:
                    video_bytes = f.read()

                st.download_button(
                    label="📥 動画をダウンロード",
                    data=video_bytes,
                    file_name=f"sora2_video_{int(time.time())}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

                # ファイルサイズ表示
                file_size_mb = len(video_bytes) / 1024 / 1024
                st.caption(f"ファイルサイズ: {file_size_mb:.2f} MB")

else:
    # 画像未アップロード時の表示
    st.info("👆 まず画像をアップロードしてください")

    # デモ画像の表示
    st.markdown("### 📸 デモ画像例")
    st.caption("風景、物体、抽象的な画像などが適しています")
