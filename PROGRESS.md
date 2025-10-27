# 開発進捗状況

最終更新: 2025-10-27

## ✅ 完了した項目

### 1. Sora2 API動作確認 ✅
- **test_sora2.py**: 3パターンのテスト実装
  - Test 1 (simple English, 4s): ✅ Success
  - Test 2 (Japanese narration, 12s): ✅ Success (1.8MB)
  - Test 3 (70 chars, 12s): ⚠️ Generation OK but download 404

### 2. 404エラーの原因特定 ✅
**実在人物名がNGでした！**
- ❌ 「井上尚弥」などの実名 → 404 Error
- ✅ 架空のストーリー → Success

**Sora2コンテンツ制限:**
- 実在人物名は使用不可（公人・一般人問わず）
- 著作権キャラクター・音楽は不可
- 18歳未満向けコンテンツのみ
- 人間の顔を含む入力画像は拒否

### 3. 3シーン生成→結合フロー成功 ✅
**test_scene_flow.py: 完全成功**
```
シーン1: 43文字 → 2.4MB ✅
シーン2: 43文字 → 2.4MB ✅
シーン3: 44文字 → 2.5MB ✅
結合: 36秒 → 7.3MB ✅
```

**成功パターン（厳守）:**
```python
prompt = f"""Book promotional video, 12 seconds, cinematic style, 16:9.
Japanese voice-over with background music.

Voice-over (Japanese): {narration}"""
```

### 4. バックエンド実装 ✅
- **backend/prompt_engineer.py**
  - `create_scene_prompt_for_sora2()`: Test 2成功パターン厳守
  - コンテンツ制限の警告追加

- **backend/scene_splitter_sora2.py**
  - Geminiで3シーン分割（40-50文字/シーン）
  - 実在人物名を代名詞に自動置換
  - 3シーン構成: 導入（続く...）→ 展開（緊張感）→ 結末（完結）

- **backend/sora2_engine.py**
  - ダウンロードリトライ機能（3回、5秒間隔）

- **backend/video_composer.py**
  - moviepyで動画結合（既存）

### 5. セッション管理基盤 ✅
- **backend/session_manager.py**: 実装済み
- JSON形式で保存（タイムスタンプ + latest）
- Pathオブジェクトの文字列変換対応

### 6. UI改善 ✅
- **app.py**: ステップバッジ、デバッグ情報、セッション復元UI
- **pages/2_scenario_editor.py**: シーン数を3固定、説明更新
- **pages/3_sora2_generate.py**: セッション保存統合（既存フロー）

---

## ✅ 新規実装完了（このセッション）

### 1. pages/3_sora2_generate.py の完全書き換え ✅
**完了:** シーンベースワークフローに完全移行

**実装内容:**
```
✅ Step 1: シーン分割
  - scene_splitter_sora2.split_into_scenes_for_sora2() 統合
  - 3シーン表示（各40-50文字）
  - ユーザーがナレーション編集可能（文字数警告付き）

✅ Step 2: 各シーン生成
  - シーン1生成 → 保存 → プレビュー表示
  - シーン2生成 → 保存 → プレビュー表示
  - シーン3生成 → 保存 → プレビュー表示
  - セッション保存（途中からの再開対応）
  - 個別シーンダウンロードボタン

✅ Step 3: 最終結合
  - video_composer.concatenate_videos()
  - 36秒動画完成
  - ダウンロードボタン
  - 動画情報表示（長さ、ファイルサイズ、シーン数）
```

**使用パターン:**
- test_scene_flow.py の成功パターンを厳密に再現
- prompt_engineer.create_scene_prompt_for_sora2() を使用
- Test 2 成功フォーマット厳守

### 2. セッション復元機能の修正 ✅
**完了:** シーンベース生成に対応

**修正内容:**
- ✅ app.py のセッション復元ロジック更新
  - scenes 配列の復元
  - scene_videos 辞書の復元（Path変換対応）
  - final_video の復元
- ✅ 3_sora2_generate.py での自動セッション保存
  - 各シーン生成後に即座に保存
  - 最終結合後に完了ステータス保存
- ✅ シーン別動画ファイルの保存・復元対応

### 3. コンテンツ制限の注意表示 ✅
**完了:** 3_sora2_generate.py に警告ボックス追加

