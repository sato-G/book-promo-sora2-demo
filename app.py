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
:root {
    --primary-color: #8B5CF6;
    --secondary-color: #06B6D4;
    --success-color: #10B981;
}

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

.step-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    margin: 0.25rem;
    border-radius: 2rem;
    background: #f0f0f0;
    font-size: 0.9rem;
}

.step-badge.completed {
    background: #10B981;
    color: white;
}

.step-badge.current {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
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
    st.header("📍 ナビゲーション")

    # ステップ表示
    steps = [
        ("1️⃣ EPUBアップロード", "pages/1_upload_epub.py"),
        ("2️⃣ シナリオ選択", "pages/2_scenario_editor.py"),
        ("3️⃣ Sora2動画生成", "pages/3_sora2_generate.py")
    ]

    current_step = st.session_state.get('current_step', 0)

    for i, (label, page) in enumerate(steps, 1):
        if i == current_step:
            st.markdown(f'<div class="step-badge current">{label}</div>', unsafe_allow_html=True)
        elif i < current_step:
            st.markdown(f'<div class="step-badge completed">{label}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="step-badge">{label}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # デバッグ情報
    with st.expander("🔧 デバッグ情報"):
        st.write("現在のステップ:", current_step)
        st.write("EPUB:", "✅" if st.session_state.get('uploaded_epub') else "❌")
        st.write("書籍分析:", "✅" if st.session_state.get('book_analysis') else "❌")
        st.write("シナリオ選択:", "✅" if st.session_state.get('selected_scenario') else "❌")
        st.write("生成済み動画:", "✅" if st.session_state.get('generated_video') else "❌")

    st.markdown("---")

    # セッション復元機能
    with st.expander("📂 セッション復元"):
        st.caption("過去に生成した動画を復元できます")

        # backend読み込み
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from backend import session_manager

        # 利用可能なセッション一覧
        sessions = session_manager.get_saved_sessions()
        if sessions:
            # 書籍名を抽出
            book_names = set()
            for session_path in sessions:
                filename = session_path.name
                if 'latest' in filename:
                    book_name = filename.replace('session_', '').replace('_latest.json', '')
                    book_names.add(book_name)

            if book_names:
                selected_book = st.selectbox(
                    "書籍を選択",
                    sorted(book_names),
                    key="restore_book_select"
                )

                if st.button("🔄 このセッションを復元", use_container_width=True):
                    session_data = session_manager.load_session_state(selected_book, use_latest=True)
                    if session_data:
                        # session_stateに復元
                        if 'scenario' in session_data:
                            st.session_state.selected_scenario = session_data['scenario']
                        if 'generated_video' in session_data:
                            st.session_state.generated_video = session_data['generated_video']
                        if 'generation_mode' in session_data:
                            st.session_state.generation_mode = session_data['generation_mode']
                        if 'edited_scenario' in session_data:
                            st.session_state.edited_scenario = session_data['edited_scenario']
                        if 'edited_scenario_part1' in session_data:
                            st.session_state.edited_scenario_part1 = session_data['edited_scenario_part1']
                        if 'edited_scenario_part2' in session_data:
                            st.session_state.edited_scenario_part2 = session_data['edited_scenario_part2']

                        st.session_state.current_step = 3  # Sora2生成ページへ

                        st.success(f"✅ セッション復元完了: {selected_book}")
                        st.info("Sora2生成ページから確認できます")
                        st.rerun()
                    else:
                        st.error("セッションの読み込みに失敗しました")
            else:
                st.info("復元可能なセッションがありません")
        else:
            st.info("保存されたセッションがありません")

    st.markdown("---")

    if st.button("🔄 すべてリセット"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# メインコンテンツ
col1, col2 = st.columns([2, 1])

with col1:
    with st.container():
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

with col2:
    with st.container():
        st.subheader("⚙️ 技術スタック")

        st.markdown("""
        - **Sora2**: 動画生成
        - **Gemini 2.5**: テキスト分析
        - **Streamlit**: UI
        - **Python**: バックエンド
        """)

# ワークフローステップ
st.markdown("---")
st.subheader("📋 ワークフロー")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("### 1️⃣ EPUBアップロード")
        st.markdown("書籍ファイルをアップロードして自動解析")

        if st.button("開始 →", key="step1", use_container_width=True):
            st.session_state.current_step = 1
            st.switch_page("pages/1_upload_epub.py")

with col2:
    with st.container():
        st.markdown("### 2️⃣ シナリオ選択")
        st.markdown("複数パターンから最適なシナリオを選択")

        disabled = 'uploaded_epub' not in st.session_state

        if st.button("開始 →", key="step2", use_container_width=True, disabled=disabled):
            st.session_state.current_step = 2
            st.switch_page("pages/2_scenario_editor.py")

        if disabled:
            st.caption("⚠️ Step 1を完了してください")

with col3:
    with st.container():
        st.markdown("### 3️⃣ Sora2生成")
        st.markdown("AIが一撃で動画を生成")

        disabled = 'selected_scenario' not in st.session_state

        if st.button("開始 →", key="step3", use_container_width=True, disabled=disabled):
            st.session_state.current_step = 3
            st.switch_page("pages/3_sora2_generate.py")

        if disabled:
            st.caption("⚠️ Step 2を完了してください")

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
