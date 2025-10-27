#!/usr/bin/env python3
"""
Page 4: プレビュー＆ダウンロード

生成された動画の最終確認とダウンロード
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import session_manager

st.set_page_config(
    page_title="4️⃣ 完成動画",
    page_icon="🎉",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    border-radius: 1rem;
    margin-bottom: 2rem;
}
.completion-card {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
    text-align: center;
}
.stats-card {
    background: #f0f9ff;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #3b82f6;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🎉 完成！プロモーション動画</h1><p>生成された動画を確認してダウンロード</p></div>', unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.header("📍 現在の位置")
    st.success("**Step 4/4**: 完成動画")

    if st.button("🏠 ホームに戻る"):
        st.switch_page("app.py")

    if st.button("⬅️ 動画生成に戻る"):
        st.switch_page("pages/3_sora2_generate.py")

    st.markdown("---")

    if st.button("🔄 新しいプロジェクトを開始", type="secondary"):
        # 確認
        st.warning("⚠️ 現在のプロジェクトデータがクリアされます")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ はい", key="confirm_new"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.switch_page("app.py")
        with col2:
            if st.button("❌ いいえ", key="cancel_new"):
                st.rerun()

# 前提チェック
if 'final_video' not in st.session_state:
    st.warning("⚠️ まだ動画が生成されていません")
    st.info("先にSora2動画生成ページで全シーンを生成し、結合してください")

    if st.button("➡️ 動画生成ページへ"):
        st.switch_page("pages/3_sora2_generate.py")
    st.stop()

# 動画情報取得
final_video = st.session_state.final_video
scenario = st.session_state.get('selected_scenario', {})
scenes = st.session_state.get('scenes', [])
scene_videos = st.session_state.get('scene_videos', {})

# 完成メッセージ
st.markdown("""
<div class="completion-card">
    <h2>✨ 動画生成完了 ✨</h2>
    <p style="font-size: 1.2rem; color: #666;">プロモーション動画が完成しました！</p>
