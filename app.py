import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

# ==========================================
# 🌸 第一區：【完整資料庫】
# ==========================================
ETF_INFO = {
    "00981A": {"名稱": "主動統一台股增", "成立日期": "2025/05/27", "殖利率": "1.52%", "配息": "季配"},
    "00992A": {"名稱": "主動群益科技創", "成立日期": "2025/12/30", "殖利率": "-", "配息": "季配"},
    "00982A": {"名稱": "主動群益台灣強", "成立日期": "2025/05/22", "殖利率": "4.53%", "配息": "季配"},
    "00991A": {"名稱": "主動復華未來50", "成立日期": "2025/12/10", "殖利率": "-", "配息": "半年配"},
    "00990A": {"名稱": "主動元大AI高股", "成立日期": "2025/12/22", "殖利率": "-", "配息": "不配息"},
    "00988A": {"名稱": "主動統一全球創", "成立日期": "2025/11/05", "殖利率": "-", "配息": "年配"},
    "00400A": {"名稱": "主動國泰動能高", "成立日期": "2026/04/09", "殖利率": "-", "配息": "月配"},
    "00980A": {"名稱": "主動野村臺灣優", "成立日期": "2025/05/05", "殖利率": "3.26%", "配息": "季配"},
    "00985A": {"名稱": "主動野村台灣50", "成立日期": "2025/07/21", "殖利率": "-", "配息": "年配"},
    "009B1D": {"名稱": "主動中信非投等", "成立日期": "2025/09/15", "殖利率": "3.77%", "配息": "月配"},
    "00984A": {"名稱": "主動安聯台灣高", "成立日期": "2025/07/14", "殖利率": "4.54%", "配息": "季配"},
    "00980D": {"名稱": "主動野村傳投高", "成立日期": "2025/08/04", "殖利率": "3.90%", "配息": "月配"},
    "00982D": {"名稱": "主動富邦動能入", "成立日期": "2025/10/14", "殖利率": "2.08%", "配息": "月配"},
}

ETF_LIST = list(ETF_INFO.keys())
TODAY_STR = datetime.now().strftime("%Y%m%d")

# ==========================================
# 🌸 第二區：【視覺魔法：全域 20 點字設定】
# ==========================================
st.set_page_config(page_title="🌸 主人的 ETF 監控基地", layout="wide")

