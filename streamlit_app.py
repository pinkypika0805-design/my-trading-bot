import streamlit as st
from datetime import datetime
import pytz

# 設定網頁標題
st.set_page_config(page_title="Annex Garage 交易系統 V3.2", page_icon="🏎️")
st.title("🏹 進階當沖進場檢核 (V3.2)")
st.caption("實驗目標：每日一單，動態額度控管 (30-50萬)")

# --- 1. 時間檢查 (自動判斷台灣時間) ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 左側數據輸入 ---
st.sidebar.header("💰 資金與數據填寫")
# 新增額度選擇滑桿 (30萬 - 50萬)
max_cap = st.sidebar.slider("本次交易額度上限 (萬)", 30, 50, 30) * 10000

ticker = st.sidebar.text_input("股票代號", value="2330")
price = st.sidebar.number_input("當前成交價", value=200.0, step=0.5)
open_p = st.sidebar.number_input("開盤價", value=195.0, step=0.5)
ma_p = st.sidebar.number_input("均價線 (VWAP/均線)", value=198.0, step=0.5)

st.sidebar.markdown("---")
stop_p = st.sidebar.number_input("預計停損價", value=197.0, step=0.5)
target_p = st.sidebar.number_input("預期獲利點", value=210.0, step=0.5)

# --- 3. 自動趨勢判定 ---
st.subheader("🌍 市場環境與趨勢判定")
is_above_open = price > open_p
is_above_ma = price > ma_p

trend_type = "🟢 順勢 (多頭格局)" if (is_above_open and is_above_ma) else "🔴 逆勢 (注意風險)"
st.info(f"**個股狀態
