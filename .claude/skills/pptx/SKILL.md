---
name: pptx
description: 調査結果からPython-PPTXで高品質なプレゼン資料を生成する。デザインシステムに基づくレイアウト自動選択、Vertex AI画像生成に対応。
---

# PowerPoint Generation Skill

## 手順

1. ユーザーの要件を確認:
   - スライドの目的（提案書、報告書、競合分析プレゼン等）
   - ベースにする調査レポート（`output/` 内のファイル指定、または会話中の内容）
   - スライド枚数の目安
   - デザインの方向性（指定がなければ「クリーン × プロフェッショナル」）
   - 画像生成の要否（インフォグラフィック、概念図、イメージ写真等）
2. `output/` 内の関連レポートがあれば読み込む
3. 大量のスライド（20枚以上）の場合は、まず構成案を提示してから生成に進む
4. Python-PPTX がインストールされているか確認。なければ `pip install python-pptx` を実行
5. 以下のデザインシステムに従い、Pythonスクリプトを**1ファイルで**作成し実行
6. 生成したPPTXファイルを `output/` に出力し、パスを報告。各スライドのタイトルと概要を表示

---

## デザインシステム

### スライドグリッド（固定値）

```python
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN

SLIDE_W = Inches(13.333)  # 16:9 ワイド
SLIDE_H = Inches(7.5)
MARGIN_X = Inches(0.8)    # 左右マージン
MARGIN_TOP = Inches(0.6)  # 上マージン
MARGIN_BOTTOM = Inches(0.5)
CONTENT_W = SLIDE_W - MARGIN_X * 2  # コンテンツ幅 = 11.733"
CONTENT_H = SLIDE_H - MARGIN_TOP - MARGIN_BOTTOM
CARD_GAP = Inches(0.3)    # カード間ギャップ
CARD_RADIUS = Inches(0.15)  # カード角丸
```

### デフォルトカラーパレット

トーンに応じて差し替える。指定がなければ以下をデフォルトとして使用:

```python
from pptx.dml.color import RGBColor

COLORS = {
    "primary":    RGBColor(0x1A, 0x1A, 0x2E),  # ダークネイビー — 見出し・強調
    "secondary":  RGBColor(0x4A, 0x5A, 0x7A),  # スレートブルー — サブ見出し
    "accent":     RGBColor(0x2D, 0x8C, 0xF0),  # ブルーアクセント — 数値・ハイライト
    "accent_warm":RGBColor(0xF0, 0x6B, 0x2D),  # オレンジ — CTA・警告的強調
    "bg":         RGBColor(0xFF, 0xFF, 0xFF),   # 白 — スライド背景
    "surface":    RGBColor(0xF5, 0xF5, 0xF8),   # 淡グレー — カード背景
    "text":       RGBColor(0x33, 0x33, 0x33),   # ダークグレー — 本文
    "muted":      RGBColor(0x99, 0x99, 0x99),   # ミューテッド — キャプション・注釈
    "border":     RGBColor(0xE0, 0xE0, 0xE0),   # ボーダー — 区切り線
    "success":    RGBColor(0x2D, 0xA0, 0x6F),   # グリーン — ポジティブ指標
    "danger":     RGBColor(0xE0, 0x4F, 0x5F),   # レッド — ネガティブ指標
}
```

トーン別パレット差し替え例:

- **ナチュラル × フェミニン**: primary=#5C4A3A, accent=#C87B6B, surface=#FAF5EE
- **モダン × スタイリッシュ**: primary=#111111, accent=#6C5CE7, surface=#F8F8FC, bg=#FAFAFA
- **ポップ × フレンドリー**: primary=#2D3436, accent=#FF7675, surface=#FFF3E0

### タイポグラフィ

```python
FONT = {
    "ja": "Noto Sans JP",
    "en": "Arial",
    "title":   {"size": Pt(32), "bold": True,  "color": COLORS["primary"]},
    "heading": {"size": Pt(24), "bold": True,  "color": COLORS["primary"]},
    "subhead": {"size": Pt(18), "bold": True,  "color": COLORS["secondary"]},
    "body":    {"size": Pt(16), "bold": False, "color": COLORS["text"]},
    "caption": {"size": Pt(12), "bold": False, "color": COLORS["muted"]},
    "number":  {"size": Pt(48), "bold": True,  "color": COLORS["accent"]},
}
```

1スライド内のフォントサイズは3段階まで。行間は本文で1.4〜1.6倍。

### 情報設計（スライドの流れ）

目的に応じてストーリーを組み立てる:

