import streamlit as st
from datetime import datetime
import pytz

# 設定網頁標題
st.set_page_config(page_title="Annex Garage 交易系統 V2", page_icon="📈")
st.title("🏹 精準當沖進場檢核 (V2)")
st.caption("實驗目標：每日一單，嚴格遵守 9:10 後進場紀律")

# --- 1. 時間檢查 (自動判斷是否超過 9:10) ---
# 設定台灣時區
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)
current_time_str = now_tw.strftime("%H:%M")
# 判斷是否已經 9:10 之後 (且在收盤前)
can_trade_time = now_tw.hour > 9 or (now_tw.hour == 9 and now_tw.minute >= 10)
market_closed = now_tw.hour >= 14 # 簡單判斷台股收盤

# --- 2. 左側數據輸入 ---
st.sidebar.header("📊 盤中實況數據")
ticker = st.sidebar.text_input("股票代號", value="2330")
price = st.sidebar.number_input("當前成交價", value=200.0, step=0.5)
stop_p = st.sidebar.number_input("預計停損價", value=198.0, step=0.5)
target_p = st.sidebar.number_input("預期獲利點", value=210.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("🌍 市場環境")
market_state = st.sidebar.radio("大盤/櫃買開盤狀態", ["開高", "開平", "開低"])
stock_open_pos = st.sidebar.radio("個股開盤位置", ["開高 (跳空)", "開平", "開低"])
direction = st.sidebar.radio("開盤後出方向", ["往上衝", "往下殺", "橫盤震盪"])

# --- 3. 核心檢查邏輯 ---
st.subheader("🔍 進場條件驗證")

# A. 時間限制 (自動檢查)
if can_trade_time:
    st.success(f"✅ 時間檢核：目前 {current_time_str}，已過 9:10 (符合進場時間)")
    time_ok = True
else:
    st.error(f"❌ 時間檢核：目前 {current_time_str}，未到 9:10 (請耐心等待，禁動手)")
    time_ok = False

# B. 手動勾選檢查
st.write("### 關鍵動作確認：")
key_level = st.checkbox("關鍵價位：是否已【突破】或【跌破】關鍵壓力/支撐？")
plan_ok = st.checkbox("計畫執行：這筆單符合「大盤方向」與「個股方向」的一致性？")

# C. 損益比計算
risk = price - stop_p
reward = target_p - price
rr_ratio = reward / risk if risk > 0 else 0
rr_ok = rr_ratio >= 2.0

# --- 4. 綜合判斷結果 ---
st.markdown("---")

# 總結所有條件
final_check = all([time_ok, key_level, plan_ok, rr_ok])

if final_check:
    st.balloons()
    st.markdown("## 🟢 【准許進場】")
    st.info(f"大盤{market_state} / 個股{stock_open_pos} / 方向{direction}")
    st.warning(f"建議：嚴格執行 {stop_p} 停損，不加碼、不攤平。")
else:
    st.markdown("## 🔴 【條件未齊 - 觀望】")
    if not rr_ok:
        st.write(f"⚠️ 損益比不足：目前僅 {rr_ratio:.2f} (目標需 > 2.0)")
    if not key_level:
        st.write("⚠️ 尚未突破或跌破關鍵價位")

# --- 5. 數據小卡 ---
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("當前損益比", f"{rr_ratio:.2f}")
c2.metric("最大風控額", "30 萬")
shares = int(300000 // (price * 1.001425))
c3.metric("建議股數", f"{shares}")

st.caption(f"數據最後更新時間：{current_time_str}")
