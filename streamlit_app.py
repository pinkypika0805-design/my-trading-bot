import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf

st.set_page_config(page_title="Annex Garage 交易系統 V5.1", page_icon="🏎️")
st.title("🏹 精準當沖進場檢核 (V5.1)")
st.caption("實驗目標：每日一單 (自動抓取名稱版)，嚴格執行 09:10 紀律")

# --- 1. 時間檢查 ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 側邊欄：設定 ---
st.sidebar.header("💰 交易數據輸入")
trade_type = st.sidebar.radio("操作方向", ["做多 (Long)", "做空 (Short)"])
max_cap = st.sidebar.slider("額度上限 (萬)", 30, 50, 30) * 10000

# 股號輸入
ticker_input = st.sidebar.text_input("股票代號 (例如: 2330)", value="2330")

# 初始化 Session State 用於存儲抓到的數據
if 'auto_data' not in st.session_state:
    st.session_state.auto_data = {
        "name": "待抓取", 
        "last_close": 195.0, 
        "open": 195.0, 
        "current": 200.0
    }

if st.sidebar.button("🔍 自動抓取今日數據"):
    try:
        # 台灣股市代號處理
        stock = yf.Ticker(f"{ticker_input}.TW")
        hist = stock.history(period="2d")
        if hist.empty:
            stock = yf.Ticker(f"{ticker_input}.TWO")
            hist = stock.history(period="2d")
        
        if not hist.empty:
            # 抓取股票名稱 (yf.Ticker.info 有時較慢，使用 fast_info 或自定義)
            info = stock.info
            st.session_state.auto_data["name"] = info.get('shortName', ticker_input)
            st.session_state.auto_data["last_close"] = hist['Close'].iloc[-2]
            st.session_state.auto_data["open"] = hist['Open'].iloc[-1]
            st.session_state.auto_data["current"] = hist['Close'].iloc[-1]
            st.sidebar.success(f"已更新 {st.session_state.auto_data['name']} 數據")
        else:
            st.sidebar.error("找不到該股號，請手動輸入")
    except:
        st.sidebar.error("抓取失敗，請確認網路或代號格式")

# 數據輸入區
price = st.sidebar.number_input("當前成交價", value=float(st.session_state.auto_data["current"]), step=0.5)
last_close = st.sidebar.number_input("平盤價 (昨日收盤)", value=float(st.session_state.auto_data["last_close"]), step=0.5)
open_p = st.sidebar.number_input("開盤價", value=float(st.session_state.auto_data["open"]), step=0.5)
ma_p = st.sidebar.number_input("均價線 (手動輸入)", value=price, step=0.5)

st.sidebar.markdown("---")
if trade_type == "做多 (Long)":
    stop_p = st.sidebar.number_input("預計停損價", value=price * 0.98, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 1.05, step=0.5)
else:
    stop_p = st.sidebar.number_input("預計停損價", value=price * 1.02, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 0.95, step=0.5)

# --- 3. 趨勢判定與強度計算 ---
# 顯示股票名稱
stock_display_name = st.session_state.auto_data["name"]
st.subheader(f"🌍 當前標的：{ticker_input} {stock_display_name}")
st.write(f"方向：**{trade_type}**")

open_gap_percent = ((open_p - last_close) / last_close) * 100
strength_label = "🔥 極強 (5%↑)" if open_gap_percent >= 5.0 else "💪 強 (3%↑)" if open_gap_percent >= 3.0 else "⚖️ 普通"

is_trend = (price > open_p and price > ma_p) if trade_type == "做多 (Long)" else (price < open_p and price < ma_p)
trend_label = "🟢 順勢格局" if is_trend else "🔴 逆勢操作"

st.info(f"**開盤強度：{strength_label} ({open_gap_percent:.2f}%) | 趨勢：{trend_label}**")

# --- 4. 核心準則檢核 ---
st.markdown("---")
st.subheader("🔍 進場準則最終檢核")
col3, col4 = st.columns(2)
with col3:
    m_momentum = st.selectbox("🚩 目前大盤慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])
    s_signal = st.selectbox("📈 K 棒結構觀察", ["請選擇", "高不過高 (轉弱)", "低不過低 (支撐)", "橫盤整理沒出方向 (不建議)", "無明顯訊號"])
    exhaust_text = "🚩 高點力竭" if trade_type == "做多 (Long)" else "🎯 底部力竭"
    exhaustion_signal = st.checkbox(exhaust_text)
with col4:
    key_level = st.checkbox("🔑 突破/跌破關鍵價位")
    trend_confirm = st.checkbox("⚖️ 我知曉做多/做空風險")
    plan_ok = st.checkbox("✅ 符合今日交易計畫")
    st.caption("💡 小提醒：是否符合策略以及出現訊號")

# --- 5. 綜合判斷 ---
st.markdown("---")
env_ok = all([m_momentum != "請選擇", s_signal != "請選擇"])
risk_dist = abs(price - stop_p)
rr_ratio = abs(target_p - price) / risk_dist if risk_dist > 0 else 0
side_market = (s_signal == "橫盤整理沒出方向 (不建議)")
can_enter = all([can_trade_time, env_ok, key_level, trend_confirm, plan_ok, rr_ratio >= 2.0, not exhaustion_signal, not side_market])

if can_enter:
    st.balloons()
    st.success(f"## 🟢 【准許進場 - {stock_display_name} 一張】")
else:
    st.error("## 🔴 【條件未齊 - 觀望】")

c1, c2 = st.columns(2)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("設定額度", f"{int(max_cap/10000)} 萬")