</div>
""", unsafe_allow_html=True)

# 書籍情報
st.markdown("---")
st.subheader("📖 書籍情報")

col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.metric("書籍名", scenario.get('book_name', '不明'))

with col_info2:
    pattern_name = scenario.get('selected_pattern', {}).get('pattern_name', '不明')
    st.metric("シナリオパターン", pattern_name)

with col_info3:
    aspect_ratio = scenario.get('aspect_ratio', '16:9')
    visual_style = scenario.get('visual_style', 'Photorealistic')
    st.metric("スタイル", f"{aspect_ratio} / {visual_style}")

# 動画統計
st.markdown("---")
st.subheader("📊 動画統計")

if final_video.get('video_file') and Path(final_video['video_file']).exists():
    video_path = Path(final_video['video_file'])
    file_size_mb = video_path.stat().st_size / (1024 * 1024)

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

    with col_stat1:
        st.markdown("""
        <div class="stats-card">
            <h3>⏱️ 動画の長さ</h3>
            <p style="font-size: 1.5rem; font-weight: bold;">{} 秒</p>
        </div>
        """.format(final_video.get('duration', 36)), unsafe_allow_html=True)

    with col_stat2:
        st.markdown("""
        <div class="stats-card">
            <h3>🎬 シーン数</h3>
            <p style="font-size: 1.5rem; font-weight: bold;">{} シーン</p>
        </div>
        """.format(final_video.get('scene_count', len(scenes))), unsafe_allow_html=True)

    with col_stat3:
        st.markdown(f"""
        <div class="stats-card">
            <h3>💾 ファイルサイズ</h3>
            <p style="font-size: 1.5rem; font-weight: bold;">{file_size_mb:.2f} MB</p>
        </div>
        """, unsafe_allow_html=True)

    with col_stat4:
        st.markdown("""
        <div class="stats-card">
            <h3>📐 アスペクト比</h3>
            <p style="font-size: 1.5rem; font-weight: bold;">{}</p>
        </div>
        """.format(final_video.get('aspect_ratio', scenario.get('aspect_ratio', '16:9'))), unsafe_allow_html=True)

# 完成動画プレビュー
st.markdown("---")
st.subheader("🎬 完成動画プレビュー")

if final_video.get('video_file') and Path(final_video['video_file']).exists():
    video_path = Path(final_video['video_file'])

    # 動画プレビュー（中央配置）
    col_left, col_video, col_right = st.columns([1, 3, 1])

    with col_video:
        st.video(str(video_path))

    # ダウンロードセクション
    st.markdown("---")
    st.subheader("📥 ダウンロード")

    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])

    with col_dl2:
        with open(video_path, 'rb') as f:
            video_bytes = f.read()

        st.download_button(
            label="📥 完成動画をダウンロード",
            data=video_bytes,
            file_name=f"{scenario.get('book_name', 'promo')}_final.mp4",
            mime="video/mp4",
            type="primary",
            use_container_width=True
        )

        st.caption(f"💾 ファイル: {video_path.name}")

else:
    st.error("⚠️ 動画ファイルが見つかりません")
    st.info(f"パス: {final_video.get('video_file', 'N/A')}")

# 個別シーンプレビュー
if scene_videos:
    st.markdown("---")
    st.subheader("🎞️ 個別シーンプレビュー")

    st.caption("生成された各シーンを確認できます")

    # シーン数に応じて列数を調整
    num_scenes = len(scene_videos)
    cols = st.columns(min(num_scenes, 3))

    for idx, (scene_num, video_data) in enumerate(sorted(scene_videos.items())):
        col_idx = idx % 3

        with cols[col_idx]:
            st.markdown(f"**シーン {scene_num}**")

            if video_data.get('video_file') and Path(video_data['video_file']).exists():
                scene_path = Path(video_data['video_file'])

                # 小さいプレビュー
                st.video(str(scene_path))

                # 個別ダウンロード
                with open(scene_path, 'rb') as f:
                    st.download_button(
                        "📥",
                        data=f.read(),
                        file_name=f"scene_{scene_num}_{scenario.get('book_name', 'promo')}.mp4",
                        mime="video/mp4",
                        use_container_width=True,
                        key=f"dl_individual_{scene_num}"
                    )
            else:
                st.warning("ファイルなし")

# 次のアクション
st.markdown("---")
st.subheader("🚀 次のアクション")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    if st.button("🔄 別の動画を生成", use_container_width=True):
        # 動画関連のみクリア
        keys_to_delete = ['scenes', 'scene_videos', 'final_video']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("pages/3_sora2_generate.py")

with col_a2:
    if st.button("📝 シナリオを変更", use_container_width=True):
        # シーン・動画をクリア
        keys_to_delete = ['scenes', 'scene_videos', 'final_video']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_step = 2
        st.switch_page("pages/2_scenario_editor.py")

with col_a3:
    if st.button("📖 別の書籍で生成", use_container_width=True):
        # 全クリア
        keys_to_delete = ['scenes', 'scene_videos', 'final_video', 'selected_scenario']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_step = 1
        st.switch_page("pages/1_upload_epub.py")

# 技術情報（折りたたみ）
st.markdown("---")

with st.expander("🔧 技術情報"):
    st.markdown("### 生成情報")

    tech_info = {
        "書籍名": scenario.get('book_name', 'N/A'),
        "アスペクト比": final_video.get('aspect_ratio', scenario.get('aspect_ratio', 'N/A')),
        "ビジュアルスタイル": scenario.get('visual_style', 'N/A'),
        "動画の長さ": f"{final_video.get('duration', 'N/A')}秒",
        "シーン数": final_video.get('scene_count', len(scenes)),
        "動画ファイル": str(final_video.get('video_file', 'N/A'))
    }

    for key, value in tech_info.items():
        st.text(f"{key}: {value}")

    if scenes:
        st.markdown("### シーン詳細")
        for scene in scenes:
            st.text(f"シーン {scene['scene_number']}: {scene['narration'][:30]}...")

st.markdown("---")
st.success("🎉 プロジェクト完了！お疲れ様でした。")