**実装内容:**
- ✅ ページ上部に目立つ警告ボックス表示
- ✅ 実在人物名使用不可の明記
- ✅ 著作権物使用不可の明記
- ✅ 18歳以上向けコンテンツ制限の明記
- ✅ 自動代名詞置換の説明

## ⚠️ 今後の改善項目（オプション）

### 1. EPUBアップロード画面への警告追加 🟡
- pages/1_upload_epub.py にコンテンツ制限警告を追加
- アップロード前に注意喚起

### 2. シナリオ編集画面への警告追加 🟡
- pages/2_scenario_editor.py に警告を追加
- 実在人物名検出機能（オプション）

### 3. エラーハンドリング強化 🟡
- Sora2 API エラー時の詳細メッセージ
- リトライ機能の UI 表示

---

## 📋 技術仕様まとめ

### Sora2成功パターン
```python
# プロンプト（このフォーマット厳守）
prompt = f"""Book promotional video, 12 seconds, cinematic style, 16:9.
Japanese voice-over with background music.

Voice-over (Japanese): {narration}"""

# API呼び出し
video = client.videos.create_and_poll(
    model="sora-2",
    prompt=prompt,
    seconds="12",
    size="1280x720"
)
content = client.videos.download_content(video.id)
```

### ナレーション長
- **推奨: 40-50文字/シーン**
- 12秒動画 ÷ 6文字/秒 = 72文字が理論値
- 実測: 43-44文字で安定

### 3シーン構成
1. **シーン1 (導入)**: 問題提起、「戦いが始まる」「旅立つ」
2. **シーン2 (展開)**: 困難や葛藤、「敗北を知る」「試練に立ち向かう」
3. **シーン3 (結末)**: タイトル表示、「物語が動き出す」「感動の結末へ」

### コンテンツ制限
- ❌ 実在人物名（公人・一般人）
- ❌ 著作権キャラクター・音楽
- ❌ 18歳以上向けコンテンツ
- ✅ 架空のストーリー・キャラクター

---

## 🗂️ 重要ファイル

### バックエンド
- `backend/sora2_engine.py` - Sora2 API統合（リトライ機能付き）
- `backend/prompt_engineer.py` - プロンプト生成（成功パターン）
- `backend/scene_splitter_sora2.py` - シーン分割（Gemini使用）
- `backend/video_composer.py` - 動画結合（moviepy）
- `backend/session_manager.py` - セッション保存・復元

### テストスクリプト
- `test_sora2.py` - Sora2 API動作確認（3パターン）
- `test_scene_flow.py` - 3シーン生成→結合フルフロー ✅成功

### フロントエンド
- `app.py` - ホーム（ステップバッジ、セッション復元UI）
- `pages/1_upload_epub.py` - EPUBアップロード
- `pages/2_scenario_editor.py` - シナリオ選択（3シーン固定）
- `pages/3_sora2_generate.py` - 動画生成 **← 要書き換え**

### 生成物
- `test_scene_output/scene_1.mp4` (2.4MB)
- `test_scene_output/scene_2.mp4` (2.4MB)
- `test_scene_output/scene_3.mp4` (2.5MB)
- `test_scene_output/final_combined.mp4` (7.3MB) ✅

---

## 🚀 次のステップ

### 必須タスク
1. **エンドツーエンドテスト**
   - ローカルで完全なフロー確認
   - EPUB → シナリオ → シーン分割 → 生成 → 結合
   - セッション復元のテスト

2. **Streamlit Cloud デプロイ**
   - 環境変数設定（OPENAI_API_KEY, GOOGLE_API_KEY）
   - moviepy動作確認
   - ファイル保存パスの確認

### オプション改善
3. **追加の警告表示**
   - pages/1_upload_epub.py に警告追加
   - pages/2_scenario_editor.py に警告追加

4. **エラーハンドリング強化**
   - Sora2 APIエラーの詳細表示
   - リトライUI実装

---

## 📝 メモ

- Sora2 API料金は高額（12秒で約$10程度？）なので、セッション保存は必須
- Test 2の成功パターン（43文字）が最も安定
- 実在人物名検出はGeminiに任せる（自動置換）
- moviepyはStreamlit Cloud対応（ffmpegより推奨）