- **提案書**: 表紙 → エグゼクティブサマリー → 現状分析 → 課題提起 → 解決策 → 施策詳細 → 期待効果 → ネクストステップ
- **報告書**: 表紙 → サマリー → 調査背景 → 主要発見 → 詳細分析 → 考察 → 推奨アクション
- **競合分析**: 表紙 → 市場概況 → 競合マッピング → 比較マトリクス → 差別化 → 戦略提案

最初のスライドで「何について・結論は何か」を一言で伝える。詳細は後に回す。

### トーン&マナー

クライアント・目的に合わせて印象を制御する:

- コンサル提案 → クリーン × コーポレート（信頼感・整然）
- クリエイティブ提案 → モダン × スタイリッシュ（洗練・先進性）
- 女性向けサービス → ナチュラル × フェミニン（柔らかさ・上品）
- スタートアップ → ポップ × フレンドリー（親しみ・勢い）

---

## レイアウトブループリント

コンテンツの性質に応じてレイアウトを**自動選択**する。同じレイアウトを3枚以上連続させない（視覚的リズム）。

### A. 表紙（Title）

大きなタイトル + サブタイトル + 日付/会社名。下部にアクセントバー。

```
┌─────────────────────────────────┐
│                                 │
│         [タイトル 32pt]          │
│        [サブタイトル 18pt]       │
│                                 │
│   ───────── accent bar ─────    │
│         [日付 / 社名 12pt]      │
└─────────────────────────────────┘
```

### B. セクション区切り（Divider）

章の切り替え。背景をPrimary色で塗り、白文字。

```
┌━━━━━━ primary bg ━━━━━━━━━━━━━┐
│                                 │
│      [セクション名 32pt 白]      │
│      [補足テキスト 16pt 白]      │
│                                 │
└━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┘
```

### C. タイトル+本文（Standard）

上部にタイトル、下部にコンテンツ。最も基本的なレイアウト。

```
┌─────────────────────────────────┐
│ [タイトル 24pt]                  │
│ ─── border line ───              │
│                                 │
│ [本文 / 箇条書き 16pt]          │
│                                 │
│                       [出典 12pt]│
└─────────────────────────────────┘
```

### D. 2カラム（Split）

左テキスト + 右ビジュアル、または左右比較。

```
┌─────────────────────────────────┐
│ [タイトル 24pt]                  │
│ ┌──────────┐  ┌──────────┐     │
│ │  テキスト  │  │ 画像/図解 │     │
│ │  or 左項目 │  │ or 右項目 │     │
│ └──────────┘  └──────────┘     │
└─────────────────────────────────┘
左右比率: 50:50 または 55:45。カラム間ギャップ = CARD_GAP
```

### E. カードグリッド（Cards）

3〜4枚のカードを横並び。各カードはsurface色の角丸矩形。

```
┌─────────────────────────────────┐
│ [タイトル 24pt]                  │
│ ┌────────┐┌────────┐┌────────┐ │
│ │ accent  ││ accent  ││ accent  │ │
│ │ bar top ││ bar top ││ bar top │ │
│ │ 見出し  ││ 見出し  ││ 見出し  │ │
│ │ 本文    ││ 本文    ││ 本文    │ │
│ └────────┘└────────┘└────────┘ │
└─────────────────────────────────┘
カード幅 = (CONTENT_W - CARD_GAP * (n-1)) / n
カード背景 = COLORS["surface"]、角丸 = CARD_RADIUS
カード上辺にaccent色の細いバー（高さ4pt）でモダンな印象
```

### F. KPI・数値ハイライト（Number）

大きな数値を中心に据え、インパクトを出す。

```
┌─────────────────────────────────┐
│ [タイトル 24pt]                  │
│ ┌────────┐┌────────┐┌────────┐ │
│ │  48pt   ││  48pt   ││  48pt   │ │
│ │ 数値    ││ 数値    ││ 数値    │ │
│ │ accent  ││ accent  ││ accent  │ │
│ │ ラベル  ││ ラベル  ││ ラベル  │ │
│ │ 16pt    ││ 16pt    ││ 16pt    │ │
│ └────────┘└────────┘└────────┘ │
└─────────────────────────────────┘
```

### G. 比較テーブル（Table）

ヘッダー行はPrimary背景+白文字。交互に行色を変えて視認性確保。

### H. 全面ビジュアル（Visual）

背景画像 + 半透明オーバーレイ + 短いコピー。インパクトスライド用。

### コンテンツ→レイアウト自動選択ルール

