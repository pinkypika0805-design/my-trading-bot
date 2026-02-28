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
st.info(f"**個股狀態：{trend_type}** (開盤之上: {'✅' if is_above_open else '❌'} / 均價之上: {'✅' if is_above_ma else '❌'})")

col1, col2 = st.columns(2)
with col1:
    market_state = st.selectbox("1. 大盤/櫃買開盤狀態", ["請選擇", "開高", "開平", "開低"])
    market_momentum = st.selectbox("2. 目前大盤/櫃買慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])

with col2:
    direction = st.selectbox("3. 個股開盤後出方向", ["請選擇", "往上衝", "往下殺", "橫盤震盪"])
    structure_signal = st.radio("4. K 棒結構訊號", ["無訊號", "高不過高 (轉弱)", "低不過低 (支撐)"])

# --- 4. 核心準則驗證 ---
st.markdown("---")
st.subheader("🔍 進場準則驗證")

col3, col4 = st.columns(2)
with col3:
    key_level = st.checkbox("🔑 突破/跌破關鍵價位")
    exhaustion_signal = st.checkbox("🚩 大單力竭 (敲過 3-4 tick 回縮)")
with col4:
    trend_confirm = st.checkbox("⚖️ 我知曉順逆勢風險")
    plan_ok = st.checkbox("✅ 符合今日交易計畫")

# --- 5. 綜合判斷結果 ---
st.markdown("---")
env_ok = all([market_state != "請選擇", market_momentum != "請選擇", direction != "請選擇"])
risk = abs(price - stop_p)
reward = abs(target_p - price)
rr_ratio = reward / risk if risk > 0 else 0
rr_ok = rr_ratio >= 2.0

final_check = all([can_trade_time, env_ok, key_level, plan_ok, rr_ok, exhaustion_signal == False])

if final_check:
    st.balloons()
    st.markdown(f"## 🟢 【准許進場】")
    st.success(f"目前大盤「{market_momentum}」，請密切觀察。")
else:
    st.markdown("## 🔴 【條件未齊 - 觀望】")
    if not can_trade_time: st.warning(f"⚠️ 時間未到 9:10 (目前 {current_time_str})")
    if exhaustion_signal: st.error("⚠️ 偵測到大單力竭，請勿進場！")
    if not rr_ok: st.warning(f"⚠️ 損益比不足 ({rr_ratio:.2f})")

# --- 6. 數據卡片 ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("當前風控額", f"{int(max_cap/10000)} 萬")
# 計算股數 (含手續費考慮)
shares = int(max_cap // (price * 1.001425))
c3.metric("建議最大買進", f"{shares} 股", f"{shares//1000} 張")
