#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
望月リソルゴルフクラブ 第2期会員募集｜2026年8月 配信提案

骨子（docs/2026-08-proposal-outline.md）の構成をそのままスライド化する。全10枚。
  01 表紙 ／ 02 サマリー ／ 03 現状 ／ 04-06 分析の要点 ／
  07 課題と打ち手 ／ 08 配信プラン ／ 09 KPIと進行 ／ 10 ご依頼事項

デザインフォーマット: 「営業本部共有_買取シミュレーター_2026-07.pptx」の実測トークンに準拠。
  Meiryo単一／直角矩形のみ／タイトル27pt／ヘッダは縦バー+キッカー+短バー+ヘアライン／
  フッタはページ番号のみ／カードは上辺0.05inのアクセントバー／表はヘッダprimary+交互行。
  詳細は .claude/skills/pptx/SKILL.md「デザインフォーマット（参照資料に準拠）」。

正確性プロトコル（.claude/rules/general.md）: 両論併記・証拠クラス明示・内部整合性。
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
import os

OUT_DIR = "output"
OUT = os.path.join(OUT_DIR, "望月リソルGC_2026年8月_配信提案.pptx")

COLORS = {
    "primary":     RGBColor(0x40, 0x5D, 0x7B),
    "primary_dk":  RGBColor(0x33, 0x4A, 0x62),
    "accent":      RGBColor(0xA9, 0x69, 0x33),
    "gray":        RGBColor(0x6C, 0x75, 0x82),
    "ink":         RGBColor(0x2A, 0x2E, 0x33),
    "text":        RGBColor(0x45, 0x4B, 0x52),
    "muted":       RGBColor(0x8A, 0x92, 0x9C),
    "slate_lt":    RGBColor(0x8F, 0xA3, 0xB8),
    "surface":     RGBColor(0xF2, 0xF4, 0xF7),
    "surface_alt": RGBColor(0xEE, 0xF0, 0xF3),
    "border":      RGBColor(0xE2, 0xE6, 0xEB),
    "hairline":    RGBColor(0xD6, 0xDB, 0xE1),
    "bg":          RGBColor(0xFF, 0xFF, 0xFF),
}
FONT_JA = "Meiryo"
SW, SH = 13.333, 7.5
MX, CW = 0.62, 12.10
BODY_Y, PAGE_Y, G = 1.90, 7.12, 0.20

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
BLANK = prs.slide_layouts[6]
I = Inches
_st = {"page": 0, "layouts": []}


