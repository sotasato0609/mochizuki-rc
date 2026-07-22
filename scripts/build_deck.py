#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""望月リソルゴルフクラブ 第2期会員募集｜運用分析レポート＆2026年8月配信提案"""

from pptx import Presentation
from pptx.util import Inches as In, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
import copy

OUT = "望月リソルGC_運用分析レポート＆2026年8月配信提案.pptx"

# ── デザイントークン ─────────────────────────────
FONT = "Yu Gothic"
FONT_EN = "Arial"
GREEN = RGBColor(0x1F, 0x4E, 0x3D)
GREEN_MID = RGBColor(0x3D, 0x6B, 0x58)
GREEN_PALE = RGBColor(0xE7, 0xEE, 0xEA)
GOLD = RGBColor(0xA8, 0x89, 0x5C)
INK = RGBColor(0x2B, 0x2B, 0x2B)
MUTED = RGBColor(0x74, 0x74, 0x74)
LINE = RGBColor(0xD9, 0xD9, 0xD9)
SOFT = RGBColor(0xF5, 0xF6, 0xF4)
ALERT = RGBColor(0xA6, 0x3A, 0x3A)
ALERT_PALE = RGBColor(0xF6, 0xEC, 0xEC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SW, SH = 13.333, 7.5
ML, MR = 0.72, 0.72
CW = SW - ML - MR
BODY_TOP = 1.62
BODY_BOT = 6.92

prs = Presentation()
prs.slide_width, prs.slide_height = In(SW), In(SH)
BLANK = prs.slide_layouts[6]
_page = {"n": 0}


# ── 基本ヘルパ ───────────────────────────────
def tf_style(tf, size=12, color=INK, bold=False, align=PP_ALIGN.LEFT,
             space_after=3, line=1.25, font=FONT):
    tf.word_wrap = True
    for p in tf.paragraphs:
        p.alignment = align
        p.space_after = Pt(space_after)
        p.line_spacing = line
        for r in p.runs:
            r.font.size, r.font.bold, r.font.name = Pt(size), bold, font
            r.font.color.rgb = color


def text(slide, x, y, w, h, s, size=12, color=INK, bold=False,
         align=PP_ALIGN.LEFT, line=1.25, space_after=3, anchor=MSO_ANCHOR.TOP, font=FONT):
    tb = slide.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = s.split("\n")
    tf.text = lines[0]
    for ln in lines[1:]:
        tf.add_paragraph().text = ln
    tf_style(tf, size, color, bold, align, space_after, line, font)
    return tb


def rect(slide, x, y, w, h, fill=None, lc=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, In(x), In(y), In(w), In(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if lc is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = lc
        sp.line.width = Pt(lw)
    sp.shadow.inherit = False
    sp.text_frame.text = ""
    return sp


def slide_new(title, label=None, lead=None):
    s = prs.slides.add_slide(BLANK)
    _page["n"] += 1
    rect(s, 0, 0, SW, 0.075, GREEN)
    y = 0.46
    if label:
        text(s, ML, y, CW, 0.24, label, 10.5, GOLD, True)
        y += 0.3
    text(s, ML, y, CW, 0.52, title, 25, GREEN, True, line=1.1)
    ty = y + (0.62 if len(title) < 34 else 0.98)
    rect(s, ML, ty, 0.9, 0.035, GOLD)
    if lead:
        text(s, ML, ty + 0.18, CW, 0.4, lead, 12.5, MUTED, line=1.35)
    rect(s, ML, 7.06, CW, 0.012, LINE)
    text(s, ML, 7.13, 8, 0.22, "望月リソルゴルフクラブ｜運用分析レポート＆2026年8月配信提案", 8.5, MUTED)
    text(s, SW - MR - 1.2, 7.13, 1.2, 0.22, f"{_page['n']:02d}", 8.5, MUTED, align=PP_ALIGN.RIGHT, font=FONT_EN)
    return s


def table(slide, x, y, w, rows, col_w, head_fill=GREEN, head_color=WHITE,
          fs=11, hfs=10.5, row_h=0.34, head_h=0.36, aligns=None, zebra=True,
          hl_rows=None, hl_fill=GREEN_PALE, bold_rows=None):
    """rows[0] = ヘッダ"""
    hl_rows = hl_rows or []
    bold_rows = bold_rows or []
    nrow, ncol = len(rows), len(rows[0])
    tot = sum(col_w)
    col_w = [c / tot * w for c in col_w]
    aligns = aligns or [PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * (ncol - 1)
    cy = y
    for ri, row in enumerate(rows):
        h = head_h if ri == 0 else row_h
        if ri == 0:
            rect(slide, x, cy, w, h, head_fill)
        elif ri in hl_rows:
            rect(slide, x, cy, w, h, hl_fill)
        elif zebra and ri % 2 == 0:
            rect(slide, x, cy, w, h, SOFT)
        cx = x
        for ci, cell in enumerate(row):
            pad = 0.09
            bold = (ri == 0) or (ri in bold_rows) or str(cell).startswith("**")
            val = str(cell).replace("**", "")
            col = head_color if ri == 0 else INK
            al = aligns[ci] if ci < len(aligns) else PP_ALIGN.LEFT
            text(slide, cx + pad, cy, col_w[ci] - pad * 2, h, val,
                 hfs if ri == 0 else fs, col, bold, al,
                 anchor=MSO_ANCHOR.MIDDLE, line=1.0, space_after=0)
            cx += col_w[ci]
        if ri > 0:
            rect(slide, x, cy + h, w, 0.008, LINE)
        cy += h
    return cy


def stat(slide, x, y, w, h, value, label, note=None,
         vcolor=GREEN, fill=SOFT, vsize=30, border=None):
    rect(slide, x, y, w, h, fill, border, 1.0)
    text(slide, x + 0.16, y + 0.16, w - 0.32, 0.26, label, 10.5, MUTED, True)
    text(slide, x + 0.16, y + 0.46, w - 0.32, 0.62, value, vsize, vcolor, True, line=1.0, font=FONT_EN)
    if note:
        text(slide, x + 0.16, y + h - 0.52, w - 0.32, 0.44, note, 9.5, MUTED, line=1.2)


def callout(slide, x, y, w, h, body, kind="info"):
    fill, bar, col = (GREEN_PALE, GREEN, INK) if kind == "info" else (ALERT_PALE, ALERT, INK)
    rect(slide, x, y, w, h, fill)
    rect(slide, x, y, 0.055, h, bar)
    text(slide, x + 0.24, y + 0.13, w - 0.42, h - 0.26, body, 11.5, col, line=1.35, anchor=MSO_ANCHOR.MIDDLE)


def note(slide, y, s):
    text(slide, ML, y, CW, 0.4, s, 9.5, MUTED, line=1.3)


def chart_style(gf, cat_size=10, val_size=9.5, legend=False, gridlines=False):
    ch = gf.chart
    ch.font.size = Pt(cat_size)
    ch.font.name = FONT
    ch.font.color.rgb = INK
    if legend:
        ch.has_legend = True
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(10)
    else:
        ch.has_legend = False
    try:
        va = ch.value_axis
        va.has_major_gridlines = gridlines
        if gridlines:
            va.major_gridlines.format.line.color.rgb = LINE
            va.major_gridlines.format.line.width = Pt(0.5)
        va.tick_labels.font.size = Pt(val_size)
        va.format.line.fill.background()
    except Exception:
        pass
    try:
        ca = ch.category_axis
        ca.tick_labels.font.size = Pt(cat_size)
        ca.format.line.color.rgb = LINE
    except Exception:
        pass
    return ch


# ══════════════════════════════════════════════
# 01 表紙
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, GREEN)
rect(s, 0, 0, SW, 0.16, GOLD)
text(s, 1.15, 2.05, 11, 0.34, "MOCHIZUKI RESOL GOLF CLUB", 12.5, GOLD, True, font=FONT_EN)
text(s, 1.15, 2.5, 11.2, 1.5,
     "第2期会員募集\nWEB広告 運用分析レポート", 40, WHITE, True, line=1.16)
rect(s, 1.15, 4.32, 1.5, 0.045, GOLD)
text(s, 1.15, 4.62, 11, 0.42, "および 2026年8月 配信提案", 19, WHITE, False)
text(s, 1.15, 6.25, 6, 0.28, "2026年7月22日", 12, GOLD, font=FONT_EN)
text(s, 1.15, 6.58, 8, 0.28, "ゲンダイエージェンシー株式会社", 12.5, WHITE)

# ══════════════════════════════════════════════
# 02 本レポートについて
# ══════════════════════════════════════════════
s = slide_new("本レポートについて", "INTRODUCTION",
              "成果が伸びていない要因を特定するため、第1期にさかのぼって全データを検証しました。")
rows = [
    ["調査対象", "期間", "内容"],
    ["お問い合わせ実データ", "2025年8月〜2026年7月", "通知メールを1件ずつ精査。スパム・テスト送信を除外し、居住地・種別・意向を分類"],
    ["Google Analytics 4", "2024年10月〜2026年7月", "セッション・地域・デバイス・流入元・サイト内行動・遷移先"],
    ["Google広告", "2025年6月〜2026年7月", "キャンペーン別実績、検索テーマ、エリア設定、アセットグループ"],
    ["Meta広告", "2024年10月〜2026年7月", "キャンペーン・広告セット別実績、月別のエリア設定の変遷、オーディエンス別成績"],
    ["DV360", "2024年11月〜2026年7月", "全キャンペーン実績、配信面別データ 9,833行"],
    ["LINEヤフー広告", "2024年10月〜2025年6月", "配信実績（表示・クリック・クリック率）"],
    ["ご請求データ", "2024年9月〜2026年7月", "媒体別・月別の費用構成"],
    ["ランディングページ", "2026年7月22日", "実機での動作検証、入力導線の確認"],
]
table(s, ML, BODY_TOP + 0.12, CW, rows, [2.5, 2.4, 7.2],
      aligns=[PP_ALIGN.LEFT] * 3, fs=10.5, row_h=0.365)
callout(s, ML, 6.18, CW, 0.66,
        "推測で数字を埋めていません。確認できなかった項目は「未確認」と明記しています。"
        "件数が少ない項目は、断定せず「方向性」として扱っています。")

# ══════════════════════════════════════════════
# 03 サマリー
# ══════════════════════════════════════════════
s = slide_new("分析で分かったこと", "SUMMARY",
              "ご予算を30%増やし集客を1.8倍にしたにもかかわらず、お問い合わせは1/3以下に減少しました。")
findings = [
    ("01", "成果の53%は、ゴルフ場から\n概ね70km圏内の方でした", "第3章"),
    ("02", "配信エリアと成果は、\n月単位できれいに対応していました", "第4章"),
    ("03", "成果が出ていた時期は、\n3媒体がバランスしていました", "第5章"),
    ("04", "媒体によって「クリックがサイトに\n届く割合」が2.7倍違います", "第6章"),
    ("05", "検索広告のクリックの70%が、\nすでに貴クラブをご存知の方でした", "第7章"),
    ("06", "じっくり読まれているのはパソコン。\nしかし流入の96%はスマートフォン", "第8章"),
]
cw, ch_, gx, gy = 3.72, 1.42, 0.29, 0.26
for i, (no, body, ref) in enumerate(findings):
    x = ML + (i % 3) * (cw + gx)
    y = BODY_TOP + 0.34 + (i // 3) * (ch_ + gy)
    rect(s, x, y, cw, ch_, SOFT)
    rect(s, x, y, 0.05, ch_, GREEN)
    text(s, x + 0.22, y + 0.16, 0.6, 0.3, no, 15, GOLD, True, font=FONT_EN)
    text(s, x + 0.22, y + 0.5, cw - 0.44, 0.72, body, 12, INK, True, line=1.3)
    text(s, x + cw - 0.85, y + ch_ - 0.34, 0.66, 0.24, ref, 9, MUTED, align=PP_ALIGN.RIGHT)
callout(s, ML, 6.28, CW, 0.56,
        "原因は「広告の量」ではなく、配信の設計にあります。", kind="info")

# ══════════════════════════════════════════════
# 04 第1期・第2期の比較
# ══════════════════════════════════════════════
s = slide_new("第1期・第2期の比較", "第2章　成果の全体像")
cards = [
    ("+30.0%", "月あたりご請求額", "¥251,250 → ¥326,667", GREEN),
    ("1.8倍", "月あたりサイト集客", "6,427 → 11,715", GREEN),
    ("−89%", "お問い合わせ", "19件 → 2件", ALERT),
    ("4.63倍", "獲得単価", "¥105,789 → ¥490,000", ALERT),
]
cwd = (CW - 0.3 * 3) / 4
for i, (v, l, n, c) in enumerate(cards):
    stat(s, ML + i * (cwd + 0.3), BODY_TOP + 0.18, cwd, 1.72, v, l, n, c,
         SOFT if c == GREEN else ALERT_PALE, vsize=29)
rows = [
    ["", "第1期  2025年8月〜2026年3月（8ヶ月）", "第2期  2026年5月〜7月（3ヶ月）"],
    ["ご請求額 合計", "¥2,010,000", "¥980,000"],
    ["サイトセッション", "51,414", "31,630"],
    ["**お問い合わせ", "**19件", "**2件"],
    ["お問い合わせ率（CVR）", "0.037%", "0.006%"],
    ["**獲得単価", "**¥105,789", "**¥490,000"],
]
table(s, ML, BODY_TOP + 2.22, CW, rows, [4.2, 3.85, 3.85], hl_rows=[3, 5], row_h=0.365)
callout(s, ML, 6.3, CW, 0.54, "集客量は増えています。増えた集客が、お問い合わせに結びついていません。")

# ══════════════════════════════════════════════
# 05 月次推移
# ══════════════════════════════════════════════
s = slide_new("月次推移 ── 最良月は2026年3月", "第2章　成果の全体像",
              "第1期は月を追うごとに改善していました。2026年1月2件 → 2月3件 → 3月5件。")
cd = CategoryChartData()
cd.categories = ["25/8", "25/9", "25/10", "25/11", "25/12", "26/1", "26/2", "26/3", "26/5", "26/6", "26/7"]
cd.add_series("お問い合わせ件数", (1, 3, 3, 0, 2, 2, 3, 5, 1, 1, 0))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, In(ML), In(BODY_TOP + 0.5),
                        In(CW), In(3.15), cd)
ch = chart_style(gf, gridlines=True)
pl = ch.plots[0]
pl.gap_width = 55
pl.has_data_labels = True
dl = pl.data_labels
dl.font.size = Pt(11)
dl.font.bold = True
dl.font.color.rgb = INK
dl.position = XL_LABEL_POSITION.OUTSIDE_END
ser = pl.series[0]
ser.format.fill.solid()
ser.format.fill.fore_color.rgb = GREEN_MID
for idx in (7,):
    pt = ser.points[idx]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = GOLD
rows = [
    ["月", "2025/8", "2025/9", "2025/10", "2025/11", "2025/12", "2026/1", "2026/2", "2026/3", "2026/5", "2026/6", "2026/7"],
    ["ご請求額（千円）", "300", "300", "280", "100", "150", "330", "300", "**250", "300", "380", "300"],
    ["獲得単価（千円）", "300", "100", "93", "—", "75", "165", "100", "**50", "300", "380", "—"],
]
table(s, ML, BODY_TOP + 3.85, CW, rows, [2.15] + [0.9] * 11,
      aligns=[PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * 11, fs=9.5, hfs=9, row_h=0.33, head_h=0.33)
note(s, 6.62, "※ 2026年4月はLP刷新期間のため比較から除外。2026年7月は7月21日時点。オレンジは全期間で最良の月。")

# ══════════════════════════════════════════════
# 06 お問い合わせの質
# ══════════════════════════════════════════════
s = slide_new("件数だけでなく、見込み度も下がっています", "第2章　成果の全体像",
              "フォーム「会員権について」のご回答内訳です。")
stat(s, ML, BODY_TOP + 0.3, 5.7, 2.1, "68%", "第1期（19件）｜具体的に検討している",
     "13件が「具体的に検討している」と回答", GREEN, SOFT, vsize=48)
stat(s, ML + 6.13, BODY_TOP + 0.3, 5.7, 2.1, "0%", "第2期（2件）｜具体的に検討している",
     "「興味がある」1件、来場予定の方からのご連絡1件", ALERT, ALERT_PALE, vsize=48)
rows = [
    ["会員権について", "第1期（19件）", "第2期（2件）"],
    ["**具体的に検討している", "**13件（68%）", "**0件"],
    ["興味がある", "7件", "1件"],
    ["未選択・その他", "—", "1件"],
]
table(s, ML, BODY_TOP + 2.72, CW, rows, [5.6, 3.1, 3.1], hl_rows=[1], row_h=0.37)
callout(s, ML, 6.16, CW, 0.66,
        "第1期は7割が「具体的に検討している」でした。第2期の2件は、いずれも購入検討の段階に至っていません。",
        kind="alert")

# ══════════════════════════════════════════════
# 07 入口は資料請求
# ══════════════════════════════════════════════
s = slide_new("誰が申し込んでいるのか ①　入口は「資料請求」です", "第3章　お問い合わせ19件の分析",
              "第1期のお問い合わせ19件を、1件ずつ内容を確認して分類しました。")
stat(s, ML, BODY_TOP + 0.35, 4.05, 2.35, "95%", "お問い合わせ種別｜資料のご請求",
     "19件中18件", GREEN, SOFT, vsize=58)
rows = [
    ["お問い合わせ種別", "件数", "比率"],
    ["**資料のご請求", "**18件", "**95%"],
    ["視察プレーのお問い合わせ", "3件", "16%"],
    ["その他", "1件", "5%"],
]
table(s, ML + 4.45, BODY_TOP + 0.35, CW - 4.45, rows, [4.6, 1.5, 1.5], hl_rows=[1], row_h=0.42)
note(s, BODY_TOP + 2.32, "※ 複数選択のため合計は100%を超えます")
callout(s, ML, BODY_TOP + 3.0, CW, 1.12,
        "示唆　視察プレーの直接お申し込みは3件のみでした。大半の方は、まず資料を請求し、そこから検討に入られています。\n"
        "8月に視察プレーを訴求する場合も、入口は「資料請求」に置いたほうが実際の行動に沿います。")

# ══════════════════════════════════════════════
# 08 距離帯別
# ══════════════════════════════════════════════
s = slide_new("誰が申し込んでいるのか ②　成果の53%は概ね70km圏内", "第3章　お問い合わせ19件の分析")
cd = CategoryChartData()
cd.categories = ["概ね30km圏\n佐久・小諸・軽井沢・御代田", "概ね40km圏\n上田市",
                 "概ね70km圏\n群馬県高崎市", "概ね90km圏\n長野県松本市",
                 "首都圏\n東京・神奈川・千葉"]
cd.add_series("件数", (7, 2, 1, 1, 8))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, In(ML), In(BODY_TOP + 0.28),
                        In(7.6), In(3.5), cd)
ch = chart_style(gf, cat_size=9.5)
pl = ch.plots[0]
pl.gap_width = 45
pl.has_data_labels = True
pl.data_labels.font.size = Pt(12)
pl.data_labels.font.bold = True
pl.data_labels.font.color.rgb = INK
ser = pl.series[0]
ser.format.fill.solid()
ser.format.fill.fore_color.rgb = GREEN_MID
for idx in (0, 1, 2):
    pt = ser.points[idx]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = GOLD
stat(s, ML + 7.95, BODY_TOP + 0.28, 3.88, 1.62, "53%", "概ね70km圏内の累計",
     "19件中10件。佐久市内が2件、隣接町村が5件", GOLD, SOFT, vsize=48)
rows = [
    ["距離帯", "件数", "累計"],
    ["**概ね30km圏", "**7件", "**37%"],
    ["概ね40km圏", "2件", "47%"],
    ["**概ね70km圏", "**1件", "**53%"],
    ["概ね90km圏", "1件", "58%"],
    ["首都圏", "8件", "100%"],
]
table(s, ML + 7.95, BODY_TOP + 2.06, 3.88, rows, [2.1, 0.9, 0.9], fs=10, row_h=0.29, head_h=0.3)
callout(s, ML, 6.22, CW, 0.6,
        "ゴルフ場のすぐ近くから、着実にお問い合わせが来ています。")

# ══════════════════════════════════════════════
# 09 地元と首都圏
# ══════════════════════════════════════════════
s = slide_new("誰が申し込んでいるのか ③　地元は件数、首都圏は検討度", "第3章　お問い合わせ19件の分析",
              "地元と首都圏では、役割が違います。一律に扱うべきではありません。")
bw = (CW - 0.42) / 2
for i, (ttl, cnt, rate, desc, col, fill) in enumerate([
    ("地元（長野・群馬）", "11件", "64%", "件数が多い。ゴルフ場のすぐ近くから\n着実にお問い合わせが来ています", GREEN, SOFT),
    ("首都圏（東京・神奈川・千葉）", "8件", "75%", "件数は少ないが、検討度が高い。\n「遠い」ことを自覚したうえでご検討", GOLD, SOFT),
]):
    x = ML + i * (bw + 0.42)
    rect(s, x, BODY_TOP + 0.28, bw, 2.72, fill)
    rect(s, x, BODY_TOP + 0.28, bw, 0.055, col)
    text(s, x + 0.28, BODY_TOP + 0.5, bw - 0.56, 0.3, ttl, 14, INK, True)
    text(s, x + 0.28, BODY_TOP + 0.92, 2.4, 0.62, cnt, 34, INK, True, font=FONT_EN, line=1.0)
    text(s, x + 0.28, BODY_TOP + 1.58, bw - 0.56, 0.24, "うち「具体的に検討している」", 10, MUTED)
    text(s, x + 0.28, BODY_TOP + 1.84, 2.6, 0.56, rate, 30, col, True, font=FONT_EN, line=1.0)
    text(s, x + 0.28, BODY_TOP + 2.42, bw - 0.56, 0.5, desc, 10.5, MUTED, line=1.3)
callout(s, ML, BODY_TOP + 3.24, CW, 1.12,
        "唯一の遠方からの資料請求（神奈川県茅ヶ崎市）は、お問い合わせ本文で「自宅から遠方のため、まずは資料をもとに検討を始めたい」と\n"
        "述べられていました。地元は件数、首都圏は検討度。別枠に分けて成果を測るべきです。")
note(s, 6.62, "※ 件数が19件と少ないため、これは断定ではなく方向性としてご理解ください。")

# ══════════════════════════════════════════════
# 10 成果と集客のミスマッチ
# ══════════════════════════════════════════════
s = slide_new("成果を生む地域に、集客が向いていません", "第4章　配信エリアの分析")
cd = CategoryChartData()
cd.categories = ["長野県", "群馬県", "東京都", "神奈川県"]
cd.add_series("第1期の成果構成比", (53, 5, 32, 5))
cd.add_series("2026年7月の集客構成比", (16.7, 2.6, 35.7, 13.6))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, In(ML), In(BODY_TOP + 0.24),
                        In(7.5), In(3.9), cd)
ch = chart_style(gf, legend=True, gridlines=True)
pl = ch.plots[0]
pl.gap_width = 70
pl.has_data_labels = True
pl.data_labels.font.size = Pt(10)
pl.data_labels.font.color.rgb = INK
pl.series[0].format.fill.solid()
pl.series[0].format.fill.fore_color.rgb = GREEN
pl.series[1].format.fill.solid()
pl.series[1].format.fill.fore_color.rgb = RGBColor(0xC8, 0xCF, 0xCB)
rows = [
    ["地域", "成果", "集客", "差"],
    ["**長野県", "**53%", "**16.7%", "**−36pt"],
    ["群馬県", "5%", "2.6%", "−2pt"],
    ["東京都", "32%", "35.7%", "+4pt"],
    ["神奈川県", "5%", "13.6%", "+9pt"],
]
table(s, ML + 7.85, BODY_TOP + 0.24, 3.98, rows, [1.5, 0.85, 0.9, 0.95],
      hl_rows=[1], fs=10.5, row_h=0.36)
callout(s, ML + 7.85, BODY_TOP + 2.24, 3.98, 1.9,
        "成果の半分以上を生む長野県に、\n集客の2割弱しか向けていません。\n\n"
        "長野県からの流入は平均滞在5.8秒と、\n東京（3.2秒）の1.8倍。集客量は最も\n少ないのに、最も読まれています。", kind="alert")

# ══════════════════════════════════════════════
# 11 地域別の流入品質
# ══════════════════════════════════════════════
s = slide_new("長野からの流入は、最も質が高い", "第4章　配信エリアの分析",
              "第2期（2026年5月〜7月）の地域別。集客量が最も少ない長野が、最も読まれています。")
rows = [
    ["地域", "セッション", "構成比", "エンゲージ率", "平均滞在"],
    ["東京都", "10,262", "35.7%", "21.1%", "3.2秒"],
    ["**長野県", "**4,802", "**16.7%", "**25.2%", "**5.8秒"],
    ["神奈川県", "3,895", "13.6%", "22.9%", "2.8秒"],
    ["埼玉県", "1,918", "6.7%", "22.7%", "2.5秒"],
    ["大阪府", "1,360", "4.7%", "24.0%", "2.5秒"],
]
table(s, ML, BODY_TOP + 0.3, CW, rows, [3.4, 2.2, 2.0, 2.2, 2.0], hl_rows=[2], row_h=0.44)
callout(s, ML, BODY_TOP + 3.12, CW, 1.2,
        "長野県は、集客構成比では4番目の東京の半分以下。しかし平均滞在は東京の1.8倍、エンゲージ率も最も高い水準です。\n"
        "「量は最も少なく、質は最も高い」地域に、予算が向いていません。")

# ══════════════════════════════════════════════
# 12 エリア設定と成果の月次対応
# ══════════════════════════════════════════════
s = slide_new("配信エリアの設定と成果は、月単位で対応していました", "第4章　配信エリアの分析",
              "Meta広告のエリア設定を月別に調べたところ、成果と明確に対応していました。")
rows = [
    ["月", "配信エリア", "お問い合わせ"],
    ["2025年9月", "東京23区", "3件"],
    ["2025年10月", "ゴルフ場から半径40km", "3件"],
    ["2025年11月", "Meta配信なし", "0件"],
    ["2025年12月", "東京23区", "2件"],
    ["2026年1月", "半径24km", "2件"],
    ["2026年2月", "半径48〜49km", "3件"],
    ["**2026年3月", "**半径48〜49km", "**5件（最良）"],
    ["2026年6月", "半径50km", "1件"],
    ["**2026年7月", "**東京・神奈川・長野の3都県に拡大", "**0件"],
]
table(s, ML, BODY_TOP + 0.28, 7.5, rows, [2.0, 4.0, 1.8],
      aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
      hl_rows=[7], row_h=0.345)
stat(s, ML + 7.85, BODY_TOP + 0.28, 3.98, 1.5, "12件", "半径24〜50km圏で運用していた月の合計",
     None, GREEN, SOFT, vsize=40)
stat(s, ML + 7.85, BODY_TOP + 1.94, 3.98, 1.5, "0件", "3都県に広げた2026年7月",
     None, ALERT, ALERT_PALE, vsize=40)
callout(s, ML + 7.85, BODY_TOP + 3.6, 3.98, 1.28,
        "留保　7月1日にはエリア拡大に加え、\nGoogle広告のP-MAX移行・DV360の停止も\n同時に起きています。エリア単独の因果は\n統計的には証明できません。")

# ══════════════════════════════════════════════
# 13 媒体構成の変遷
# ══════════════════════════════════════════════
s = slide_new("成果が出ていた時期は、3媒体がバランスしていました", "第5章　媒体構成の分析")
cd = CategoryChartData()
cd.categories = ["2025年9月\n3件", "2025年10月\n3件", "2026年2月\n3件", "2026年3月\n5件",
                 "2026年5月\n1件", "2026年6月\n1件", "2026年7月\n0件"]
cd.add_series("Google広告", (33, 40, 50, 40, 17, 14, 17))
cd.add_series("Meta広告", (33, 40, 33, 20, 33, 14, 83))
cd.add_series("DV360", (33, 20, 17, 40, 50, 71, 0))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, In(ML), In(BODY_TOP + 0.24),
                        In(7.8), In(3.75), cd)
ch = chart_style(gf, cat_size=9.5, legend=True)
pl = ch.plots[0]
pl.gap_width = 55
pl.has_data_labels = True
pl.data_labels.font.size = Pt(9)
pl.data_labels.font.color.rgb = WHITE
for i, c in enumerate([GREEN, GOLD, RGBColor(0x8F, 0xA5, 0x9A)]):
    pl.series[i].format.fill.solid()
    pl.series[i].format.fill.fore_color.rgb = c
rows = [
    ["", "Google", "Meta", "DV360", "件数/月"],
    ["**第1期 月平均", "**38%", "33%", "28%", "**2.4件"],
    ["**第2期 月平均", "**16%", "42%", "42%", "**0.67件"],
]
table(s, ML + 8.15, BODY_TOP + 0.24, 3.68, rows, [1.5, 0.75, 0.7, 0.8, 0.9],
      fs=9.5, hfs=9, row_h=0.42, head_h=0.34)
callout(s, ML + 8.15, BODY_TOP + 1.5, 3.68, 2.5,
        "Google広告が月¥75,000から\n¥40,000へ約半減しました。\n\n"
        "そして2026年7月はMeta広告に\n83%が集中し、0件でした。\n\n"
        "最良月（2026年3月）でさえ\nMeta広告は¥40,000です。", kind="alert")
note(s, 6.5, "※ 構成比は配信費ベース。金額の多寡ではなく、媒体の組み合わせが成果に効いていました。")

# ══════════════════════════════════════════════
# 14 サイト到達率
# ══════════════════════════════════════════════
s = slide_new("新しい評価軸 ── 買ったクリックは、サイトに届いているか", "第6章　配信品質の分析")
rect(s, ML, BODY_TOP + 0.18, CW, 0.72, GREEN_PALE)
text(s, ML + 0.3, BODY_TOP + 0.3, CW - 0.6, 0.5,
     "サイト到達率　＝　GA4のセッション数　÷　広告のクリック数",
     15, GREEN, True, PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
text(s, ML, BODY_TOP + 1.06, CW, 0.4,
     "広告レポートの「クリック数」は、そのままサイト訪問数にはなりません。誤タップや、読み込み前の離脱があるためです。",
     11.5, MUTED)
stat(s, ML, BODY_TOP + 1.6, 5.7, 2.0, "43.0%", "LINEヤフー広告（2024年10月〜2025年5月）",
     "クリック率 0.12%　／　健全な水準", GREEN, SOFT, vsize=52)
stat(s, ML + 6.13, BODY_TOP + 1.6, 5.7, 2.0, "15.9%", "DV360（2026年5〜6月）",
     "クリック率 11.30%　／　誤タップ主体", ALERT, ALERT_PALE, vsize=52)
callout(s, ML, BODY_TOP + 3.82, CW, 1.02,
        "媒体によって2.7倍の差があります。ディスプレイ広告のクリック率は通常0.1〜0.5%程度です。\n"
        "DV360の11.30%は、広告を見て興味を持ってクリックされた数値ではありません。", kind="alert")

# ══════════════════════════════════════════════
# 15 DV360 配信面分析
# ══════════════════════════════════════════════
s = slide_new("DV360の配信面を1面ずつ分析しました", "第6章　配信品質の分析",
              "2026年5〜6月の全配信面 9,833行を取得し、GA4と突き合わせました。")
rows = [
    ["配信面", "表示", "クリック", "クリック率", "サイト到達率", "平均滞在"],
    ["trilltrill.jp", "88,947", "7,574", "8.5%", "**18.5%", "**0.0秒"],
    ["SmartNews（iOSアプリ）", "23,728", "4,261", "**18.0%", "77.6%", "**0.9秒"],
    ["nlab.itmedia.co.jp", "25,312", "1,564", "6.2%", "12.6%", "0.8秒"],
    ["mamastar.jp", "23,619", "1,206", "5.1%", "**4.1%", "0.3秒"],
    ["ameblo.jp", "18,075", "926", "5.1%", "6.5%", "0.3秒"],
    ["**全体", "**672,105", "**43,723", "**6.51%", "**15.9%", "—"],
]
table(s, ML, BODY_TOP + 0.28, CW, rows, [3.1, 1.75, 1.6, 1.6, 1.9, 1.5],
      hl_rows=[6], row_h=0.355)
bw = (CW - 0.36) / 2
callout(s, ML, BODY_TOP + 3.06, bw, 1.0,
        "trilltrill.jp　クリックの17%を1面で占めるが、\n8割がサイトに到達していない", kind="alert")
callout(s, ML + bw + 0.36, BODY_TOP + 3.06, bw, 1.0,
        "SmartNews　到達はするが平均0.9秒で離脱。\n誤タップ後に戻られている", kind="alert")
text(s, ML, BODY_TOP + 4.22, CW, 0.7,
     "クリック率5%超の配信面が65面あり、これがクリックの61%・配信費の47%を占めています。\n"
     "一方でMILE mobile（Androidアプリ）は平均滞在28.7秒と良質。面ごとの選別が有効です。",
     11.5, INK, line=1.35)

# ══════════════════════════════════════════════
# 16 LINEヤフー実績
# ══════════════════════════════════════════════
s = slide_new("LINEヤフー広告は、最も質の高い到達を実現していました", "第6章　配信品質の分析")
rows = [
    ["配信月", "表示回数", "クリック", "クリック率"],
    ["2024年10月", "1,657,045", "2,944", "0.18%"],
    ["2024年11月", "1,397,408", "2,544", "0.18%"],
    ["2025年5月", "3,738,868", "2,772", "0.07%"],
    ["**合計", "**6,793,326", "**8,260", "**0.12%"],
]
table(s, ML, BODY_TOP + 0.3, 7.3, rows, [2.1, 2.0, 1.6, 1.6], hl_rows=[4], row_h=0.42)
stat(s, ML + 7.65, BODY_TOP + 0.3, 4.18, 1.5, "43.0%", "サイト到達率",
     "DV360（15.9%）の2.7倍", GREEN, SOFT, vsize=42)
stat(s, ML + 7.65, BODY_TOP + 1.96, 4.18, 1.32, "680万回", "累計表示回数",
     None, GREEN, SOFT, vsize=32)
callout(s, ML, BODY_TOP + 2.62, 7.3, 1.44,
        "680万回の表示に対しクリック率0.12%、サイト到達率43.0%。\n"
        "ディスプレイ広告として教科書通りの健全な数値です。\n"
        "貴クラブ専用アカウントが稼働可能な状態で残っており、開設手続きなしで再開できます。")
note(s, 6.42, "※ この期間のコンバージョンは0件でしたが、当時コンバージョン計測が設定されていたかは確認できていません。再開時は計測を設定したうえで配信します。")

# ══════════════════════════════════════════════
# 17 検索の分析
# ══════════════════════════════════════════════
s = slide_new("検索広告のクリックの70%が、すでに貴クラブをご存知の方でした", "第7章　検索の分析")
rows = [
    ["検索テーマ（2026年7月）", "クリック"],
    ["望月 リソル ゴルフ クラブ", "35"],
    ["リソル 望月", "11"],
    ["望月 東急（旧名称）", "9"],
    ["その他", "24"],
]
table(s, ML, BODY_TOP + 0.3, 5.6, rows, [4.0, 1.6], hl_rows=[1, 2, 3], row_h=0.4)
stat(s, ML + 5.95, BODY_TOP + 0.3, 2.8, 2.42, "70%", "クラブ名での検索",
     "検索クリックに占める比率", ALERT, ALERT_PALE, vsize=44)
stat(s, ML + 9.05, BODY_TOP + 0.3, 2.78, 2.42, "42", "「ゴルフ 会員権」\nへのクリック（第1期）",
     "本命の検索には\nほとんど出せていません", MUTED, SOFT, vsize=44)
text(s, ML, BODY_TOP + 3.0, CW, 0.32, "競合ゴルフ場名への出稿は、成果が出ていません", 14, INK, True)
text(s, ML, BODY_TOP + 3.42, CW, 0.5,
     "小諸高原ゴルフクラブ／富士見高原ゴルフコース／千曲高原カントリークラブ／サニーカントリークラブ／"
     "日向山高原ゴルフコース／浅間高原カントリー倶楽部／蓼科高原カントリークラブ／佐久リゾートゴルフ倶楽部 ほか",
     10.5, MUTED, line=1.3)
callout(s, ML, BODY_TOP + 4.12, CW, 0.92,
        "これらからのお問い合わせは0件でした。クラブ名での検索は、広告を出さなくても自然検索で到達できます。\n"
        "その分を、会員権をお探しの方への配信に振り向ける余地があります。")

# ══════════════════════════════════════════════
# 18 サイト内行動
# ══════════════════════════════════════════════
s = slide_new("サイト内行動の分析", "第8章")
text(s, ML, BODY_TOP + 0.1, CW, 0.3, "① じっくり読まれているのはパソコン。しかし流入の96%はスマートフォンです", 13.5, INK, True)
rows = [
    ["デバイス", "セッション", "構成比", "エンゲージ率", "平均滞在"],
    ["スマートフォン", "30,377", "**95.9%", "22.4%", "**2.5秒"],
    ["**パソコン", "**964", "**3.0%", "**47.5%", "**28.5秒"],
    ["タブレット", "326", "1.0%", "18.7%", "5.5秒"],
]
table(s, ML, BODY_TOP + 0.5, 7.4, rows, [2.0, 1.5, 1.2, 1.5, 1.3], hl_rows=[2], fs=10.5, row_h=0.33, head_h=0.33)
callout(s, ML + 7.75, BODY_TOP + 0.5, 4.08, 1.32,
        "パソコンは流入の3%ですが、\n平均滞在はスマートフォンの11.4倍。\n"
        "「スマートフォンの流入品質が低い」\nということです。")
text(s, ML, BODY_TOP + 2.00, CW, 0.3, "② 会員募集の導線が二重になっています", 13.5, INK, True)
rows2 = [
    ["期間", "LPから公式サイトへの遷移", "お問い合わせ"],
    ["第1期（8ヶ月）", "767件", "19件"],
    ["第2期（3ヶ月）", "84件", "2件"],
    ["**全期間累計", "**1,430件", "—"],
]
table(s, ML, BODY_TOP + 2.40, 5.7, rows2, [2.2, 2.4, 1.5], hl_rows=[3], fs=10.5, row_h=0.33, head_h=0.33)
text(s, ML + 6.05, BODY_TOP + 2.40, 5.78, 1.4,
     "LPと公式サイトで同じ会員募集を掲載しており、リンクは一方通行です。\n"
     "2026年7月の遷移の75%が広告経由でした。\n"
     "ただし公式サイトにもお問い合わせフォームがあり、そちらで成果が発生している可能性があります。",
     10.5, MUTED, line=1.35)
text(s, ML, BODY_TOP + 3.90, CW, 0.3, "③ 検討中の方への再接触が不足しています", 13.5, INK, True)
rows3 = [
    ["Meta広告（直近30日）", "予算構成比", "クリック率", "LP到達率", "接触回数"],
    ["興味関心（新規開拓）", "**91.0%", "1.84%", "82.3%", "1.87回"],
    ["**リターゲティング（検討層）", "**9.0%", "**2.89%", "**85.7%", "2.12回"],
]
table(s, ML, BODY_TOP + 4.30, CW, rows3, [3.6, 2.1, 2.0, 2.0, 2.1], hl_rows=[2], fs=10.5, row_h=0.33, head_h=0.33)

# ══════════════════════════════════════════════
# 19 分析のまとめ → 3つの課題と打ち手
# ══════════════════════════════════════════════
s = slide_new("分析のまとめ ── 3つの課題と打ち手", "第9章・第10章",
              "いずれも「広告を増やす／減らす」ではなく、「向き先を変える」ことで対応できます。")
items = [
    ("課題 01", "配信エリアが広すぎる",
     "成果の53%が概ね70km圏／長野の集客は16.7%／\nエリア設定と成果が月次で対応",
     "配信エリアを半径50〜80km圏へ戻す",
     "東京は停止せず別枠に分離し、\nエリア別に成果を測れる状態に"),
    ("課題 02", "検討中の方への再接触が足りていない",
     "リターゲティングのクリック率は1.57倍なのに\n予算9%・接触2.12回／高額・長期検討の商材",
     "リターゲティングを強化する",
     "比率を9%→20〜25%、接触回数4〜5回へ／\nカスタムオーディエンスを拡張"),
    ("課題 03", "配信面と媒体構成に偏りがある",
     "DV360の到達率15.9%・65面が配信費の47%／\nGoogle広告が半減し7月はMeta83%",
     "配信面を整理し、媒体構成を戻す",
     "DV360は65面を除外して再開／Google広告を\n第1期水準へ／LINEヤフーを再開"),
]
y = BODY_TOP + 0.42
for no, ttl, ev, act, det in items:
    rect(s, ML, y, 5.55, 1.44, ALERT_PALE)
    rect(s, ML, y, 0.05, 1.44, ALERT)
    text(s, ML + 0.22, y + 0.13, 1.1, 0.22, no, 10, ALERT, True, font=FONT_EN)
    text(s, ML + 0.22, y + 0.4, 5.1, 0.28, ttl, 13, INK, True)
    text(s, ML + 0.22, y + 0.76, 5.1, 0.58, ev, 9.5, MUTED, line=1.3)
    ax = ML + 5.55
    text(s, ax + 0.09, y + 0.58, 0.42, 0.3, "▶", 14, GOLD, True, PP_ALIGN.CENTER)
    rect(s, ax + 0.6, y, CW - 5.55 - 0.6, 1.44, GREEN_PALE)
    rect(s, ax + 0.6, y, 0.05, 1.44, GREEN)
    text(s, ax + 0.82, y + 0.28, 5.0, 0.3, act, 13, GREEN, True)
    text(s, ax + 0.82, y + 0.68, 5.0, 0.6, det, 9.5, MUTED, line=1.3)
    y += 1.62

# ══════════════════════════════════════════════
# 20 8月配信プラン
# ══════════════════════════════════════════════
s = slide_new("2026年8月 配信プラン", "第10章　配信提案",
              "視察プレー期間（7月11日〜8月30日）の最終月。期間限定オファーの刈り取り月として設計します。")
rows = [
    ["媒体", "役割・設定", "配信費", "構成比"],
    ["Meta広告", "半径50〜80km（55%）／東京別枠（20%）／リターゲティング（25%）", "¥200,000", "47.6%"],
    ["Google広告（P-MAX）", "半径50〜80km＋東京別枠／クラブ名検索を除外", "¥80,000", "19.0%"],
    ["DV360", "競合店GEO／クリック率5%超の65面を除外", "¥80,000", "19.0%"],
    ["LINEヤフー広告", "長野県東信＋群馬県西部／既存アカウントを再開", "¥60,000", "14.3%"],
    ["配信費 小計", "", "¥420,000", ""],
    ["運用代行費", "", "¥105,000", ""],
    ["**合計", "", "**¥525,000", "**対7月 +75%"],
]
table(s, ML, BODY_TOP + 0.3, CW, rows, [2.6, 5.9, 1.8, 1.55],
      aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
      hl_rows=[7], row_h=0.365)
text(s, ML, BODY_TOP + 3.42, 5.7, 0.3, "媒体の偏りを是正します", 13, INK, True)
rows2 = [
    ["", "Meta", "Google", "DV360", "LINEヤフー"],
    ["2026年7月（実績）", "**83.3%", "16.7%", "0%", "—"],
    ["**2026年8月（提案）", "**47.6%", "19.0%", "19.0%", "14.3%"],
]
table(s, ML, BODY_TOP + 3.82, 5.7, rows2, [1.9, 1.0, 1.0, 0.95, 1.15],
      hl_rows=[2], fs=9.5, hfs=9, row_h=0.34, head_h=0.32)
text(s, ML + 6.05, BODY_TOP + 3.42, 5.78, 0.3, "KPI", 13, INK, True)
rows3 = [
    ["指標", "目標", "根拠"],
    ["**お問い合わせ", "**3〜5件", "第1期の月平均2.4件／最良月5件"],
    ["**獲得単価", "**¥105,000〜175,000", "5件なら第1期平均と同水準"],
    ["地元の集客構成比", "19% → 40%以上", "成果構成比53%に近づける"],
    ["DV360のサイト到達率", "15.9% → 40%以上", "配信面の除外による改善"],
]
table(s, ML + 6.05, BODY_TOP + 3.82, 5.78, rows3, [1.85, 1.65, 2.3],
      aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT],
      hl_rows=[1, 2], fs=9, hfs=9, row_h=0.31, head_h=0.3)

# ══════════════════════════════════════════════
# 21 スケジュール・ご依頼事項
# ══════════════════════════════════════════════
s = slide_new("スケジュールとご依頼事項", "第12章・第13章")
text(s, ML, BODY_TOP + 0.14, 6.4, 0.3, "スケジュール", 14, INK, True)
rows = [
    ["期日", "内容"],
    ["7月下旬", "配信エリアの設定変更／DV360除外リスト作成／クラブ名検索の除外／コンバージョン計測の接続／LPの入力導線最適化"],
    ["7月末", "クリエイティブを視察プレー訴求へ差し替え／LINEヤフー広告の入稿"],
    ["**8月1日", "**配信開始"],
    ["8月中旬", "中間レポート・配分の見直し"],
    ["**8月30日", "**視察プレー受付終了"],
    ["9月上旬", "8月実績のご報告・9月以降のご提案"],
]
table(s, ML, BODY_TOP + 0.54, 6.4, rows, [1.5, 4.9],
      aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT], hl_rows=[3, 5], fs=10, row_h=0.44, head_h=0.34)
