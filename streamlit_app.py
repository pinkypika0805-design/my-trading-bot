import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Annex Garage 交易系統 V3.4", page_icon="🏎️")
st.title("🏹 精準當沖進場檢核 (多空雙向版)")

# --- 1. 時間檢查 ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 側邊欄：資金與多空設定 ---
st.sidebar.header("💰 交易設定")
trade_type = st.sidebar.radio("本次操作方向", ["做多 (Long)", "做空 (Short)"])
max_cap = st.sidebar.slider("額度上限 (萬)", 30, 50, 30) * 10000

ticker = st.sidebar.text_input("股票代號", value="2330")
price = st.sidebar.number_input("當前成交價", value=200.0, step=0.5)
open_p = st.sidebar.number_input("開盤價", value=195.0, step=0.5)
ma_p = st.sidebar.number_input("均價線", value=198.0, step=0.5)

st.sidebar.markdown("---")
stop_p = st.sidebar.number_input("預計停損價", value=197.0 if trade_type == "作多 (Long)" else 203.0, step=0.5)
target_p = st.sidebar.number_input("預期獲利點", value=210.0 if trade_type == "作多 (Long)" else 190.0, step=0.5)

# --- 3. 自動趨勢判定 (多空邏輯翻轉) ---
st.subheader(f"🌍 市場環境 - 當前預計：{trade_type}")

# 多頭順勢：價在開盤/均線上；空頭順勢：價在開盤/均線下
if trade_type == "作多 (Long)":
    is_trend = (price > open_p and price > ma_p)
else:
    is_trend = (price < open_p and price < ma_p)

trend_label = "🟢 順勢格局" if is_trend else "🔴 逆勢操作 (注意反彈/殺多風險)"
st.info(f"**趨勢判定：{trend_label}**")

col1, col2 = st.columns(2)
with col1:
    market_state = st.selectbox("1. 大盤/櫃買開盤狀態", ["請選擇", "開高", "開平", "開低"])
    m_momentum = st.selectbox("2. 目前大盤/櫃買慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])

with col2:
    direction = st.selectbox("3. 個股開盤後出方向", ["請選擇", "往上衝", "往下殺", "橫盤震盪"])
    s_signal = st.selectbox("4. K 棒結構觀察", ["無明顯訊號", "高不過高 (轉弱)", "低不過低 (支撐)"])

# --- 4. 核心準則檢核 ---
st.markdown("---")
st.subheader("🔍 進場準則最終檢核")

col3, col4 = st.columns(2)
with col3:
    key_level = st.checkbox("🔑 突破/跌破關鍵價位")
    exhaustion_signal = st.checkbox("🚩 出現大單力竭 (敲過 3-4 tick 回縮)")
with col4:
    trend_confirm = st.checkbox(f"⚖️ 我知曉「{trade_type}」風險")
    plan_ok = st.checkbox("✅ 符合今日交易計畫")

# --- 5. 綜合判斷結果 ---
st.markdown("---")

# 損益比計算
risk = abs(price - stop_p)
reward = abs(target_p - price)
rr_ratio = reward / risk if risk > 0 else 0
rr_ok = rr_ratio >= 2.0

# 力竭訊號判斷：做多時有訊號為差，做空時有訊號為好
if trade_type == "作多 (Long)":
    exhaustion_ok = not exhaustion_signal
else:
    # 做空時，有力竭訊號反而是加分項，這裡設定為不阻礙進場
    exhaustion_ok = True 

env_ok = all([market_state != "請選擇", m_momentum != "請選擇", direction != "請選擇"])
final_check = all([can_trade_time, env_ok, key_level, plan_ok, rr_ok, exhaustion_ok])

if final_check:
    st.balloons()
    st.markdown(f"## 🟢 【准許進場 - {trade_type}】")
    if trade_type == "做空 (Short)" and exhaustion_signal:
        st.success("🎯 偵測到上攻力竭，符合放空時機。")
else:
    st.markdown(f"## 🔴 【條件未齊 - 觀望】")
    if trade_type == "作多 (Long)" and exhaustion_signal:
        st.error("⚠️ 偵測到力竭訊號，多單請勿進場！")
    if not rr_ok: st.warning(f"⚠️ 損益比不足 ({rr_ratio:.2f})")

# --- 6. 數據與檢討 ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("設定額度", f"{int(max_cap/10000)} 萬")
shares = int(max_cap // (price * 1.001425))
c3.metric("建議股數", f"{shares} 股")

if st.button("🚀 錄入交易檢討"):
    st.write("請前往您的檢討表單填寫紀錄。")
