import streamlit as st
import pandas as pd

st.set_page_config(page_title="Smoke Test", layout="wide")
st.title("✅ Smoke Test")
st.dataframe(pd.DataFrame({"国名":["台湾","韓国"], "訪日客数":[1,2]}))
st.success("Streamlit本体は起動OKです。")
