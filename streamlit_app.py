import streamlit as st

# 設定網頁標題與圖標
st.set_page_config(page_title="Annex Garage Trading Monitor", page_icon="📈")

st.title("📊 當沖進場條件檢核器")
st.caption("專為 150-399 TWD 高周轉標的設計")

# --- 左側輸入區 ---
st.sidebar.header("🎯 盤中即時數據")
ticker = st.sidebar.text_input("股票代碼", value="2330")
price = st.sidebar.number_input("當前股價 (TWD)", min_value=0.0, value=250.0, step=0.5)
open_p = st.sidebar.number_input("今日開盤價", min_value=0.0, value=245.0)
ma_p = st.sidebar.number_input("均線價格 (5分K)", min_value=0.0, value=248.0)
vol_ratio = st.sidebar.slider("預估量比 (昨日=1.0)", 0.0, 5.0, 1.2)

st.sidebar.markdown("---")
st.sidebar.header("🛡️ 風險控管設定")
stop_p = st.sidebar.number_input("停損撤退價", min_value=0.0, value=244.0)
target_p = st.sidebar.number_input("預期獲利價", min_value=0.0, value=265.0)
fomo = st.sidebar.checkbox("我現在心態很急 (FOMO)")

# --- 核心邏輯計算 ---
max_cap = 300000
risk = price - stop_p
reward = target_p - price
rr_ratio = reward / risk if risk > 0 else 0
# 計算建議股數 (考慮手續費 0.1425%)
suggested_shares = int(max_cap // (price * 1.001425))

# --- 中間結果顯示 ---
st.header(f"檢測標的：{ticker}")

# 建立五個檢查燈號
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("建議最大買進", f"{suggested_shares} 股", f"{suggested_shares//1000} 張")
with col2:
    st.metric("損益比 (R/R)", f"{rr_ratio:.2f}", delta="及格" if rr_ratio >= 2 else "不及格", delta_color="normal" if rr_ratio >= 2 else "inverse")
with col3:
    st.metric("交易額度", "30 萬", "固定上限")

st.markdown("---")

# 條件列表
checks = {
    "價格區間 (150-399)": 150 <= price <= 399,
    "趨勢向上 (價 > 開)": price > open_p,
    "均線支撐 (價 > 均)": price > ma_p,
    "量能充足 (量比 >= 1)": vol_ratio >= 1.0,
    "心理防線 (非 FOMO)": not fomo,
    "損益比 > 2.0": rr_ratio >= 2.0
}

for label, passed in checks.items():
    if passed:
        st.success(f"✅ {label}")
    else:
        st.error(f"❌ {label}")

# --- 最終決策 ---
st.markdown("---")
if all(checks.values()):
    st.balloons()
    st.markdown("## 🟢 準則全數成立：請執行交易！")
    st.warning(f"提醒：請嚴格執行 {stop_p} 停損，不要攤平。")
else:
    st.markdown("## 🔴 條件未齊：保持空手觀望。")
