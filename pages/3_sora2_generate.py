#!/usr/bin/env python3
"""
Page 3: Sora2動画生成（シーンベース版）

シナリオを3シーンに分割 → 各シーン個別生成 → 結合
test_scene_flow.pyの成功パターンを厳密に再現
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import sora2_engine, prompt_engineer, video_composer, session_manager, scene_splitter_sora2

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
.scene-card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 1rem;
    border-left: 4px solid #667eea;
    margin-bottom: 1rem;
}
.warning-box {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🎬 Step 3: Sora2動画生成</h1><p>3シーン構成で高品質プロモーション動画を作成</p></div>', unsafe_allow_html=True)

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

# コンテンツ制限警告
st.markdown("""
<div class="warning-box">
<h4>⚠️ Sora2 コンテンツ制限について</h4>
<ul>
<li>実在人物名は使用できません（公人・一般人問わず）</li>
<li>著作権キャラクター・音楽は使用できません</li>
<li>18歳以上向けコンテンツは使用できません</li>
<li>実在人物が登場する場合は自動的に代名詞に置き換えられます</li>
</ul>
</div>
""", unsafe_allow_html=True)

# シナリオ情報表示と設定変更
col_info, col_settings = st.columns([4, 1])

with col_info:
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

with col_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚙️ 設定変更", use_container_width=True, help="シナリオ選択に戻る"):
        # シーン関連データを削除してシナリオ選択に戻る
        keys_to_delete = ['scenes', 'scene_videos', 'final_video']
        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.current_step = 2
        st.switch_page("pages/2_scenario_editor.py")

st.markdown("---")

# ========================================
# Step 1: シーン分割
# ========================================
st.subheader("🎬 Step 1: シーン分割")

if 'scenes' not in st.session_state:
    st.info("""
    💡 **シーン分割について**
    - シナリオを自動的に3シーン（各12秒）に分割します
    - 元のシナリオテキストを文単位で分割（テキストは変更されません）
    - 文の区切りの良いところで3分割します
    """)

    if st.button("✂️ シーンに分割", type="primary", use_container_width=True):
        with st.spinner("✂️ シーン分割中..."):
            try:
                scenes = scene_splitter_sora2.split_into_scenes_for_sora2(
                    scenario=scenario,
                    num_scenes=3
                )
                st.session_state.scenes = scenes
                st.success("✅ シーン分割完了！")
                st.rerun()
            except Exception as e:
                st.error(f"❌ シーン分割エラー: {str(e)}")
                st.exception(e)
else:
    scenes = st.session_state.scenes

    col_status, col_regen = st.columns([3, 1])

    with col_status:
        st.success(f"✅ {len(scenes)}シーンに分割済み")

    with col_regen:
        if st.button("🔄 シーン分割をやり直す", use_container_width=True, help="新しくシーンを生成し直します"):
            # 確認なしで即座に削除して再生成
            del st.session_state.scenes
            if 'scene_videos' in st.session_state:
                del st.session_state.scene_videos
            if 'final_video' in st.session_state:
                del st.session_state.final_video
            st.rerun()

    # シーン編集UI
    st.markdown("### 📝 シーン編集（ナレーション調整）")
    st.caption("各シーンのナレーションを編集できます（元のシナリオから自動分割）")

    edited_scenes = []

    for i, scene in enumerate(scenes):
        with st.expander(f"**シーン {scene['scene_number']}** ({len(scene['narration'])}文字)", expanded=False):
            edited_narration = st.text_area(
                f"ナレーション (シーン {scene['scene_number']})",
                value=scene['narration'],
                height=100,
                key=f"narration_{i}"
            )

            char_count = len(edited_narration)
            st.caption(f"📊 文字数: {char_count}文字")

            edited_scenes.append({
                'scene_number': scene['scene_number'],
                'narration': edited_narration,
                'duration_seconds': 12
            })

    # 編集されたシーンを保存
    st.session_state.scenes = edited_scenes

# ========================================
# Step 2: 各シーン生成
# ========================================
if 'scenes' in st.session_state:
    st.markdown("---")
    st.subheader("🎥 Step 2: 各シーン動画生成")

    scenes = st.session_state.scenes

    # シーン動画の保存先を初期化
    if 'scene_videos' not in st.session_state:
        st.session_state.scene_videos = {}

    st.info("""
    💡 **動画生成について**
    - 各シーンを個別に生成します（各12秒）
    - 合計生成時間: 36秒
    - 生成には1シーンあたり1-3分かかります
    """)

    # 各シーンの生成ボタンとプレビュー
    for i, scene in enumerate(scenes):
        scene_num = scene['scene_number']

        with st.container():
            st.markdown(f"#### 🎬 シーン {scene_num}")

            col_info, col_action = st.columns([3, 1])

            with col_info:
                st.caption(f"ナレーション: {scene['narration']} ({len(scene['narration'])}文字)")

            with col_action:
                # シーンが既に生成済みかチェック
                if scene_num in st.session_state.scene_videos:
                    col_status, col_regen_scene = st.columns(2)
                    with col_status:
                        st.success("✅ 生成済み")
                    with col_regen_scene:
                        if st.button("🔄", key=f"regen_scene_{scene_num}", help="このシーンを再生成"):
                            # シーン動画を削除して再生成可能に
                            del st.session_state.scene_videos[scene_num]
                            # 最終動画も削除（再結合が必要）
                            if 'final_video' in st.session_state:
                                del st.session_state.final_video
                            st.rerun()
                else:
                    if st.button(f"▶️ シーン {scene_num} を生成", key=f"gen_scene_{scene_num}"):
                        with st.spinner(f"🎬 シーン {scene_num} を生成中... (1-3分)"):
                            try:
                                # test_scene_flow.pyの成功パターンを使用
                                prompt = prompt_engineer.create_scene_prompt_for_sora2(
                                    book_name=scenario['book_name'],
                                    scene_narration=scene['narration'],
                                    visual_style=scenario.get('visual_style', 'Photorealistic'),
                                    aspect_ratio=scenario.get('aspect_ratio', '16:9'),
                                    duration=12,
                                    scene_number=scene_num,
                                    total_scenes=len(scenes)
                                )

                                # デバッグ表示
                                with st.expander(f"🔍 シーン {scene_num} プロンプト"):
                                    st.code(prompt)

                                # Sora2で生成
                                result = sora2_engine.generate_video(
                                    prompt=prompt,
                                    book_name=f"{scenario['book_name']}_scene{scene_num}",
                                    aspect_ratio=scenario.get('aspect_ratio', '16:9'),
                                    duration=12
                                )

                                if result['status'] == 'success':
                                    # 生成結果を保存
                                    st.session_state.scene_videos[scene_num] = result

                                    # セッション保存（途中経過）
                                    try:
                                        session_data = {
                                            'book_name': scenario['book_name'],
                                            'scenario': scenario,
                                            'scenes': scenes,
                                            'scene_videos': {
                                                k: {
                                                    'video_file': str(v['video_file']),
                                                    'generation_id': v.get('generation_id'),
                                                    'prompt': v.get('prompt')
                                                } for k, v in st.session_state.scene_videos.items()
                                            },
                                            'generation_mode': 'scene_based'
                                        }
                                        session_manager.save_session_state(session_data, scenario['book_name'])
                                    except Exception as e:
                                        st.warning(f"⚠️ セッション保存エラー: {str(e)}")

                                    st.success(f"✅ シーン {scene_num} 生成完了！")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(f"❌ シーン {scene_num} 生成エラー: {result.get('error', '不明なエラー')}")

                            except Exception as e:
                                st.error(f"❌ シーン {scene_num} エラー: {str(e)}")
                                st.exception(e)

            # 生成済みの場合はプレビュー表示
            if scene_num in st.session_state.scene_videos:
                video_result = st.session_state.scene_videos[scene_num]

                if video_result.get('video_file') and Path(video_result['video_file']).exists():
                    video_path = Path(video_result['video_file'])

                    col_preview, col_download = st.columns([2, 1])

                    with col_preview:
                        st.video(str(video_path))

                    with col_download:
                        file_size_mb = video_path.stat().st_size / (1024 * 1024)
                        st.caption(f"📊 {file_size_mb:.2f} MB")

                        with open(video_path, 'rb') as f:
                            st.download_button(
                                "📥 DL",
                                data=f.read(),
                                file_name=f"scene_{scene_num}_{scenario['book_name']}.mp4",
                                mime="video/mp4",
                                use_container_width=True,
                                key=f"dl_scene_{scene_num}"
                            )
                else:
                    st.warning("⚠️ 動画ファイルが見つかりません")

        st.markdown("---")

# ========================================
# Step 3: 最終結合
# ========================================
if 'scenes' in st.session_state and 'scene_videos' in st.session_state:
    scenes = st.session_state.scenes
    scene_videos = st.session_state.scene_videos

    # 全シーンが生成済みかチェック
    all_scenes_ready = all(scene['scene_number'] in scene_videos for scene in scenes)

    if all_scenes_ready:
        st.subheader("🎬 Step 3: 最終結合")

        if 'final_video' not in st.session_state:
            st.info("""
            💡 **最終結合について**
            - 3つのシーンを1つの動画に結合します
            - 合計36秒の完成動画が作成されます
            """)

            if st.button("🔗 動画を結合", type="primary", use_container_width=True):
                with st.spinner("🔗 動画を結合中..."):
                    try:
                        # シーン番号順にソート
                        sorted_scene_nums = sorted(scene_videos.keys())
                        video_files = [Path(scene_videos[num]['video_file']) for num in sorted_scene_nums]

                        # 結合実行
                        final_video_path = video_composer.concatenate_videos(
                            video_files,
                            output_file=Path("data/internal/videos") / f"{scenario['book_name']}_final.mp4"
                        )

                        # 最終動画を保存
                        st.session_state.final_video = {
                            'video_file': final_video_path,
                            'duration': 36,
                            'aspect_ratio': scenario.get('aspect_ratio', '16:9'),
                            'scene_count': len(scenes)
                        }

                        # セッション保存（完了）
                        try:
                            session_data = {
                                'book_name': scenario['book_name'],
                                'scenario': scenario,
                                'scenes': scenes,
                                'scene_videos': {
                                    k: {
                                        'video_file': str(v['video_file']),
                                        'generation_id': v.get('generation_id'),
                                        'prompt': v.get('prompt')
                                    } for k, v in scene_videos.items()
                                },
                                'final_video': {
                                    'video_file': str(final_video_path),
                                    'duration': 36
                                },
                                'generation_mode': 'scene_based',
                                'status': 'completed'
                            }
                            session_manager.save_session_state(session_data, scenario['book_name'])
                        except Exception as e:
                            st.warning(f"⚠️ セッション保存エラー: {str(e)}")

                        st.success("✅ 動画結合完了！")
                        st.balloons()
                        st.session_state.current_step = 4
                        st.info("➡️ 完成動画ページで確認できます")

                        # 自動遷移ボタン
                        if st.button("➡️ 完成動画を確認", type="primary", use_container_width=True):
                            st.switch_page("pages/4_preview_download.py")

                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 結合エラー: {str(e)}")
                        st.exception(e)
        else:
            # 最終動画プレビュー
            final_video = st.session_state.final_video

            st.success("🎉 完成動画")

            if final_video.get('video_file') and Path(final_video['video_file']).exists():
                video_path = Path(final_video['video_file'])

                # 動画プレビュー（中央）
                col_left, col_video, col_right = st.columns([1, 2, 1])

                with col_video:
                    st.video(str(video_path))

                # ファイル情報
                file_size_mb = video_path.stat().st_size / (1024 * 1024)

                col_info1, col_info2, col_info3 = st.columns(3)

                with col_info1:
                    st.metric("動画の長さ", f"{final_video['duration']}秒")

                with col_info2:
                    st.metric("ファイルサイズ", f"{file_size_mb:.2f} MB")

                with col_info3:
                    st.metric("シーン数", f"{final_video['scene_count']}シーン")

                # ダウンロード
                st.markdown("---")

                col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])

                with col_dl2:
                    with open(video_path, 'rb') as f:
                        st.download_button(
                            label="📥 完成動画をダウンロード",
                            data=f.read(),
                            file_name=f"{scenario['book_name']}_promo.mp4",
                            mime="video/mp4",
                            type="primary",
                            use_container_width=True
                        )

                # 次のアクション
                st.markdown("---")
                st.subheader("🚀 次のアクション")

                col_a0, col_a1, col_a2, col_a3 = st.columns(4)

                with col_a0:
                    if st.button("✨ 完成動画を確認", type="primary", use_container_width=True):
                        st.session_state.current_step = 4
                        st.switch_page("pages/4_preview_download.py")

                with col_a1:
                    if st.button("🔄 別の動画を生成", use_container_width=True):
                        # 生成結果のみクリア
                        keys_to_delete = ['scenes', 'scene_videos', 'final_video']
                        for key in keys_to_delete:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.rerun()

                with col_a2:
                    if st.button("📝 シナリオを変更", use_container_width=True):
                        # シーン関連をクリア
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
            else:
                st.warning("⚠️ 動画ファイルが見つかりません")
    else:
        # まだ生成されていないシーンがある
        remaining = [s['scene_number'] for s in scenes if s['scene_number'] not in scene_videos]
        st.info(f"💡 残り {len(remaining)} シーンを生成してください: シーン {', '.join(map(str, remaining))}")