| コンテンツの性質       | レイアウト  |
| ---------------------- | ----------- |
| 章の切り替え           | B. Divider  |
| 3〜4個の並列ポイント   | E. Cards    |
| 主要な数値・KPI        | F. Number   |
| テキスト + 図解/画像   | D. Split    |
| 比較表・マトリクス     | G. Table    |
| 箇条書き・プロセス説明 | C. Standard |
| インパクト・ビジョン   | H. Visual   |

### 視覚的リズム

- 同じレイアウトを **3枚以上連続させない**
- 5〜7枚ごとに **Divider** を挟んでセクション感を出す
- Standard が続きそうなら Cards や Split に変換できないか検討する
- Number スライドは **最も伝えたい数値** に絞る（乱用しない）

---

## 実装パターン

### カード背景の作り方

```python
from pptx.enum.shapes import MSO_SHAPE

def add_card(slide, left, top, width, height, fill_color, accent_color=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    shape.shadow.inherit = False
    adj = shape.adjustments
    if len(adj) > 0:
        adj[0] = 0.03

    if accent_color:
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            left, top, width, Pt(4)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_color
        bar.line.fill.background()
    return shape
```

### テキスト設定ヘルパー

```python
def set_text(textframe, text, font_spec, alignment=PP_ALIGN.LEFT):
    textframe.clear()
    textframe.word_wrap = True
    p = textframe.paragraphs[0]
    p.text = text
    p.font.name = FONT["ja"]
    p.font.size = font_spec["size"]
    p.font.bold = font_spec.get("bold", False)
    p.font.color.rgb = font_spec.get("color", COLORS["text"])
    p.alignment = alignment
    p.space_after = Pt(6)
    p.line_spacing = 1.5
```

---

## 画像生成（Vertex AI）

プレゼンにビジュアルが必要な場合、Vertex AI で画像を生成しスライドに挿入する。

- **Nano Banana Pro**（`gemini-3-pro-image-preview`）: インフォグラフィック、ブランド素材、複雑な構図
- **Nano Banana 2**（`gemini-3.1-flash-image`）: 概念図、イメージ写真、シンプルなビジュアル
- GCPプロジェクト: `servertest-337307`

```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project="servertest-337307",
    location="us-central1"
)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="プロンプト",
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"]
    )
)

# response から画像バイトを取得し output/images/ に保存
```

画像生成前に `google-genai` がインストールされているか確認。なければ `pip install google-genai` を実行。
生成画像は `output/images/` に保存してからPPTXに挿入する。

---

## 正確性（general.md「成果物の正確性プロトコル」準拠）

スライドに数値・主張を載せる際は、general.md の9項目を適用する。特にスライドで頻発する問題:

- **スコープ先確定**: 分析対象を列挙してからスライド作成に入る。「全件」「一極集中」等の総括語は母集団を数え上げた場合のみ使用
- **両面提示**: 有利な指標だけのグラフ・表を作らない。反する事実を同じスライドに併記
- **証拠クラス**: 実測値・業界一般値・仮説を区別し、スライド上に明記（注釈でも可）
- **内部整合性**: 繰り返し登場する数値・定義がスライド間で矛盾していないか全件照合
- **敵対的検証**: 完成後、fact-checker エージェントで全スライドの主張を反証ベースで検証してから報告

## 禁止事項

- AI丸出しのテンプレートデザイン（全スライド同じレイアウト、変化のない構成）
- 絵文字やクリップアートの使用
- 過剰な装飾（グラデーション背景、ドロップシャドウ多用、3D効果）
- 1スライドに箇条書き7項目以上
- データの推測・創作。調査レポートまたはユーザー提供データのみ使用
- Python-PPTX 以外のスライド生成ライブラリの使用
- 色の直接指定ハードコード（必ず COLORS 辞書経由で参照する）

---

## 本プロジェクト固有の設定（望月リソルGC）

テンプレート由来の上記デザインシステムに、この案件の実環境に合わせた差分を定義する。**同期で戻さないこと。**

### 出力先

`output/` に出力する。`deck/` は使わない。

### フォント（テンプレートからの差し替え）

```python
FONT["ja"] = "Yu Gothic"   # ← テンプレート既定の "Noto Sans JP" から差し替え
```

**理由**: Noto Sans JP は当開発環境にも、想定されるクライアント環境（Windows / PowerPoint）にも未導入の可能性が高く、
代替フォントで表示が崩れる。**游ゴシックは Windows 8.1+ / macOS 標準**で確実に表示できる。
`Noto Sans JP` が全関係者の環境に入ったことを確認できたら、テンプレート既定に戻してよい。

