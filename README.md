# 望月リソルゴルフクラブ LP — 運用手順書

## プロジェクト情報

| 項目 | 値 |
|------|---|
| GCPプロジェクトID | `servertest-337307` |
| GCSバケット名（仮） | `mochizuki-gc-lp` |
| 要件定義書 | LP制作_要件定義書_望月ゴルフクラブ_v1.4.md |

---

## ファイル構成

```
mochizuki-gc-lp/
├── index.html          ← LP本体（全セクション1ファイル完結）
├── css/
│   └── style.css       ← メインスタイル
├── js/
│   ├── main.js         ← ナビ・スクロール・アニメーション
│   └── form.js         ← フォーム送信（SendGrid / Cloud Functions）
├── images/             ← 画像ディレクトリ（下記参照）
└── README.md           ← 本ファイル
```

---

## GCS デプロイ手順

### 初回セットアップ

```bash
# 1. GCPプロジェクト設定
gcloud config set project servertest-337307

# 2. バケット作成（仮名 / ドメイン確定後に変更）
gcloud storage buckets create gs://mochizuki-gc-lp \
  --location=ASIA-NORTHEAST1 \
  --uniform-bucket-level-access

# 3. 公開設定
gcloud storage buckets add-iam-policy-binding gs://mochizuki-gc-lp \
  --member=allUsers \
  --role=roles/storage.objectViewer

# 4. ウェブサイト設定
gcloud storage buckets update gs://mochizuki-gc-lp \
  --web-main-page-suffix=index.html \
  --web-error-page=index.html

# 5. 初回アップロード
gcloud storage cp -r ./* gs://mochizuki-gc-lp/ \
  --exclude=".git/*" --exclude="README.md"
```

### 更新デプロイ（差分のみ）

```bash
gcloud storage rsync -r -d . gs://mochizuki-gc-lp \
  --exclude=".git/.*|README\.md"
```

### キャッシュ設定

```bash
# HTML: キャッシュ無効（常に最新取得）
gcloud storage objects update gs://mochizuki-gc-lp/index.html \
  --cache-control="no-cache, no-store, must-revalidate"

# 静的アセット: 長期キャッシュ
gcloud storage objects update "gs://mochizuki-gc-lp/css/**" \
  --cache-control="public, max-age=31536000, immutable"
gcloud storage objects update "gs://mochizuki-gc-lp/js/**" \
  --cache-control="public, max-age=31536000, immutable"
gcloud storage objects update "gs://mochizuki-gc-lp/images/**" \
  --cache-control="public, max-age=31536000, immutable"
```

---

## Cloud Functions デプロイ（SendGrid フォームバックエンド）

```bash
# 1. functions/ ディレクトリで実行
cd functions/

# 2. 依存インストール
npm install

# 3. デプロイ
gcloud functions deploy sendMail \
  --project servertest-337307 \
  --runtime nodejs20 \
  --trigger-http \
  --allow-unauthenticated \
  --region asia-northeast1 \
  --set-env-vars SENDGRID_API_KEY=YOUR_API_KEY_HERE \
  --entry-point sendMail

# 4. デプロイ後: js/form.js の CF_URL を実際のURLに更新すること
# 例: https://asia-northeast1-servertest-337307.cloudfunctions.net/sendMail
```

---

## コンテンツ差し替えチェックリスト

### 画像（仮画像 → 本番画像）

| ファイルパス | 内容 | ステータス |
|------------|------|---------|
| `images/hero/hero-main.webp` | FV背景（1920×1080px以上） | ⬜ 差し替え待ち |
| `images/course/course-01.webp` | コース写真① | ⬜ 差し替え待ち |
| `images/course/course-02.webp` | コース写真② | ⬜ 差し替え待ち |
| `images/course/course-03.webp` | コース写真③ | ⬜ 差し替え待ち |
| `images/benefits/benefit-01.webp` | 特典①画像 | ⬜ 差し替え待ち |
| `images/benefits/benefit-02.webp` | 特典②画像 | ⬜ 差し替え待ち |
| `images/benefits/benefit-03.webp` | 特典③画像 | ⬜ 差し替え待ち |
| `images/benefits/benefit-04.webp` | 特典④画像 | ⬜ 差し替え待ち |
| `images/common/logo.png` | ロゴファイル | ⬜ 支給待ち |
| `images/common/ogp.jpg` | OGP画像（1200×630px） | ⬜ 差し替え待ち |

### テキスト・設定

| 項目 | 場所 | ステータス |
|------|------|---------|
| 視察プレー土日祝料金 | `index.html` #trial | ⬜ 後日連絡待ち |
| 新ドメイン | GCSバケット名・canonical・OGP | ⬜ 未定 |
| GA4プロパティID | `index.html` `<head>` | ⬜ デプロイ前に設定 |
| SendGrid APIキー | Cloud Functions 環境変数 | ⬜ 要設定 |
| フォーム送信先メール | `functions/index.js` | ⬜ `mochizuki@resol-golf.jp` で仮設定 |
| コース開場年数 | `index.html` #numbers | ⬜ 確認待ち |
| GoogleマップURL | `index.html` #access | ⬜ 正確な座標に差し替え |

> **仮画像の目印：** `data-placeholder="true"` 属性が付いている画像はすべて差し替え対象

---

## 画像最適化コマンド

```bash
# WebP変換（npx sharp-cli 使用）
npx sharp-cli --input images/src/*.jpg \
  --output images/hero/ \
  --format webp --quality 82

# または squoosh-cli
npx @squoosh/cli --webp '{"quality":82}' images/src/*.jpg -d images/output/
```

---

## ブラウザ確認チェックリスト

- [ ] Chrome最新版（PC / Android）
- [ ] Safari最新版（macOS / iOS）
- [ ] Firefox最新版
- [ ] Edge最新版
- [ ] 375px（iPhone SE）表示確認
- [ ] 768px（iPad）表示確認
- [ ] 1280px（PC）表示確認
- [ ] フォーム送信テスト（GAS管理シート受信確認）
- [ ] Lighthouse: Performance 90+ / SEO 95+ / Accessibility 90+
- [ ] GA4リアルタイムレポートで計測確認
