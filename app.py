#!/usr/bin/env python3
"""
書籍プロモーション動画ジェネレーター - Sora2版

EPUBファイルから自動的にプロモーション動画を生成（Sora2使用）
シンプルな3ステップワークフロー
"""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="書籍プロモーション動画ジェネレーター（Sora2版）",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
.main-title {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 1rem;
    margin-bottom: 2rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
    border-left: 4px solid #667eea;
}

.step-card {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    padding: 1.5rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: transform 0.2s;
}

.step-card:hover {
    transform: translateY(-2px);
}

.demo-badge {
    background: #ff6b6b;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 1rem;
    font-size: 0.9rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# メインタイトル
st.markdown("""
<div class="main-title">
    <h1>📚 書籍プロモーション動画ジェネレーター</h1>
    <h3>Powered by OpenAI Sora2</h3>
    <p style="margin-top: 1rem; font-size: 1.1rem;">EPUBから自動的にプロモーション動画を生成</p>
    <span class="demo-badge">Sora2 Demo Version</span>
</div>
""", unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.header("📖 使い方")
    st.markdown("""
    ### ワークフロー

    1. **EPUBアップロード**
       書籍ファイルをアップロード

    2. **シナリオ選択**
       複数パターンから選択

    3. **Sora2生成**
       一撃で動画を生成！

    ---

    ### 💡 Sora2版の特徴

    - ⚡ 超高速（1-3分）
    - 🎬 高品質な動画
    - ✨ シンプルな操作

    ---

    ### ⚠️ 注意事項

    Sora2 APIが必要です
    """)

    st.markdown("---")

    # セッション状態表示
    if 'current_step' in st.session_state:
        st.info(f"現在: Step {st.session_state.current_step + 1}")

# メインコンテンツ
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.subheader("🚀 主な機能")

    features = [
        ("📤", "EPUBアップロード", "書籍ファイルを自動解析"),
        ("🤖", "AI分析", "Gemini 2.5で書籍を分析"),
        ("🎨", "シナリオ生成", "複数のパターンを提案"),
        ("🎬", "Sora2動画生成", "一撃で高品質動画を作成"),
        ("📥", "ダウンロード", "MP4形式で保存")
    ]

    for icon, title, desc in features:
        st.markdown(f"**{icon} {title}**: {desc}")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.subheader("⚙️ 技術スタック")

    st.markdown("""
    - **Sora2**: 動画生成
    - **Gemini 2.5**: テキスト分析
    - **Streamlit**: UI
    - **Python**: バックエンド
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# ワークフローステップ
st.markdown("---")
st.subheader("📋 ワークフロー")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 1️⃣ EPUBアップロード")
    st.markdown("書籍ファイルをアップロードして自動解析")

    if st.button("開始 →", key="step1", use_container_width=True):
        st.session_state.current_step = 1
        st.switch_page("pages/1_upload_epub.py")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 2️⃣ シナリオ選択")
    st.markdown("複数パターンから最適なシナリオを選択")

    disabled = 'uploaded_epub' not in st.session_state

    if st.button("開始 →", key="step2", use_container_width=True, disabled=disabled):
        st.session_state.current_step = 2
        st.switch_page("pages/2_scenario_editor.py")

    if disabled:
        st.caption("⚠️ Step 1を完了してください")

    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown("### 3️⃣ Sora2生成")
    st.markdown("AIが一撃で動画を生成")

    disabled = 'selected_scenario' not in st.session_state

    if st.button("開始 →", key="step3", use_container_width=True, disabled=disabled):
        st.session_state.current_step = 3
        st.switch_page("pages/3_sora2_generate.py")

    if disabled:
        st.caption("⚠️ Step 2を完了してください")

    st.markdown('</div>', unsafe_allow_html=True)

# フッター
st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <p style="color: #666;">
            Made with ❤️ using Streamlit & Sora2
        </p>
        <p style="color: #999; font-size: 0.9rem;">
            © 2025 Book Promo Video Generator
        </p>
    </div>
    """, unsafe_allow_html=True)

# セッション初期化
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