### デザインフォーマット（参照資料に準拠）

**基準資料**: `営業本部共有_買取シミュレーター_2026-07.pptx`（adsim-reuse / agentic-advertising-skills）
テンプレート既定のデザインシステムより、**こちらの実測トークンを優先**する。

```python
FONT_JA = "Meiryo"          # 単一フォント。英数もMeiryo
COLORS = {
    "primary":     "405D7B",  # スレートブルー — ヘッダ・表ヘッダ・濃色パネル
    "primary_dk":  "334A62",  # タイトル下の短バー
    "accent":      "A96933",  # カッパー — 強調・カードのアクセントバー
    "gray":        "6C7582",  # 第3系統
    "ink":         "2A2E33",  # 見出し
    "text":        "454B52",  # 本文
    "muted":       "8A929C",  # 注釈
    "slate_lt":    "8FA3B8",  # 濃色面上の補助文字
    "surface":     "F2F4F7",  # カード面
    "surface_alt": "EEF0F3",  # 表の交互行
    "border":      "E2E6EB",  # ヘアライン
    "hairline":    "D6DBE1",  # 表紙の区切り線
}
```

| 要素         | 仕様                                                                                                                                                                                  |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 図形         | **すべて直角の RECTANGLE。角丸を使わない**（参照資料の角丸figure数＝0）                                                                                                               |
| 影           | 装飾矩形は `shadow.inherit = False`                                                                                                                                                   |
| グリッド     | 左マージン `0.62` ／ コンテンツ幅 `12.10` ／ タイトルのみ `x=0.58 w=12.00`                                                                                                            |
| ヘッダ       | 縦バー(`0.09×0.26` primary @ y=0.50) ＋ キッカー11.5pt @ x=0.80 → タイトル**27pt** @ y=0.80 → 短バー(`1.75×0.05` primary_dk @ y=1.53) ＋ 全幅ヘアライン(`12.10×0.01` border @ y=1.55) |
| 本文開始     | `y = 1.90`                                                                                                                                                                            |
| フッタ       | **ページ番号のみ**（`x=12.40 y=7.12 w=0.70`・10.5pt・右寄せ）。罫線・社名を置かない                                                                                                   |
| カード       | `surface` の面 ＋ **上辺 0.05in のアクセントバー**。3カラム幅 `3.90`／2カラム幅 `5.95`／ギャップ `0.20`                                                                               |
| 表           | ヘッダ `primary` 背景＋白文字 → 行は `bg` / `surface_alt` の交互。セルは個別の矩形＋テキストボックス                                                                                  |
| 箇条書き     | 自動bulletを使わず `･` プレフィックス、`line_spacing = 1.2〜1.5`                                                                                                                      |
| 文字サイズ   | 33（表紙）／27（タイトル）／22／16／15.5／13.5／13／12.5／12／11.5／10.5／9.5／8.5                                                                                                    |
| フォント指定 | **run単位で設定する**（段落レベルだけだと環境によって効かない）                                                                                                                       |

**巨大な数値（48pt等）は使わない。** 参照資料の最大は表紙33pt・タイトル27pt。KPIも27〜30ptに収める。

### 🛑 提出版に載せてはならないもの（案件固有）

`.claude/rules/general.md`「成果物の正確性プロトコル」第8項の具体化。

| 項目                                        | 提出版                            | 社内版     |
| ------------------------------------------- | --------------------------------- | ---------- |
| ご請求額（売上ベース）・構成比              | ✅                                | ✅         |
| **原価・粗利・粗利率・マージン率**          | 🛑 **禁止**                       | ✅         |
| **媒体実費（各媒体APIの実測消化額）**       | 🛑 **禁止**                       | ✅         |
| CPC・CPM・CPA                               | ✅ **請求額から算出したもののみ** | 実費版も可 |
| セッション・CV・CTR・到達率・地域・デバイス | ✅                                | ✅         |
| 個人情報（氏名・住所詳細・電話・メール）    | 🛑 **禁止**（集計のみ）           | 集計のみ   |

**請求額と実費を並べるとマージンが逆算される。** 生成後に必ず機械チェックを回す:

```bash
python3 - <<'PY'
from pptx import Presentation
p = Presentation("output/<file>.pptx")
t = "\n".join(sh.text_frame.text for s in p.slides for sh in s.shapes if sh.has_text_frame)
banned = ["原価", "粗利", "マージン", "実費"]  # + 実費の具体数値
print([b for b in banned if b in t] or "OK")
PY
```