st.markdown("""
    <style>
    /* 全域字體大小設定 */
    html, body, [class*="st-"], .stMarkdown, .stText, .stButton, .stSelectbox, .stRadio, .stTable, .stDataFrame, p, li, span {
        font-size: 20px !important;
    }
    /* 側邊欄專屬字體 */
    [data-testid="stSidebar"] * {
        font-size: 20px !important;
    }
    /* 表格內部字體 */
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        font-size: 20px !important;
    }
    /* 指標數字大小 */
    [data-testid="stMetricValue"] {
        font-size: 40px !important;
        font-weight: bold;
    }
    .capital-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff69b4;
        margin-bottom: 20px;
    }
    .metric-label { font-size: 20px; color: #666; }
    .delta-plus { color: #28a745; font-size: 20px; }
    .delta-minus { color: #dc3545; font-size: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 第三區：【核心邏輯】
# ==========================================
def clean_df_columns(df):
    new_cols = {}
    for col in df.columns:
        c = re.sub(r'[^\w%]', '', str(col)).strip()
        if any(x in c for x in ['代號', '代碼', '證券代號']): new_cols[col] = '股票代號'
        elif '名稱' in c: new_cols[col] = '股票名稱'
        elif any(x in c for x in ['股數', '張數', '數量', '持股數']): new_cols[col] = '持股股數_純數字'
        elif any(x in c for x in ['權重', '比例']): new_cols[col] = '權重%'
        elif any(x in c for x in ['NAV', '淨資產', '基金規模']): new_cols[col] = '__NAV_VALUE'
    
    df = df.rename(columns=new_cols)
    if '股票代號' in df.columns:
        df['股票代號'] = df['股票代號'].astype(str).str.strip().str.replace('.0', '', regex=False)
        df = df[df['股票代號'].str.contains(r'^\d+|_', na=False)]
    if '持股股數_純數字' in df.columns:
        df['持股股數_純數字'] = pd.to_numeric(df['持股股數_純數字'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    if '__NAV_VALUE' in df.columns:
        nav_series = pd.to_numeric(df['__NAV_VALUE'], errors='coerce').fillna(0)
        df['__NAV_VALUE'] = nav_series.max()
    return df

def run_comparison(today_df, prev_filename):
    try:
        df_prev = pd.read_csv(prev_filename, encoding='utf-8-sig') if prev_filename.endswith('.csv') else pd.read_excel(prev_filename)
        df_prev = clean_df_columns(df_prev)
        today_df = clean_df_columns(today_df)
        
        t_nav = today_df['__NAV_VALUE'].iloc[0] if not today_df.empty and '__NAV_VALUE' in today_df.columns else 0.0
        p_nav = df_prev['__NAV_VALUE'].iloc[0] if not df_prev.empty and '__NAV_VALUE' in df_prev.columns else 0.0
        
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        df_stocks = df_diff[df_diff['股票代號'].str.match(r'^\d+$', na=False)].copy()
        
        df_stocks['昨張數'] = (df_stocks['持股股數_純數字_昨'] / 1000).round(2)
        df_stocks['今張數'] = (df_stocks['持股股數_純數字'] / 1000).round(2)
        df_stocks['增減張數'] = (df_stocks['今張數'] - df_stocks['昨張數']).round(2)
        
        df_change = df_stocks[df_stocks['增減張數'] != 0].sort_values(by='增減張數', ascending=False)
        return df_change, t_nav, p_nav
    except Exception as e:
        return None, 0.0, 0.0

# ==========================================
# 🌸 第四區：【渲染頁面】
# ==========================================

# --- 📥 新增功能：手動上傳區 ---
def render_manual_upload():
    st.header("📥 手動新增持股資料 (基地增援)")
    st.write("如果小蜜蜂採集失敗，主人可以在這裡手動餵食 Excel 或 CSV 檔案喔！✨")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_etf = st.selectbox("1. 選擇要存入的 ETF 標的：", ETF_LIST, index=ETF_LIST.index("00400A"))
        upload_date = st.date_input("2. 選擇這份資料的日期：", datetime.now())
    
    with col2:
        uploaded_file = st.file_uploader("3. 請選擇 Excel 或 CSV 檔案", type=["xlsx", "csv", "xls"])
    
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1]
        date_str = upload_date.strftime("%Y%m%d")
        target_filename = f"holdings_{selected_etf}_{date_str}.{file_ext}"
        
        with open(target_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✨ 報告主人！資料已成功入庫：`{target_filename}`")
        st.balloons()
        st.info("💡 溫馨提醒：上傳成功後，請點擊左側對應的 ETF 編號即可看到最新數據喔！")

def render_gods_eye():
    st.header("👑 全市場投信籌碼總匯")
    all_files = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and not f.startswith('~$')]
    if not all_files:
        st.info("💡 雲端目前是空的喔！請等待小管家自動採集或手動上傳。")
        return
    st.write(f"✅ 系統運作中，目前偵測到 {len(all_files)} 份持股檔案。")
    st.markdown("---")
    
    all_changes = []
    for etf_code in ETF_LIST:
        fs = [f for f in all_files if f.startswith(f'holdings_{etf_code}_')]
        fs.sort(reverse=True)
        today_f = next((f for f in fs if TODAY_STR in f), (fs[0] if fs else None))
        prev_f = next((f for f in fs if f != today_f), None)
        if today_f and prev_f:
            try:
                df_today = pd.read_csv(today_f) if today_f.endswith('.csv') else pd.read_excel(today_f)
                df_change, _, _ = run_comparison(df_today, prev_f)
                if df_change is not None and not df_change.empty:
                    all_changes.append(df_change[['股票代號', '股票名稱', '增減張數']])
            except: pass
                
    if all_changes:
        master_df = pd.concat(all_changes, ignore_index=True)
        summary_df = master_df.groupby(['股票代號', '股票名稱'], as_index=False)['增減張數'].sum()
        summary_df = summary_df[summary_df['增減張數'] != 0]
        top_buys = summary_df[summary_df['增減張數'] > 0].sort_values(by='增減張數', ascending=False)
        top_sells = summary_df[summary_df['增減張數'] < 0].sort_values(by='增減張數', ascending=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚀 今日主動 ETF 買超總排行")
            st.dataframe(top_buys, use_container_width=True, hide_index=True)
        with col2:
            st.subheader("📉 今日主動 ETF 賣超總排行")
            st.dataframe(top_sells, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 目前雲端各 ETF 的檔案數量不足以計算全市場變動。")

def render_etf_mode(etf_code):
    info = ETF_INFO.get(etf_code, {})
    st.header(f"📊 {etf_code} {info.get('名稱','')} 分析儀")
    all_fs = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and f.startswith(f'holdings_{etf_code}_') and not f.startswith('~$')]
    all_fs.sort(reverse=True)
    today_f = next((f for f in all_fs if TODAY_STR in f), (all_fs[0] if all_fs else None))
    prev_f = next((f for f in all_fs if f != today_f), None)

    if today_f and prev_f:
        try:
            df_today = pd.read_csv(today_f) if today_f.endswith('.csv') else pd.read_excel(today_f)
            df_today = clean_df_columns(df_today)
            df_change, t_nav, p_nav = run_comparison(df_today, prev_f)
            
            st.subheader("💰 基金總資產資金水位監控")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("今日總資金", f"{t_nav:,.0f} 元")
            with c2: st.metric("近期總資金", f"{p_nav:,.0f} 元")
            with c3:
                delta = t_nav - p_nav
                st.metric("資金水位增減", f"{delta:,.0f} 元", delta_color="normal", delta=f"{delta:,.0f}")
            st.markdown("---")
            if df_change is not None:
                st.subheader("🔥 今日動開獎")
                st.dataframe(df_change[['股票代號', '股票名稱', '昨張數', '今張數', '增減張數', '權重%']], use_container_width=True)
        except Exception as e:
            st.error(f"解析發生錯誤：{e}")
    else:
        st.warning("⚠️ 雲端尚無足夠檔案進行比對。")

    if today_f:
        st.subheader(f"📋 目前完整持股明細 ({today_f})")
        df_full = pd.read_csv(today_f) if today_f.endswith('.csv') else pd.read_excel(today_f)
        df_full = clean_df_columns(df_full)
        st.dataframe(df_full[['股票代號', '股票名稱', '持股股數_純數字', '權重%']], use_container_width=True)

# ==========================================
# 🌸 第五區：【導航中心】
# ==========================================
st.sidebar.header("📁 監控目錄")
selected = st.sidebar.radio("請點擊目標：", ["🌟 全市場籌碼總匯", "📖 ETF 總覽清單", "📥 手動新增資料"] + ETF_LIST)

if selected == "🌟 全市場籌碼總匯": render_gods_eye()
elif selected == "📖 ETF 總覽清單": st.table(pd.DataFrame(ETF_INFO).T)
elif selected == "📥 手動新增資料": render_manual_upload()
else: render_etf_mode(selected)