#!/usr/bin/env python3
"""
Page 3: Sora2動画生成

シナリオをもとにSora2で動画を一撃生成
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import sora2_engine, prompt_engineer

st.set_page_config(
    page_title="3️⃣ Sora2動画生成",
    page_icon="🎬",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 1rem;
    margin-bottom: 2rem;
}
.prompt-card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 1rem;
    border-left: 4px solid #667eea;
    margin-bottom: 1.5rem;
}
.video-card {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🎬 Step 3: Sora2動画生成</h1><p>AIが一撃で動画を生成します</p></div>', unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.header("📍 現在の位置")
    st.info("**Step 3/3**: Sora2動画生成")

    if st.button("🏠 ホームに戻る"):
        st.session_state.current_step = 0
        st.switch_page("app.py")

    if st.button("⬅️ シナリオ選択に戻る"):
        st.session_state.current_step = 2
        st.switch_page("pages/2_scenario_editor.py")

# セッション状態チェック
if 'selected_scenario' not in st.session_state:
    st.warning("⚠️ 先にシナリオを選択してください")
    if st.button("シナリオ選択へ"):
        st.switch_page("pages/2_scenario_editor.py")
    st.stop()

scenario = st.session_state.selected_scenario

# シナリオ情報表示
st.subheader("📖 選択されたシナリオ")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("書籍名", scenario['book_name'])

with col2:
    pattern_name = scenario.get('selected_pattern', {}).get('pattern_name', '不明')
    st.metric("パターン", pattern_name)

with col3:
    aspect_ratio = scenario.get('aspect_ratio', '16:9')
    visual_style = scenario.get('visual_style', 'Photorealistic')
    st.metric("設定", f"{aspect_ratio} / {visual_style}")

# プロンプト生成
st.markdown("---")
st.subheader("✨ Sora2プロンプト生成")

with st.container():
    # プロンプトタイプ選択
    prompt_type = st.radio(
        "プロンプトタイプ",
        ["詳細版（推奨）", "シンプル版"],
        help="詳細版: より具体的な指示でクオリティ向上 / シンプル版: 簡潔な指示"
    )

    # 動画の長さを選択（先に選択させる）
    duration = st.radio(
        "動画の長さ",
        [4, 8, 12],
        index=1,
        format_func=lambda x: f"{x}秒",
        help="Sora2 APIで選択可能な長さは 4, 8, 12秒のみです",
        horizontal=True
    )

    # プロンプト生成
    if prompt_type == "詳細版（推奨）":
        sora_prompt = prompt_engineer.create_sora2_prompt(
            scenario=scenario,
            aspect_ratio=scenario.get('aspect_ratio', '16:9'),
            visual_style=scenario.get('visual_style', 'Photorealistic'),
            duration=duration
        )
    else:
        sora_prompt = prompt_engineer.create_simple_prompt(
            book_name=scenario['book_name'],
            summary=scenario.get('selected_pattern', {}).get('summary', ''),
            visual_style=scenario.get('visual_style', 'Photorealistic')
        )

    # プロンプト表示・編集
    edited_prompt = st.text_area(
        "生成されたプロンプト（編集可能）",
        value=sora_prompt,
        height=300,
        help="必要に応じてプロンプトを編集できます"
    )

    st.session_state.sora_prompt = edited_prompt

# 動画設定
st.markdown("---")
st.subheader("⚙️ 生成設定サマリー")

# durationはプロンプト生成時に選択済み
video_duration = duration

# シーン数計算
if video_duration <= 4:
    num_scenes = 2
elif video_duration <= 8:
    num_scenes = 3
else:
    num_scenes = 4

st.info(f"""
**設定サマリー**
- アスペクト比: {scenario.get('aspect_ratio', '16:9')}
- ビジュアルスタイル: {scenario.get('visual_style', 'Photorealistic')}
- 動画の長さ: {video_duration}秒
- シーン数: {num_scenes}シーン
""")

# 動画生成
st.markdown("---")
st.subheader("🎬 動画生成")

if 'generated_video' not in st.session_state:
    st.markdown("""
    **Sora2について:**
    - OpenAIの最新動画生成AI
    - 高品質な動画を数分で生成
    - プロンプトから直接動画を作成
    - シナリオを自動で複数シーンに分割

    **処理時間:** 約1-3分（動画の長さにより変動）
    """)

    if st.button("🚀 Sora2で動画生成", type="primary", use_container_width=True):
        with st.spinner("🎬 Sora2で動画を生成中..."):
            try:
                aspect_ratio = scenario.get('aspect_ratio', '16:9')
                st.write(f"DEBUG: アスペクト比 = {aspect_ratio}, Duration = {video_duration}")

                # Sora2で動画生成
                result = sora2_engine.generate_video(
                    prompt=st.session_state.sora_prompt,
                    book_name=scenario['book_name'],
                    aspect_ratio=aspect_ratio,
                    duration=video_duration
                )

                if result['status'] == 'success':
                    st.session_state.generated_video = result
                    st.success("✅ 動画生成が完了しました！")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ エラーが発生しました: {result.get('error', '不明なエラー')}")
                    st.warning("⚠️ Sora2 APIが利用できない可能性があります。APIキーとアクセス権限を確認してください。")

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.exception(e)
else:
    st.success("✅ 動画生成済み")

    video_result = st.session_state.generated_video

    # 動画プレビュー
    with st.container():
        st.subheader("🎥 生成された動画")

    if video_result.get('video_file') and video_result['video_file'].exists():
        # 動画表示
        col_left, col_video, col_right = st.columns([1, 3, 1])

        with col_video:
            st.video(str(video_result['video_file']))

        # ダウンロードボタン
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            with open(video_result['video_file'], 'rb') as f:
                video_bytes = f.read()

            st.download_button(
                label="📥 動画をダウンロード（MP4）",
                data=video_bytes,
                file_name=f"{scenario['book_name']}_sora2.mp4",
                mime="video/mp4",
                use_container_width=True
            )

        # 生成情報
        st.markdown("---")

        with st.expander("📊 生成情報"):
            st.json({
                "書籍名": scenario['book_name'],
                "アスペクト比": video_result['aspect_ratio'],
                "動画の長さ": f"{video_result['duration']}秒",
                "生成ID": video_result.get('generation_id', 'N/A'),
                "使用プロンプト": video_result['prompt'][:200] + "..." if len(video_result['prompt']) > 200 else video_result['prompt']
            })

    else:
        st.warning("⚠️ 動画ファイルが見つかりません")

    # 再生成ボタン
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("🔄 別の動画を生成", use_container_width=True):
            del st.session_state.generated_video
            st.rerun()

    with col2:
        if st.button("⬅️ シナリオを変更", use_container_width=True):
            del st.session_state.generated_video
            st.session_state.current_step = 2
            st.switch_page("pages/2_scenario_editor.py")

    with col3:
        if st.button("🏠 最初から", use_container_width=True):
            # セッションクリア
            keys_to_delete = ['generated_video', 'selected_scenario', 'uploaded_epub', 'book_analysis']
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_step = 0
            st.switch_page("app.py")
