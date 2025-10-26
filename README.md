# 書籍プロモーション動画ジェネレーター - Sora2版

EPUBファイルから自動的にプロモーション動画を生成するStreamlitアプリケーション（OpenAI Sora2使用）

## 🎬 Sora2版の特徴

- **⚡ 超高速**: 1-3分で動画生成完了
- **🎨 高品質**: Sora2による映画品質の動画
- **✨ シンプル**: わずか3ステップで完成
- **🤖 AI駆動**: Gemini 2.5による書籍分析 + Sora2による動画生成

## 通常版との違い

| 項目 | 通常版 | Sora2版 |
|------|--------|---------|
| ページ数 | 6ページ | 3ページ |
| 処理時間 | 5-10分 | 1-3分 |
| 動画生成 | シーン分割→画像→音声→結合 | Sora2一撃生成 |
| カスタマイズ性 | 高（詳細編集可） | 低（スタイル選択のみ） |
| 用途 | 本格的な動画制作 | 高速プロトタイピング・デモ |

## 必要な環境

- Python 3.10+
- OpenAI API キー（**Sora2アクセス権限必須**）
- Google Gemini API キー

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/sato-G/book-promo-sora2-demo.git
cd book-promo-sora2-demo
```

### 2. 仮想環境の作成と有効化

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example` をコピーして `.env` ファイルを作成：

```bash
cp .env.example .env
```

`.env` ファイルに以下の情報を記入：

```
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 5. アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` を開きます。

## Streamlit Cloud へのデプロイ

### 1. GitHub リポジトリにプッシュ

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/book-promo-sora2-demo.git
git push -u origin main
```

### 2. Streamlit Cloud でデプロイ

1. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubアカウントでログイン
3. "New app" をクリック
4. リポジトリを選択
5. Main file path: `app.py`
6. Advanced settings で以下の環境変数を設定：
   - `OPENAI_API_KEY` （Sora2アクセス権限必須）
   - `GOOGLE_API_KEY`
7. "Deploy" をクリック

## 使い方

### Step 1: EPUB アップロード
- EPUBファイルをアップロード
- 書籍情報が自動解析されます

### Step 2: シナリオ選択
- 複数のシナリオパターンから選択
- 対象読者層とビジュアルスタイルを設定
- アスペクト比を選択（16:9, 9:16, 1:1）

### Step 3: Sora2動画生成
- 自動生成されたプロンプトを確認・編集
- 動画の長さを設定（5-60秒）
- Sora2で一撃生成
- プレビューとダウンロード

## 技術スタック

- **フレームワーク:** Streamlit
- **動画生成:** OpenAI Sora2
- **AI分析:**
  - Google Gemini 2.5 Flash Lite（書籍分析）
  - OpenAI GPT-4（プロンプトエンジニアリング）
- **EPUB解析:** ebooklib

## ディレクトリ構造

```
book-promo-sora2-demo/
├── app.py                    # メインエントリポイント
├── requirements.txt          # Python依存パッケージ
├── .env                      # 環境変数（gitignore）
├── .gitignore
├── README.md
├── .streamlit/
│   ├── config.toml          # Streamlit設定
│   └── secrets.toml         # シークレット（gitignore）
├── backend/                 # バックエンドモジュール
│   ├── __init__.py
│   ├── book_analyzer.py     # 書籍分析
│   ├── epub_parser.py       # EPUB解析
│   ├── scenario_generator_v2.py  # シナリオ生成
│   ├── summary_generator.py # 要約生成
│   ├── sora2_engine.py      # Sora2 API統合
│   ├── prompt_engineer.py   # プロンプトエンジニアリング
│   └── utils.py             # ユーティリティ
├── pages/                   # Streamlitページ
│   ├── 1_upload_epub.py     # Step 1: EPUBアップロード
│   ├── 2_scenario_editor.py # Step 2: シナリオ選択
│   └── 3_sora2_generate.py  # Step 3: Sora2生成
└── data/                    # データディレクトリ（gitignore）
    ├── uploaded/            # アップロードファイル
    └── output/              # 生成動画
        └── sora2_videos/    # Sora2生成動画
```

## ⚠️ 重要な注意事項

### Sora2 APIについて

2025年1月時点で、Sora2 APIは**限定プレビュー中**です：

1. **アクセス権限**: OpenAI API keyに加えて、Sora2へのアクセス権限が必要
2. **料金**: Sora2の利用には別途料金がかかります
3. **API仕様**: 正式リリース時にAPI仕様が変更される可能性があります

### コスト

- OpenAI Sora2: 動画生成あたりの料金（詳細はOpenAI公式を確認）
- Google Gemini API: テキスト分析（無料枠あり）

### 制限事項

- Streamlit Cloud の無料プランではリソース制限があります
- 動画ファイルサイズが大きくなる場合があります
- Sora2の生成時間は動画の長さや複雑さにより変動します

## ライセンス

MIT License

## 作者

Sato

## 関連リンク

- [通常版リポジトリ](https://github.com/sato-G/book-promo-video-generator)
- [OpenAI Sora2](https://openai.com/sora)
- [Streamlit](https://streamlit.io)