def txt(slide, x, y, w, h, text, size, color=None, bold=False,
        align=PP_ALIGN.LEFT, line=1.4, anchor=MSO_ANCHOR.TOP, space_after=3):
    tb = slide.shapes.add_textbox(I(x), I(y), I(w), I(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, ln in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = ln
        p.alignment = align
        p.line_spacing = line
        p.space_after = Pt(space_after)
        for fnt in [p.font] + [r.font for r in p.runs]:
            fnt.name = FONT_JA
            fnt.size = Pt(size)
            fnt.bold = bold
            fnt.color.rgb = color or COLORS["text"]
    return tb


def rect(slide, x, y, w, h, fill):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, I(x), I(y), I(w), I(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    sp.shadow.inherit = False
    sp.text_frame.text = ""
    return sp


def card(slide, x, y, w, h, accent=None, fill=None):
    rect(slide, x, y, w, h, fill or COLORS["surface"])
    if accent:
        rect(slide, x, y, w, 0.05, accent)


def slide_new(kicker, title, tag="C", lead=None):
    s = prs.slides.add_slide(BLANK)
    _st["page"] += 1
    _st["layouts"].append(tag)
    L = _st["layouts"]
    if len(L) >= 3 and L[-1] == L[-2] == L[-3]:
        raise AssertionError(f"同一レイアウト {tag} が3枚連続（p{_st['page']}）")
    rect(s, MX, 0.50, 0.09, 0.26, COLORS["primary"])
    txt(s, 0.80, 0.48, 11.5, 0.30, kicker, 11.5, COLORS["primary"], True)
    txt(s, 0.58, 0.80, 12.00, 0.62, title, 27, COLORS["ink"], True, line=1.15)
    rect(s, MX, 1.53, 1.75, 0.05, COLORS["primary_dk"])
    rect(s, MX, 1.55, CW, 0.01, COLORS["border"])
    txt(s, 12.40, PAGE_Y, 0.70, 0.30, f"{_st['page']:02d}", 10.5,
        COLORS["muted"], align=PP_ALIGN.RIGHT)
    if lead:
        txt(s, MX, 1.68, CW, 0.3, lead, 11.5, COLORS["muted"])
    return s


def table(slide, x, y, w, rows, col_w, row_h=0.44, head_h=0.46,
          fs=11.5, aligns=None, hl=None):
    hl = hl or []
    ncol = len(rows[0])
    tot = sum(col_w)
    col_w = [c / tot * w for c in col_w]
    aligns = aligns or [PP_ALIGN.LEFT] + [PP_ALIGN.RIGHT] * (ncol - 1)
    cy = y
    for ri, row in enumerate(rows):
        h = head_h if ri == 0 else row_h
        bg = COLORS["primary"] if ri == 0 else (
            COLORS["surface"] if ri in hl else
            (COLORS["bg"] if ri % 2 == 1 else COLORS["surface_alt"]))
        rect(slide, x, cy, w, h, bg)
        cx = x
        for ci, cell in enumerate(row):
            v = str(cell)
            strong = v.startswith("**")
            v = v.replace("**", "")
            col = COLORS["bg"] if ri == 0 else (COLORS["primary"] if strong else COLORS["text"])
            txt(slide, cx + 0.12, cy, col_w[ci] - 0.24, h, v, fs, col,
                bold=(ri == 0) or strong,
                align=aligns[ci] if ci < len(aligns) else PP_ALIGN.LEFT,
                line=1.0, anchor=MSO_ANCHOR.MIDDLE, space_after=0)
            cx += col_w[ci]
        cy += h
    return cy


def kpi(slide, x, y, w, h, value, label, note=None, accent=None, vcolor=None, vsize=28):
    card(slide, x, y, w, h, accent or COLORS["primary"])
    txt(slide, x + 0.22, y + 0.22, w - 0.44, 0.28, label, 10.5, COLORS["gray"], True)
    txt(slide, x + 0.22, y + 0.54, w - 0.44, 0.6, value, vsize,
        vcolor or COLORS["primary"], True, line=1.1)
    if note:
        txt(slide, x + 0.22, y + h - 0.56, w - 0.44, 0.46, note, 9.5, COLORS["muted"], line=1.3)


def panel(slide, x, y, w, h, label, title, body, accent=None, dark=False):
    rect(slide, x, y, w, h, COLORS["primary"] if dark else COLORS["surface"])
    if accent and not dark:
        rect(slide, x, y, w, 0.05, accent)
    txt(slide, x + 0.23, y + 0.2, w - 0.46, 0.28, label, 10.5,
        COLORS["slate_lt"] if dark else COLORS["gray"], True)
    ty = y + 0.46
    if title:
        txt(slide, x + 0.23, ty, w - 0.46, 0.38, title, 15.5,
            COLORS["bg"] if dark else COLORS["ink"], True)
        ty += 0.48
    txt(slide, x + 0.26, ty, w - 0.52, h - (ty - y) - 0.18, body, 12,
        COLORS["bg"] if dark else COLORS["text"], line=1.55)


def note_line(slide, y, s):
    txt(slide, MX, y, CW, 0.4, s, 9.5, COLORS["muted"], line=1.35)


def bullets(items, mark="･"):
    return "\n".join(f"{mark}  {t}" for t in items)


def chart(slide, kind, x, y, w, h, cats, series, colors, legend=False,
          lblsize=11, lblcolor=None, gap=60):
    cd = CategoryChartData()
    cd.categories = cats
    for nm, vals in series:
        cd.add_series(nm, vals)
    gf = slide.shapes.add_chart(kind, I(x), I(y), I(w), I(h), cd)
    ch = gf.chart
    ch.font.size = Pt(10)
    ch.font.name = FONT_JA
    ch.font.color.rgb = COLORS["text"]
    if legend:
        ch.has_legend = True
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(10)
    else:
        ch.has_legend = False
    try:
        va = ch.value_axis
        va.has_major_gridlines = True
        va.major_gridlines.format.line.color.rgb = COLORS["border"]
        va.major_gridlines.format.line.width = Pt(0.5)
        va.tick_labels.font.size = Pt(9.5)
        va.format.line.fill.background()
    except Exception:
        pass
    try:
        ca = ch.category_axis
        ca.tick_labels.font.size = Pt(9.5)
        ca.format.line.color.rgb = COLORS["border"]
    except Exception:
        pass
    pl = ch.plots[0]
    pl.gap_width = gap
    pl.has_data_labels = True
    pl.data_labels.font.size = Pt(lblsize)
    pl.data_labels.font.bold = True
    pl.data_labels.font.color.rgb = lblcolor or COLORS["ink"]
    for i, c in enumerate(colors):
        sr = pl.series[i]
        sr.format.fill.solid()
        sr.format.fill.fore_color.rgb = c
    return ch, pl


C3 = (CW - G * 2) / 3
C2 = (CW - G) / 2
C4 = (CW - G * 3) / 4
X3 = [MX + i * (C3 + G) for i in range(3)]
X2 = [MX + i * (C2 + G) for i in range(2)]

# ══ 01 表紙 ══════════════════════════════════════
s = prs.slides.add_slide(BLANK)
rect(s, 8.75, 0, 4.58, SH, COLORS["primary"])
rect(s, 8.75, 0, 0.06, SH, COLORS["accent"])
txt(s, 0.90, 0.90, 5.8, 0.4, "望月リソルゴルフクラブ 第2期会員募集", 13, COLORS["primary"], True)
rect(s, 0.95, 1.55, 6.90, 0.02, COLORS["hairline"])
txt(s, 0.90, 2.60, 7.4, 1.5, "2026年8月\nWEB広告 配信提案", 33, COLORS["ink"], True, line=1.2)
txt(s, 9.15, 3.05, 3.6, 1.6, "Mochizuki Resol\nGolf Club\n\n8月 配信提案",
    22, COLORS["bg"], True, line=1.35)
txt(s, 0.92, 4.42, 7.0, 0.6, "視察プレー期間 最終月の刈り取りプラン", 15, COLORS["text"])
rect(s, 0.95, 5.95, 2.30, 0.04, COLORS["primary_dk"])
txt(s, 0.92, 6.20, 7.0, 0.9, "2026年7月 ／ ゲンダイエージェンシー株式会社", 11.5, COLORS["gray"])
_st["page"] = 1
_st["layouts"].append("A")

# ══ 02 サマリー ═══════════════════════════════════
s = slide_new("サマリー", "ご提案の要旨", tag="F")
panel(s, MX, BODY_Y, CW, 1.02, "結論",
      "「予算を増やす」提案ではなく、「予算の向き先を変える」提案です",
      "成果の53%を生んでいる地元に配信を戻し、視察プレーが終わる8月30日までに刈り取ります。",
      accent=COLORS["accent"])
txt(s, MX, BODY_Y + 1.28, CW, 0.3, "なぜ、いま8月なのか", 15.5, COLORS["ink"], True)
K = [("8月30日", "視察プレー受付 終了", "残り40日。訴求できる最後の月です"),
     ("最終導線", "プレー後15分の商談", "会員獲得に直結する導線です"),
     ("次は来季", "逃すと次シーズンまで", "同じ訴求は今期できません")]
for i, (v, l, n) in enumerate(K):
    kpi(s, X3[i], BODY_Y + 1.64, C3, 1.42, v, l, n, accent=COLORS["primary"], vsize=25)
txt(s, MX, BODY_Y + 3.3, CW, 0.3, "ご提案する打ち手", 15.5, COLORS["ink"], True)
txt(s, MX, BODY_Y + 3.66, CW, 1.0,
    bullets(["配信エリアをゴルフ場から半径50〜80km圏へ戻す（追加費用なし）",
             "検討層への再接触（リターゲティング）を予算比9%→20〜25%へ強化",
             "配信面を整理し、媒体構成を成果が出ていた時期に戻す"]),
    13, COLORS["text"], line=1.62)

# ══ 03 現状 ══════════════════════════════════════
s = slide_new("1 現状", "第1期・第2期の比較", tag="G",
              lead="予算を30%増やし、集客を1.8倍に伸ばしながら、お問い合わせは1/3以下に減少しました。")
KP = [("+30.0%", "月あたりご請求額", COLORS["primary"]),
      ("1.8倍", "月あたりサイト集客", COLORS["primary"]),
      ("−89%", "お問い合わせ", COLORS["accent"]),
      ("4.63倍", "獲得単価", COLORS["accent"])]
for i, (v, l, c) in enumerate(KP):
    kpi(s, MX + i * (C4 + G), BODY_Y + 0.24, C4, 1.3, v, l, accent=c, vcolor=c, vsize=30)
rows = [
    ["", "第1期  2025年8月〜2026年3月（8ヶ月）", "第2期  2026年5月〜7月（3ヶ月）"],
    ["月あたりご請求額", "¥251,250", "¥326,667"],
    ["月あたりサイト集客", "6,427", "11,715"],
    ["**お問い合わせ", "**19件（月2.4件）", "**2件（月0.67件）"],
    ["**獲得単価", "**¥105,789", "**¥490,000"],
    ["「具体的に検討している」比率", "68%", "0%"],
]
table(s, MX, BODY_Y + 1.8, CW, rows, [4.2, 4.0, 3.9], hl=[3, 4], row_h=0.44, head_h=0.46)
note_line(s, 6.36,
          "〈実測〉ご請求額＝弊社基幹システム／集客＝GA4／お問い合わせ＝通知メールの実件数（スパム・テスト送信を除外）。\n"
          "比較期間はお問い合わせの実データが確認できている期間に揃え、2026年4月（LP刷新期間）は除外しています。")

# ══ 04 分析① 地元 ═══════════════════════════════
s = slide_new("2 分析", "成果の53%は、ゴルフ場から概ね70km圏内でした", tag="D")
chart(s, XL_CHART_TYPE.BAR_CLUSTERED, MX, BODY_Y, 7.3, 3.3,
      ["概ね30km圏\n佐久・小諸・軽井沢・御代田", "概ね40km圏\n上田市", "概ね70km圏\n群馬県高崎市",
       "概ね90km圏\n長野県松本市", "首都圏\n東京・神奈川・千葉"],
      [("件数", (7, 2, 1, 1, 8))], [COLORS["primary"]], gap=45, lblsize=12)
rx, rw = MX + 7.3 + G, CW - 7.3 - G
kpi(s, rx, BODY_Y, rw, 1.46, "53%", "概ね70km圏内の累計",
    "19件中10件。佐久市内2件・隣接町村5件", accent=COLORS["accent"],
    vcolor=COLORS["accent"], vsize=32)
panel(s, rx, BODY_Y + 1.66, rw, 1.64, "両論併記", "首都圏も切れません",
      "首都圏は8件（42%）。件数は少ないものの「具体的に検討している」比率は75%と、地元（64%）を上回ります。",
      accent=COLORS["gray"])
note_line(s, 5.62,
          "〈実測〉距離帯はお問い合わせ記載の郵便番号・住所から分類。母集団＝第1期の全19件。\n"
          "〈方向性〉母数が少ないため、比率の差は断定ではなく方向性としてご理解ください。")

# ══ 05 分析② エリア・媒体構成 ═══════════════════
s = slide_new("2 分析", "配信エリア・媒体構成と成果は、月単位で対応していました", tag="G")
txt(s, MX, BODY_Y, C2, 0.3, "Meta広告の配信エリアと成果", 13, COLORS["ink"], True)
rows = [
    ["配信エリア", "該当月", "件数"],
    ["**半径24〜50km圏", "**2025/10・26/01・02・03・06", "**計12件"],
    ["東京23区", "2025/09・12", "計5件"],
    ["**3都県へ拡大", "**2026/07", "**0件"],
]
table(s, MX, BODY_Y + 0.36, C2, rows, [2.3, 2.6, 1.2], hl=[1, 3], row_h=0.48, head_h=0.46)
txt(s, X2[1], BODY_Y, C2, 0.3, "媒体構成の変化（配信費ベース）", 13, COLORS["ink"], True)
rows2 = [
    ["", "Google", "Meta", "DV360", "件数/月"],
    ["**第1期 月平均", "**38%", "33%", "28%", "**2.4件"],
    ["**第2期 月平均", "**16%", "42%", "42%", "**0.67件"],
    ["2026年7月", "17%", "**83%", "0%", "**0件"],
]
table(s, X2[1], BODY_Y + 0.36, C2, rows2, [1.9, 1.0, 1.0, 1.0, 1.1],
      hl=[1, 2], row_h=0.48, head_h=0.46)
panel(s, MX, BODY_Y + 2.54, C2, 1.46, "所見", "エリアを広げた月に0件",
      "最良月は2026年3月（半径48〜49km・5件・獲得単価¥50,000）。3都県に広げた7月は0件でした。",
      accent=COLORS["accent"])
panel(s, X2[1], BODY_Y + 2.54, C2, 1.46, "所見", "Google広告が半減しました",
      "月¥75,000から¥40,000へ。7月はMeta広告に83%が集中。最良月でさえMeta広告は¥40,000でした。",
      accent=COLORS["accent"])
note_line(s, 6.12,
          "〈実測〉Meta Marketing API の月別広告セット設定／ご請求データの配信費構成比。\n"
          "〈両論併記〉7月1日にはエリア拡大に加えP-MAX移行・DV360停止も同時に発生しており、エリア単独の因果は証明できません。")

# ══ 06 分析③ 配信品質 ══════════════════════════
s = slide_new("2 分析", "買ったクリックが、サイトに届いていません", tag="D")
card(s, MX, BODY_Y, CW, 0.64, COLORS["primary"])
txt(s, MX, BODY_Y, CW, 0.64, "サイト到達率　＝　GA4のセッション数　÷　広告のクリック数",
    15.5, COLORS["ink"], True, PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
kpi(s, X2[0], BODY_Y + 0.88, C2, 1.5, "43.0%", "LINEヤフー広告",
    "クリック率0.12%。ディスプレイとして健全な水準", accent=COLORS["primary"], vsize=32)
kpi(s, X2[1], BODY_Y + 0.88, C2, 1.5, "15.9%", "DV360",
    "クリック率11.30%。誤タップが大半を占めます", accent=COLORS["accent"],
    vcolor=COLORS["accent"], vsize=32)
panel(s, MX, BODY_Y + 2.58, C2, 1.42, "内訳", "65面がクリックの61%を占めます",
      "クリック率5%超の配信面が65面あり、配信費の47%を使っています。除外したうえで再開します。",
      accent=COLORS["accent"])
panel(s, X2[1], BODY_Y + 2.58, C2, 1.42, "両論併記", "良質な面もあります",
      "MILE mobileは平均滞在28.7秒。アプリ面が一律に悪いわけではなく、面ごとの選別が有効です。",
      accent=COLORS["gray"])
note_line(s, 6.12,
          "〈実測〉クリック数＝各媒体API／セッション数＝GA4。DV360は全配信面9,833行を取得して突合。\n"
          "〈業界一般〉ディスプレイ広告のクリック率は通常0.1〜0.5%程度とされます。")

# ══ 07 課題と打ち手 ═════════════════════════════
s = slide_new("3 提案", "3つの課題と打ち手", tag="E",
              lead="いずれも「広告を増やす／減らす」ではなく、「向き先を変える」ことで対応できます。")
items = [
    ("課題 01", "配信エリアが広すぎる", "成果の53%が概ね70km圏／長野の集客は16.7%",
     "半径50〜80km圏へ戻す", "東京は停止せず別枠に分離し、エリア別に成果を測る", "追加費用なし"),
    ("課題 02", "検討層への再接触が足りない", "クリック率は1.57倍なのに予算9%・接触2.12回",
     "リターゲティングを強化する", "比率を9%→20〜25%、接触回数4〜5回へ", "予算内"),
    ("課題 03", "配信面と媒体構成の偏り", "DV360の到達率15.9%／7月はMeta83%の一極集中",
     "配信面を整理し、構成を戻す", "65面を除外して再開／Google広告を第1期水準へ", "予算内"),
]
y = BODY_Y + 0.32
lw = 5.2
for no, ttl, ev, act, det, cost in items:
    card(s, MX, y, lw, 1.4, COLORS["accent"])
    txt(s, MX + 0.22, y + 0.22, 1.3, 0.24, no, 10.5, COLORS["accent"], True)
    txt(s, MX + 0.22, y + 0.5, lw - 0.44, 0.3, ttl, 14.5, COLORS["ink"], True)
    txt(s, MX + 0.22, y + 0.88, lw - 0.44, 0.36, ev, 9.5, COLORS["muted"])
    txt(s, MX + lw + 0.06, y + 0.5, 0.4, 0.34, "▶", 14, COLORS["gray"], True, PP_ALIGN.CENTER)
    ax = MX + lw + 0.52
    aw = CW - lw - 0.52
    rect(s, ax, y, aw, 1.4, COLORS["primary"])
    txt(s, ax + 0.24, y + 0.26, aw - 1.7, 0.3, act, 14.5, COLORS["bg"], True)
    txt(s, ax + 0.24, y + 0.68, aw - 1.7, 0.5, det, 9.5, COLORS["hairline"], line=1.4)
    txt(s, ax + aw - 1.55, y + 0.52, 1.32, 0.3, cost, 11, COLORS["accent"], True, PP_ALIGN.RIGHT)
    y += 1.56

# ══ 08 配信プラン ═══════════════════════════════
s = slide_new("3 提案", "2026年8月 配信プラン", tag="G",
              lead="視察プレー期間の最終月として、期間限定オファーの刈り取りに集中します。")
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
table(s, MX, BODY_Y + 0.24, CW, rows, [2.6, 5.9, 1.8, 1.6],
      aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
      hl=[7], row_h=0.42, head_h=0.44)
panel(s, MX, BODY_Y + 3.56, C2, 1.14, "補足", "Meta広告は減額しません",
      "内訳を組み替えて、一極集中（83.3%）を47.6%まで下げます。", accent=COLORS["primary"])
panel(s, X2[1], BODY_Y + 3.56, C2, 1.14, "あわせて実施", "追加費用なしの改善",
      "視察プレー訴求へのクリエイティブ差し替え／入口は資料請求に設定／コンバージョン計測を各媒体へ接続。",
      accent=COLORS["primary"])
note_line(s, 6.7, "〈実測〉7月実績＝ご請求データ。〈提案〉8月の構成比は本プランに基づく計画値です。")

# ══ 09 KPIと進行 ════════════════════════════════
s = slide_new("3 提案", "KPIと進行", tag="F")
K = [("3〜5件", "お問い合わせ", "第1期の月平均2.4件／最良月5件", COLORS["primary"]),
     ("¥105,000\n〜175,000", "獲得単価", "5件なら第1期平均と同水準", COLORS["primary"]),
     ("40%以上", "地元の集客構成比", "現在19%", COLORS["accent"]),
     ("40%以上", "DV360のサイト到達率", "現在15.9%", COLORS["accent"])]
for i, (v, l, n, c) in enumerate(K):
    kpi(s, MX + i * (C4 + G), BODY_Y + 0.22, C4, 1.6, v, l, n,
        accent=c, vcolor=c, vsize=20 if "\n" in v else 28)
rows = [
    ["期日", "内容"],
    ["7月下旬", "配信エリアの設定変更／DV360除外リスト作成／クラブ名検索の除外／コンバージョン計測の接続"],
    ["7月末", "クリエイティブを視察プレー訴求へ差し替え／LINEヤフー広告の入稿"],
    ["**8月1日", "**配信開始"],
    ["8月中旬", "中間レポート・配分の見直し"],
    ["**8月30日", "**視察プレー受付終了"],
    ["9月上旬", "8月実績のご報告・9月以降のご提案"],
]
table(s, MX, BODY_Y + 2.06, CW, rows, [1.6, 10.5],
      aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT], hl=[3, 5], row_h=0.42, head_h=0.44, fs=11)
note_line(s, 6.38,
          "〈当社仮説〉KPIは第1期の実績水準を根拠とした目標値であり、達成を保証するものではありません。\n"
          "週次でご報告し、8月中旬に配分を見直します。")

# ══ 10 ご依頼事項 ═══════════════════════════════
s = slide_new("4 依頼", "ご依頼事項", tag="C")
panel(s, MX, BODY_Y, CW, 1.32, "お願い",
      "公式サイト経由のお問い合わせ実績をご共有ください",
      "月別・「会員権について 知ったきっかけ」別で、2024年10月以降をいただけますと幸いです。",
      accent=COLORS["accent"])
txt(s, MX, BODY_Y + 1.62, CW, 0.3, "背景", 13, COLORS["ink"], True)
txt(s, MX, BODY_Y + 1.98, CW, 1.5,
    bullets([
        "LPから公式サイトへ、全期間で1,430件の遷移が発生しています（2026年7月は75%が広告経由）",
        "公式サイトのフォームには「知ったきっかけ」が必須項目としてあり、「Googleの広告」「Facebook/Instagram等の広告」が選択肢に含まれています",
        "広告経由のお問い合わせが公式サイト側で受け付けられている可能性があり、現時点の集計（LP経由のみ）は実際の成果を過小評価している可能性があります",
    ]),
    12, COLORS["text"], line=1.6)
panel(s, MX, BODY_Y + 3.62, CW, 1.06, "このデータで確定すること", "",
      "広告の実際の成果（LP＋公式サイトの合算）　／　LPと公式サイトの導線を一本化すべきか　／　第1期・第2期比較の精度",
      accent=COLORS["primary"])
note_line(s, 6.72,
          "本提案の出典：お問い合わせ通知メールの実データ／Google Analytics 4／Google Ads API／Meta Marketing API／"
          "DV360 Bid Manager API／LINEヤフー広告API／弊社基幹システム")

os.makedirs(OUT_DIR, exist_ok=True)
prs.save(OUT)
print(f"保存: {OUT}")
print(f"全{_st['page']}枚 / レイアウト順: {' '.join(_st['layouts'])}")
