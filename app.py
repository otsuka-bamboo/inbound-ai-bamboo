import streamlit as st
import pandas as pd
import plotly.express as px

# OpenAI SDK (v1系)
try:
    from openai import OpenAI
    has_openai_v1 = True
except Exception:
    has_openai_v1 = False

st.set_page_config(page_title="Inbound AI Dashboard", layout="wide")
st.title("🌏 訪日外国人分析 × AI改善提案（プロトタイプ）")

st.markdown("""
このデモは、**国別データ**（訪日客数・宿泊単価・口コミスコア）をもとに、
AIが **改善提案** を自動生成する試作品です。  
CSVをアップロードするか、下の**デモデータ**で動作します。
""")

# -----------------------------
# 1) データ入力
# -----------------------------
st.subheader("1️⃣ データ入力（CSV アップロード推奨）")
st.caption("列名の例：国名,訪日客数,宿泊単価,口コミスコア")

uploaded = st.file_uploader("CSVを選択してください（未選択ならデモデータを使用）", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
else:
    st.info("デモデータで表示中（5カ国）")
    df = pd.DataFrame({
        "国名": ["台湾", "韓国", "中国", "アメリカ", "オーストラリア"],
        "訪日客数": [450000, 380000, 310000, 120000, 85000],
        "宿泊単価": [13500, 12000, 15000, 20000, 18500],
        "口コミスコア": [4.3, 4.1, 3.8, 4.6, 4.4]
    })

# 最低限の列チェック
required_cols = {"国名", "訪日客数", "宿泊単価", "口コミスコア"}
if not required_cols.issubset(set(df.columns)):
    st.error(f"CSVの列名が不足しています。必要な列: {', '.join(required_cols)}")
    st.stop()

# -----------------------------
# 2) 可視化
# -----------------------------
st.subheader("2️⃣ 可視化（国別の傾向）")
c1, c2 = st.columns(2)

with c1:
    fig1 = px.bar(df, x="国名", y="訪日客数", title="訪日客数（国別）", text="訪日客数")
    fig1.update_layout(xaxis_title="", yaxis_title="訪日客数")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.scatter(
        df, x="口コミスコア", y="宿泊単価",
        size="訪日客数", color="国名",
        title="口コミスコア × 宿泊単価（バブル＝訪日客数）"
    )
    fig2.update_layout(xaxis_title="口コミスコア（★）", yaxis_title="宿泊単価（円）")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 3) AI 改善提案
# -----------------------------
st.subheader("3️⃣ AI 改善提案（最大3項目、定量効果つき）")

api_ok = False
if "OPENAI_API_KEY" in st.secrets:
    try:
        if has_openai_v1:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            api_ok = True
    except Exception as e:
        st.warning(f"OpenAIクライアント初期化に失敗：{e}")

with st.expander("AIに渡している表（確認用）", expanded=False):
    st.dataframe(df)

prompt = f"""
あなたは訪日観光コンサルタントです。
以下の「国別データ」（国名, 訪日客数, 宿泊単価, 口コミスコア）を読み、
「訪日外国人の集客・単価・満足度」を改善するための施策を **最大3つ**、箇条書きで提案してください。

要件:
- できるだけ具体的（例：どの国を狙う／どのチャネル／何を改善）
- 各施策に **期待効果（数値例: ADR +8〜12% など）** を付す
- 90日内にできる「即効策」を1つ以上含める

データ（表形式）:
{df.to_markdown(index=False)}
"""

btn = st.button("💡 AI提案を生成する")
if btn:
    if not api_ok:
        st.error("OpenAIのAPIキーが設定されていません。[App settings → Secrets] に `OPENAI_API_KEY` を保存してください。")
    else:
        with st.spinner("AIが分析中…"):
            try:
                chat = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "あなたは実務派の観光・ホテル再生コンサルタントです。短く、要点を定量で。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=600
                )
                st.success("改善提案")
                st.markdown(chat.choices[0].message.content)
            except Exception as e:
                st.error(f"AI呼び出しでエラーが発生しました：{e}")

st.caption("※ 本プロトタイプはデモ用。実運用では観光庁・JNTO・OTA・口コミAPIなどを自動連携予定。")
