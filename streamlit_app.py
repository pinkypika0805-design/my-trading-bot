import streamlit as st
from datetime import datetime
import pytz
import yfinance as yf

st.set_page_config(page_title="Annex Garage 交易系統 V5.3", page_icon="🏎️")
st.title("🏹 精準當沖進場檢核 (V5.3)")
st.caption("實驗目標：每日一單 (中文顯示強化版)，嚴格執行 09:10 紀律")

# --- 1. 時間檢查 ---
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)

# --- 2. 側邊欄：設定 ---
st.sidebar.header("💰 交易數據輸入")
trade_type = st.sidebar.radio("操作方向", ["做多 (Long)", "做空 (Short)"])
max_cap = st.sidebar.slider("額度上限 (萬)", 30, 50, 30) * 10000

ticker_input = st.sidebar.text_input("股票代號 (例如: 2330)", value="2330")

if 'auto_data' not in st.session_state:
    st.session_state.auto_data = {"name": "待抓取", "last_close": 195.0, "open": 195.0, "current": 200.0}

if st.sidebar.button("🔍 自動抓取今日數據"):
    try:
        # 嘗試上市與上櫃代號
        stock = yf.Ticker(f"{ticker_input}.TW")
        hist = stock.history(period="2d")
        if hist.empty:
            stock = yf.Ticker(f"{ticker_input}.TWO")
            hist = stock.history(period="2d")
        
        if not hist.empty:
            info = stock.info
            # 強化中文抓取邏輯：優先找 info 中的中文特徵
            # 有些台股的中文名稱會藏在 'longName' 或 'shortName'
            raw_name = info.get('longName') or info.get('shortName') or ticker_input
            
            # 建立常用熱門股手動對照表 (確保你常做的標的一定有中文)
            common_dict = {
                "Taiwan Semiconductor Manufacturing Company Limited": "台積電",
                "Hon Hai Precision Industry Co., Ltd.": "鴻海",
                "MediaTek Inc.": "聯發科",
                "Quanta Computer Inc.": "廣達",
                "Wiwynn Corporation": "緯穎",
                "Alchip Technologies, Ltd.": "世芯-KY",
                "Giga-Byte Technology Co., Ltd.": "技嘉"
            }
            final_name = common_dict.get(raw_name, raw_name)
            
            # 如果還是英文名，嘗試縮短它 (移除 Co., Ltd. 等)
            if any(c.isalpha() for c in final_name) and len(final_name) > 10:
                final_name = final_name.split(' ') # 只取第一個單字作為代稱
            
            st.session_state.auto_data["name"] = final_name
            st.session_state.auto_data["last_close"] = hist['Close'].iloc[-2]
            st.session_state.auto_data["open"] = hist['Open'].iloc[-1]
            st.session_state.auto_data["current"] = hist['Close'].iloc[-1]
            st.sidebar.success(f"✅ 已抓取數據")
        else:
            st.sidebar.error("找不到該股號")
    except:
        st.sidebar.error("抓取失敗")

# 左側顯示名稱
st.sidebar.markdown(f"### 🎯 {st.session_state.auto_data['name']}")

# 數據輸入區
price = st.sidebar.number_input("當前成交價", value=float(st.session_state.auto_data["current"]), step=0.5)
last_close = st.sidebar.number_input("平盤價 (昨收)", value=float(st.session_state.auto_data["last_close"]), step=0.5)
open_p = st.sidebar.number_input("開盤價", value=float(st.session_state.auto_data["open"]), step=0.5)
ma_p = st.sidebar.number_input("均價線", value=price, step=0.5)

st.sidebar.markdown("---")
# 自動計算停損獲利
if trade_type == "做多 (Long)":
    stop_p = st.sidebar.number_input("預計停損價", value=price * 0.98, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 1.05, step=0.5)
else:
    stop_p = st.sidebar.number_input("預計停損價", value=price * 1.02, step=0.5)
    target_p = st.sidebar.number_input("預期獲利點", value=price * 0.95, step=0.5)

# --- 3. 趨勢判定 ---
stock_name = st.session_state.auto_data["name"]
st.subheader(f"🌍 當前標的：{ticker_input} {stock_name}")

open_gap = ((open_p - last_close) / last_close) * 100
strength = "🔥 極強 (5%↑)" if open_gap >= 5.0 else "💪 強 (3%↑)" if open_gap >= 3.0 else "⚖️ 普通"
is_trend = (price > open_p and price > ma_p) if trade_type == "做多 (Long)" else (price < open_p and price < ma_p)
st.info(f"**開盤強度：{strength} ({open_gap:.2f}%) | 趨勢：{'🟢 順勢' if is_trend else '🔴 逆勢'}**")

# --- 4. 進場準則檢核 ---
st.markdown("---")
st.subheader("🔍 進場準則最終檢核")
c3, c4 = st.columns(2)
with c3:
    m_momentum = st.selectbox("🚩 目前大盤慣性", ["請選擇", "正在拉抬 🚀", "正在下殺 📉", "止跌跡象 🛡️", "止漲跡象 ⚠️", "橫盤震盪 ☁️"])
    s_signal = st.selectbox("📈 K 棒結構觀察", ["請選擇", "高不過高 (轉弱)", "低不過低 (支撐)", "橫盤整理沒出方向 (不建議)", "無明顯訊號"])
    exhaust_check = st.checkbox("🚩 高點力竭" if trade_type == "做多 (Long)" else "🎯 底部力竭")
with c4:
    key_level = st.checkbox("🔑 突破/跌破關鍵價位")
    risk_confirm = st.checkbox("⚖️ 我知曉做多/做空風險")
    plan_ok = st.checkbox("✅ 符合今日交易計畫")
    st.caption("💡 小提醒：是否符合策略以及出現訊號")

# --- 5. 綜合判斷 ---
st.markdown("---")
env_ok = all([m_momentum != "請選擇", s_signal != "請選擇"])
risk_dist = abs(price - stop_p)
rr_ratio = abs(target_p - price) / risk_dist if risk_dist > 0 else 0
side_market = (s_signal == "橫盤整理沒出方向 (不建議)")
can_enter = all([can_trade_time, env_ok, key_level, risk_confirm, plan_ok, rr_ratio >= 2.0, not exhaust_check, not side_market])

if can_enter:
    st.balloons()
    st.success(f"## 🟢 【准許進場 - {stock_name} 一張】")
else:
    st.error("## 🔴 【條件未齊 - 觀望】")

c1, c2 = st.columns(2)
c1.metric("損益比 (R/R)", f"{rr_ratio:.2f}")
c2.metric("設定額度", f"{int(max_cap/10000)} 萬")
