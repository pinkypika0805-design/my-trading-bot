import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Annex Garage 交易系統 V4.0", page_icon="🏎️")
st.title("🏹 精準當沖進場檢核 (V4.0)")

# --- 1. 時間檢查 ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 側邊欄：設定 ---
st.sidebar.header("💰 交易設定")
trade_type = st.sidebar.radio("操作方向", ["做多 (Long)", "做空 (Short)"])
max_cap = st.sidebar.slider("額度上限 (萬)", 30, 50, 30) * 10000

ticker = st.sidebar.text_input("股票代號", value="2330")
price = st.sidebar.number_input("當前成交價", value=200.0, step=0.5)
open_p = st.sidebar.number_input("開盤價", value=195.0, step=0.5)
ma_p = st.sidebar.number_input("均價線", value=198.0, step=0.5)

st.sidebar.markdown("---")
if trade_type == "做多 (Long)":
    stop_p = st.sidebar.number_input("預計停損價", value=price * 0.98, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 1.05, step=0.5)
else:
    stop_p = st.sidebar.number_input("預計停損價", value=price * 1.02, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 0.95, step=0.5)

# --- 3. 趨勢判定 ---
st.subheader(f"🌍 當前操作：{trade_type}")
if trade_type == "做多 (Long)":
    is_trend = (price > open_p and price > ma_p)
else:
    is_trend = (price < open_p and price < ma_p)

trend_label = "🟢 順勢格局" if is_trend else "🔴 逆勢操作"
st.info(f"**趨勢分析：{trend_label}**")

col1, col2 = st.columns(2)
with col1:
    market_state = st.selectbox("1. 大盤/櫃買開盤", ["請選擇", "開高", "開平", "開低"])
with col2:
    direction = st.selectbox("2. 個股開盤方向", ["請選擇", "往上衝", "往下殺", "橫盤震盪"])

# --- 4. 核心準則檢核 ---
st.markdown("---")
st.subheader("🔍 進場準則最終檢核")

col3, col4 = st.columns(2)
with col3:
    m_momentum = st.selectbox("🚩 目前大盤/櫃買慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])
    
    s_signal = st.selectbox("📈 K 棒結構觀察", [
        "請選擇", 
        "高不過高 (轉弱)", 
        "低不過低 (支撐)", 
        "橫
