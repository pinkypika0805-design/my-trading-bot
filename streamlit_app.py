import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Annex Garage 交易系統 V3.8", page_icon="🏎️")
st.title("🏹 精準當沖進場檢核 (V3.8)")

# --- 1. 時間檢查 ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 側邊欄：資金與多空 ---
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

# --- 4. 核心準則檢核 (併入慣性與結構) ---
st.markdown("---")
st.subheader("🔍 進場準則最終檢核")

col3, col4 = st.columns(2)
with col3:
    # 移入大盤慣性與 K 棒結構
    m_momentum = st.selectbox("🚩 目前大盤/櫃買慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])
    s_signal = st.selectbox("📈 K 棒結構觀察", ["無明顯訊號", "高不過高 (轉弱)", "低不過低 (支撐)"])
    
    if trade_type == "做多 (Long)":
        exhaust_text = "🚩 高點大單力竭 (上攻無力)"
    else:
        exhaust_text = "🎯 底部大單力竭 (下殺無力)"
    exhaustion_signal = st.checkbox(exhaust_text)

with col4:
    key_level = st.checkbox("🔑 突破/跌破關鍵價位")
    risk_text = f"⚖️ 我知曉「{trade_type}」風險"
    trend_confirm = st.checkbox(risk_text)
    plan_ok = st.checkbox("✅ 符合今日交易計畫")

# --- 5. 綜合判斷結果 ---
st.markdown("---")
env_ok = all([market_state != "請選擇", m_momentum != "請選擇", direction != "請選擇"])
risk_dist = abs(price - stop_p)
reward_dist = abs(target_p - price)
rr_ratio = reward_dist / risk_dist if risk_dist > 0 else 0
rr_ok = rr_ratio >= 2.0

# 最終邏輯：排除力竭訊號，確保環境皆已選擇
can_enter = all([can_trade_time, env_ok, key_level, trend_confirm, plan_ok, rr_ok, not exhaustion_signal])

if can_enter:
    st.balloons()
    st.success(f"## 🟢 【准許進場 - {trade_type}】")
    st.info(f"大盤慣性：{m_momentum} / 結構：{s_signal}")
else:
    st.error("## 🔴 【條件未齊 - 觀望】")
    if exhaustion_signal: st.warning(f"⚠️ 偵測到「{exhaust_text}」，先收手！")
    if not env_ok: st.warning("⚠️ 請務必選擇「大盤開盤、大盤慣性、個股方向」")
    if not rr_ok: st.warning(f"⚠️ 損益比不足 ({rr_ratio:.2f})")
    if not can_trade_time: st.warning(f"⚠️ 未到 9:10 禁動手時間")

# --- 6. 數據卡片 ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("設定額度", f"{int(max_cap/10000)} 萬")
shares = int(max_cap // (price * 1.001425))
c3.metric("建議股數", f"{shares} 股")
