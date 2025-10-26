#!/usr/bin/env python3
"""
Page 3: Sora2動画生成

シナリオをもとにSora2で動画を一撃生成
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import sora2_engine, prompt_engineer, video_composer

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

# 生成モード選択
generation_mode = st.radio(
    "生成モード",
    ["シングル（最大12秒）", "2パート結合（最大24秒）"],
    help="2パート結合: 12秒×2本を生成して結合します",
    key="generation_mode_selector"
)

# 動画の長さを選択
if generation_mode == "シングル（最大12秒）":
    duration = st.radio(
        "動画の長さ",
        [4, 8, 12],
        index=2,
        format_func=lambda x: f"{x}秒",
        help="Sora2 APIで選択可能な長さは 4, 8, 12秒のみです",
        horizontal=True
    )
    total_parts = 1
else:
    st.info("📹 2パートモード: 12秒の動画を2本生成して結合します（合計24秒）")
    duration = 12
    total_parts = 2

# シナリオ編集（日本語）
st.markdown("---")
st.subheader("📝 シナリオ編集")
st.markdown("動画で話す内容を編集できます。この内容がSora2の音声ナレーションになります。")

# ナレーション時間の計算
if total_parts == 1:
    total_video_time = duration
else:
    total_video_time = duration * 2

# 話せる文字数の目安（6文字/秒）
max_narration_chars = int(total_video_time * 6)

st.info(f"""
💡 **ナレーションのコツ:**
- この動画の長さ: {total_video_time}秒
- 話せる文字数の目安: 約{max_narration_chars}文字まで
- 長すぎる場合は自動で調整されます（重要な部分を前半に書いてください）
""")

# シナリオを取得
original_summary = scenario.get('selected_pattern', {}).get('summary', '')

if total_parts == 1:
    # シングルモード: 1つのシナリオ
    edited_scenario = st.text_area(
        "シナリオ（編集可能）",
        value=original_summary,
        height=300,
        help="このシナリオが動画のナレーションとして使われます",
        key="scenario_single"
    )

    # 文字数表示
    char_count = len(edited_scenario.replace('\n', '').replace(' ', ''))
    if char_count > max_narration_chars:
        st.warning(f"⚠️ 現在{char_count}文字（推奨{max_narration_chars}文字以内）- 超過分は自動調整されます")
    else:
        st.success(f"✅ {char_count}文字（推奨範囲内）")

    st.session_state.edited_scenario = edited_scenario
    st.session_state.generation_mode = "single"
else:
    # 2パートモード: シナリオを2分割
    # 文を分割
    sentences = [s.strip() + '。' for s in original_summary.split('。') if s.strip()]
    mid_point = len(sentences) // 2

    part1_default = ''.join(sentences[:mid_point])
    part2_default = ''.join(sentences[mid_point:])

    # 各パートの推奨文字数
    max_chars_per_part = int(duration * 6)

    st.markdown("#### Part 1 シナリオ（前半）")
    edited_scenario_part1 = st.text_area(
        "Part 1で話す内容",
        value=part1_default,
        height=200,
        key="scenario_part1"
    )
    char_count_p1 = len(edited_scenario_part1.replace('\n', '').replace(' ', ''))
    if char_count_p1 > max_chars_per_part:
        st.warning(f"⚠️ Part 1: {char_count_p1}文字（推奨{max_chars_per_part}文字以内）")
    else:
        st.success(f"✅ Part 1: {char_count_p1}文字")

    st.markdown("#### Part 2 シナリオ（後半）")
    edited_scenario_part2 = st.text_area(
        "Part 2で話す内容",
        value=part2_default,
        height=200,
        key="scenario_part2"
    )
    char_count_p2 = len(edited_scenario_part2.replace('\n', '').replace(' ', ''))
    if char_count_p2 > max_chars_per_part:
        st.warning(f"⚠️ Part 2: {char_count_p2}文字（推奨{max_chars_per_part}文字以内）")
    else:
        st.success(f"✅ Part 2: {char_count_p2}文字")

    st.session_state.edited_scenario_part1 = edited_scenario_part1
    st.session_state.edited_scenario_part2 = edited_scenario_part2
    st.session_state.generation_mode = "two_part"

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

# 総尺の計算
if st.session_state.get('generation_mode') == 'two_part':
    total_duration = video_duration * 2
    display_duration = f"{video_duration}秒 × 2パート = {total_duration}秒"
else:
    total_duration = video_duration
    display_duration = f"{video_duration}秒"

st.info(f"""
**設定サマリー**
- モード: {generation_mode}
- アスペクト比: {scenario.get('aspect_ratio', '16:9')}
- ビジュアルスタイル: {scenario.get('visual_style', 'Photorealistic')}
- 動画の長さ: {display_duration}
- シーン数: {num_scenes}シーン/パート
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
        aspect_ratio = scenario.get('aspect_ratio', '16:9')

        # プロンプトを生成（裏側で実行）
        if st.session_state.get('generation_mode') == 'two_part':
            # 2パート用プロンプト生成
            prompt_part1 = prompt_engineer.create_sora2_prompt(
                scenario=scenario,
                aspect_ratio=aspect_ratio,
                visual_style=scenario.get('visual_style', 'Photorealistic'),
                duration=video_duration,
                part=1,
                total_parts=2,
                narration_text=st.session_state.get('edited_scenario_part1', '')
            )
            prompt_part2 = prompt_engineer.create_sora2_prompt(
                scenario=scenario,
                aspect_ratio=aspect_ratio,
                visual_style=scenario.get('visual_style', 'Photorealistic'),
                duration=video_duration,
                part=2,
                total_parts=2,
                narration_text=st.session_state.get('edited_scenario_part2', '')
            )
        else:
            # シングル用プロンプト生成
            single_prompt = prompt_engineer.create_sora2_prompt(
                scenario=scenario,
                aspect_ratio=aspect_ratio,
                visual_style=scenario.get('visual_style', 'Photorealistic'),
                duration=video_duration,
                narration_text=st.session_state.get('edited_scenario', '')
            )

        if st.session_state.get('generation_mode') == 'two_part':
            # 2パートモード
            with st.spinner("🎬 Part 1を生成中... (12秒)"):
                try:
                    st.write(f"DEBUG: Part 1 - アスペクト比 = {aspect_ratio}, Duration = {video_duration}")

                    # プロンプトデバッグ表示
                    with st.expander("🔍 Part 1 プロンプト（デバッグ）"):
                        st.text(prompt_part1[:1000] + "..." if len(prompt_part1) > 1000 else prompt_part1)

                    result_part1 = sora2_engine.generate_video(
                        prompt=prompt_part1,
                        book_name=scenario['book_name'],
                        aspect_ratio=aspect_ratio,
                        duration=video_duration
                    )

                    if result_part1['status'] != 'success':
                        st.error(f"❌ Part 1生成エラー: {result_part1.get('error', '不明なエラー')}")
                        st.stop()

                    st.success("✅ Part 1完了！")

                except Exception as e:
                    st.error(f"❌ Part 1エラー: {str(e)}")
                    st.exception(e)
                    st.stop()

            with st.spinner("🎬 Part 2を生成中... (12秒)"):
                try:
                    st.write(f"DEBUG: Part 2 - アスペクト比 = {aspect_ratio}, Duration = {video_duration}")

                    result_part2 = sora2_engine.generate_video(
                        prompt=prompt_part2,
                        book_name=scenario['book_name'],
                        aspect_ratio=aspect_ratio,
                        duration=video_duration
                    )

                    if result_part2['status'] != 'success':
                        st.error(f"❌ Part 2生成エラー: {result_part2.get('error', '不明なエラー')}")
                        st.stop()

                    st.success("✅ Part 2完了！")

                except Exception as e:
                    st.error(f"❌ Part 2エラー: {str(e)}")
                    st.exception(e)
                    st.stop()

            # 動画を結合
            with st.spinner("🔗 動画を結合中..."):
                try:
                    video_files = [result_part1['video_file'], result_part2['video_file']]
                    concatenated_file = video_composer.concatenate_videos(video_files)

                    # 結合結果を保存
                    final_result = {
                        'video_file': concatenated_file,
                        'prompt': f"Part 1:\n{prompt_part1[:500]}...\n\nPart 2:\n{prompt_part2[:500]}...",
                        'aspect_ratio': aspect_ratio,
                        'duration': total_duration,
                        'generation_id': f"{result_part1['generation_id']}+{result_part2['generation_id']}",
                        'status': 'success',
                        'parts': [result_part1, result_part2]
                    }

                    st.session_state.generated_video = final_result
                    st.success("✅ 2パート動画の結合が完了しました！")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ 結合エラー: {str(e)}")
                    st.exception(e)

        else:
            # シングルモード
            with st.spinner("🎬 Sora2で動画を生成中..."):
                try:
                    st.write(f"DEBUG: アスペクト比 = {aspect_ratio}, Duration = {video_duration}")

                    # Sora2で動画生成
                    result = sora2_engine.generate_video(
                        prompt=single_prompt,
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

    # 2パートモードの場合、個別パートも表示
    if video_result.get('parts'):
        st.markdown("### 📹 個別パート")
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown("**Part 1**")
            part1 = video_result['parts'][0]
            if part1['video_file'] and part1['video_file'].exists():
                st.video(str(part1['video_file']))
                with open(part1['video_file'], 'rb') as f:
                    st.download_button(
                        "📥 Part 1をダウンロード",
                        data=f.read(),
                        file_name=f"part1_{scenario['book_name']}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

        with col_p2:
            st.markdown("**Part 2**")
            part2 = video_result['parts'][1]
            if part2['video_file'] and part2['video_file'].exists():
                st.video(str(part2['video_file']))
                with open(part2['video_file'], 'rb') as f:
                    st.download_button(
                        "📥 Part 2をダウンロード",
                        data=f.read(),
                        file_name=f"part2_{scenario['book_name']}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )

        st.markdown("---")
        st.markdown("### 🎬 結合版")

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
