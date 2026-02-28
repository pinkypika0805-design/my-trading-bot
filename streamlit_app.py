import streamlit as st
from datetime import datetime
import pytz

# 設定網頁標題
st.set_page_config(page_title="Annex Garage 交易系統 V3", page_icon="🏎️")
st.title("🏹 進階當沖進場檢核 (V3)")
st.caption("實驗目標：每日一單，嚴格遵守趨勢與力竭訊號觀測")

# --- 1. 時間檢查 (自動判斷台灣時間) ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 左側數據輸入 ---
st.sidebar.header("📊 盤中數據填寫")
ticker = st.sidebar.text_input("股票代號", value="2330")
price = st.sidebar.number_input("當前成交價", value=200.0, step=0.5)
open_p = st.sidebar.number_input("開盤價", value=195.0, step=0.5)
ma_p = st.sidebar.number_input("均價線 (VWAP/均線)", value=198.0, step=0.5)

st.sidebar.markdown("---")
stop_p = st.sidebar.number_input("預計停損價", value=197.0, step=0.5)
target_p = st.sidebar.number_input("預期獲利點", value=210.0, step=0.5)

# --- 3. 自動趨勢判定 (順勢/逆勢) ---
st.subheader("🌍 市場環境與趨勢判定")
is_above_open = price > open_p
is_above_ma = price > ma_p

# 順勢定義：價在開盤與均價之上
trend_type = "🟢 順勢 (多頭強勢)" if (is_above_open and is_above_ma) else "🔴 逆勢 (注意反彈或摸頂風險)"
st.info(f"**目前趨勢判定：{trend_type}** (開盤價之上: {'✅' if is_above_open else '❌'} / 均價線之上: {'✅' if is_above_ma else '❌'})")

col1, col2 = st.columns(2)
with col1:
    market_state = st.selectbox("1. 大盤/櫃買狀態", ["請選擇", "開高", "開平", "開低"])
    direction = st.selectbox("2. 開盤後出方向", ["請選擇", "往上衝", "往下殺", "橫盤震盪"])

with col2:
    structure_signal = st.radio("3. 結構訊號 (K棒慣性)", ["無訊號", "高不過高 (轉弱)", "低不過低 (支撐)"])
    exhaustion_signal = st.checkbox("🚩 出現大單力竭 (敲過 3-4 tick 又縮回)")

# --- 4. 核心準則驗證 ---
st.markdown("---")
st.subheader("🔍 進場準則驗證")

# A. 時間與環境檢查
time_ok = can_trade_time
env_ok = market_state != "請選擇" and direction != "請選擇"

# B. 手動確認關鍵動作
key_level = st.checkbox("🔑 已【突破】或【跌破】關鍵價位")
trend_confirm = st.checkbox(f"⚖️ 我已知曉目前為「{trend_type}」並願意承擔風險")

# C. 損益比
risk = abs(price - stop_p)
reward = abs(target_p - price)
rr_ratio = reward / risk if risk > 0 else 0
rr_ok = rr_ratio >= 2.0

# --- 5. 綜合判斷結果 ---
st.markdown("---")
# 這裡加入你的所有條件總和
final_check = all([time_ok, env_ok, key_level, trend_confirm, rr_ok, exhaustion_signal == False])

if final_check:
    st.balloons()
    st.markdown("## 🟢 【准許進場】")
    st.warning(f"提醒：嚴格執行 {stop_p} 停損，不攤平。")
else:
    st.markdown("## 🔴 【條件未齊 - 觀望】")
    if not time_ok: st.warning(f"⚠️ 時間未到 9:10 (目前 {current_time_str})")
    if exhaustion_signal: st.error("⚠️ 警告：偵測到大單力竭訊號，小心假突破！")
    if not rr_ok: st.warning(f"⚠️ 損益比不足 ({rr_ratio:.2f})")
    if not key_level: st.warning("⚠️ 關鍵價位未確認")

# --- 6. 數據卡片 ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("風控上限", "30 萬")
shares = int(300000 // (price * 1.001425))
c3.metric("建議股數", f"{shares}")