text(s, ML + 6.75, BODY_TOP + 0.14, 5.08, 0.3, "ご依頼事項", 14, INK, True)
rect(s, ML + 6.75, BODY_TOP + 0.54, 5.08, 3.42, GREEN_PALE)
rect(s, ML + 6.75, BODY_TOP + 0.54, 0.055, 3.42, GREEN)
text(s, ML + 7.0, BODY_TOP + 0.76, 4.66, 3.0,
     "公式サイト経由のお問い合わせ実績を、\n月別・「知ったきっかけ」別でご共有ください。\n\n"
     "公式サイトのお問い合わせフォームには\n「知ったきっかけ」が必須項目としてあり、\n"
     "「Googleの広告」「Facebook/Instagram等の広告」\nが選択肢に含まれています。\n\n"
     "LPから公式サイトへ1,430件の遷移が発生して\nおり、広告経由のお問い合わせが公式サイト側で\n"
     "受け付けられている可能性があります。\n\n"
     "現時点の集計はLP経由のみです。実際の成果を\n過小評価している可能性があります。",
     10.5, INK, line=1.4)
rect(s, ML, 6.14, CW, 0.68, SOFT)
text(s, ML + 0.28, 6.24, CW - 0.56, 0.5,
     "本レポートのデータ出典：お問い合わせ通知メールの実データ／Google Analytics 4／Google Ads API／Meta Marketing API／"
     "DV360 Bid Manager API／LINEヤフー広告API／弊社基幹システム",
     9.5, MUTED, line=1.3, anchor=MSO_ANCHOR.MIDDLE)

prs.save(OUT)
print(f"保存: {OUT} / 全{len(prs.slides.__iter__.__self__._sldIdLst)}枚")
