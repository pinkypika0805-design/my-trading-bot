import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf

st.set_page_config(page_title="Annex Garage 交易系統 V5.6", page_icon="🏎️")
st.title("🏹 精準當沖進場檢核 (V5.6)")
st.caption("策略核心：逆勢轉折 - 抓取爆量不破之位階")

# --- 1. 時間檢查 ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 側邊欄設定 ---
st.sidebar.header("💰 交易數據輸入")
trade_type = st.sidebar.radio("操作方向", ["做多 (Long)", "做空 (Short)"])
max_cap = st.sidebar.slider("額度上限 (萬)", 30, 50, 30) * 10000

ticker_input = st.sidebar.text_input("股票代號", value="2330")

if 'auto_data' not in st.session_state:
    st.session_state.auto_data = {"name": "待抓取", "last_close": 195.0, "open": 195.0, "current": 200.0}

if st.sidebar.button("🔍 自動抓取數據"):
    try:
        stock = yf.Ticker(f"{ticker_input}.TW")
        hist = stock.history(period="2d")
        if hist.empty:
            stock = yf.Ticker(f"{ticker_input}.TWO")
            hist = stock.history(period="2d")
        if not hist.empty:
            info = stock.info
            st.session_state.auto_data["name"] = info.get('shortName', ticker_input)
            st.session_state.auto_data["last_close"] = hist['Close'].iloc[-2]
            st.session_state.auto_data["open"] = hist['Open'].iloc[-1]
            st.session_state.auto_data["current"] = hist['Close'].iloc[-1]
    except:
        st.sidebar.error("抓取失敗")

st.sidebar.markdown(f"### 🎯 {st.session_state.auto_data['name']}")
price = st.sidebar.number_input("當前成交價", value=float(st.session_state.auto_data["current"]), step=0.5)
last_close = st.sidebar.number_input("平盤價", value=float(st.session_state.auto_data["last_close"]), step=0.5)
open_p = st.sidebar.number_input("開盤價", value=float(st.session_state.auto_data["open"]), step=0.5)
ma_p = st.sidebar.number_input("均價線", value=price, step=0.5)

if trade_type == "做多 (Long)":
    stop_p = st.sidebar.number_input("預計停損價", value=price * 0.985, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 1.03, step=0.5)
else:
    stop_p = st.sidebar.number_input("預計停損價", value=price * 1.015, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 0.97, step=0.5)

# --- 3. 環境判定 ---
open_gap = ((open_p - last_close) / last_close) * 100
strength = "🔥 極強 (5%↑)" if open_gap >= 5.0 else "💪 強 (3%↑)" if open_gap >= 3.0 else "⚖️ 普通"
st.info(f"**開盤強度：{strength} ({open_gap:.2f}%)**")

# --- 4. 準則檢核 (翻轉力竭邏輯) ---
st.markdown("---")
st.subheader("🔍 進場準則最終檢核")
c3, c4 = st.columns(2)
with c3:
    m_momentum = st.selectbox("🚩 大盤慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])
    s_signal = st.selectbox("📈 K 棒結構", ["請選擇", "高不過高 (轉弱)", "低不過低 (支撐)", "橫盤整理 (不建議)", "無明顯訊號"])
    
    # 動態力竭選項
    if trade_type == "做多 (Long)":
        exhaust_signal = st.checkbox("🎯 底部力竭 (下殺爆量不破，準備反彈)")
        bad_exhaust = st.checkbox("⚠️ 高點力竭 (上攻爆量不破，多單警訊)")
    else:
        exhaust_signal = st.checkbox("🚩 高點力竭 (上攻爆量不破，準備下殺)")
        bad_exhaust = st.checkbox("⚠️ 底部力竭 (下殺爆量不破，空單警訊)")

with c4:
    key_level = st.checkbox("🔑 關鍵價位 (突破/跌破/支撐/壓力)")
    risk_confirm = st.checkbox("⚖️ 我知曉做多/做空風險")
    plan_ok = st.checkbox("✅ 符合今日交易計畫 (訊號出現)")

# --- 5. 綜合判斷 ---
st.markdown("---")
env_ok = all([m_momentum != "請選擇", s_signal != "請選擇"])
risk_dist = abs(price - stop_p)
rr_ratio = abs(target_p - price) / risk_dist if risk_dist > 0 else 0
side_market = (s_signal == "橫盤整理 (不建議)")

# 准許進場邏輯：必須沒有「錯誤的力竭訊號」
can_enter = all([can_trade_time, env_ok, key_level, risk_confirm, plan_ok, rr_ratio >= 1.5, not bad_exhaust, not side_market])

if can_enter:
    st.balloons()
    st.success(f"## 🟢 【准許進場 - 整股一張】")
    if exhaust_signal:
        st.info("💡 偵測到轉折力竭訊號，具備逆勢進場優勢。")
else:
    st.error("## 🔴 【條件未齊 - 觀望】")
    if bad_exhaust: st.warning("⚠️ 注意：當前方向與力竭位置衝突（例如多頭遇到高點力竭）。")

c1, c2 = st.columns(2)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("設定額度", f"{int(max_cap/10000)} 萬")
