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
# 🌸 第二區：【視覺魔法：全域 20 點字】
# ==========================================
st.set_page_config(page_title="🌸 主人的 ETF 監控基地", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="st-"], .stMarkdown, .stText, .stButton, .stSelectbox, .stRadio, .stTable, .stDataFrame, p, li, span, div {
        font-size: 20px !important;
    }
    [data-testid="stSidebar"] * { font-size: 20px !important; }
    .stDataFrame td, .stDataFrame th, [data-testid="stTable"] td, [data-testid="stTable"] th {
        font-size: 20px !important;
    }
    [data-testid="stMetricValue"] { font-size: 45px !important; font-weight: bold; }
    [data-testid="stMetricLabel"] p { font-size: 24px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 第三區：【核心邏輯：強健讀取引擎】
# ==========================================
def robust_read_file(filename):
    """🌸 小粉專屬讀取引擎：解決元大 CSV 格式不一報錯問題"""
    try:
        if filename.endswith('.csv'):
            # 預設 25 欄讀取，防止 Expected 1 fields 錯誤
            return pd.read_csv(filename, encoding='utf-8-sig', header=None, names=range(25), on_bad_lines='skip')
        else:
            return pd.read_excel(filename, header=None, names=range(25))
    except Exception as e:
        return pd.DataFrame()

def clean_df_columns(df):
    if df.empty: return df
    df = df.fillna("")
    fund_nav = 0.0
    
    # 1. 🔍 掃描檔案上方 (前 30 列) 尋找基金總資產
    for i in range(min(len(df), 30)):
        row_list = [str(x).strip() for x in df.iloc[i].values]
        for idx, val in enumerate(row_list):
            # ✨ 修正點：排除 "代號/名稱" 等干擾字，避免把 2330 當成資金！
            if any(k in val for k in ["基金資產淨值", "基金淨資產價值", "股票"]) and \
               not any(ex in val for ex in ["代號", "代碼", "名稱", "數量", "權重"]):
                try:
                    target_val = ""
                    if idx + 1 < len(row_list) and re.search(r'\d', row_list[idx+1]):
                        target_val = row_list[idx+1]
                    elif i + 1 < len(df):
                        target_val = str(df.iloc[i+1, idx])
                    
                    val_clean = re.sub(r'[^\d.]', '', target_val)
                    if val_clean: fund_nav = max(fund_nav, float(val_clean))
                except: pass

    # 2. 🕵️‍♀️ 智能標題定位
    header_idx = -1
    for i in range(min(len(df), 40)):
        row_values = [str(x).strip() for x in df.iloc[i].values]
        if any(re.search(r'代號|代碼|證券代號|商品代碼', x) for x in row_values):
            df.columns = row_values
            header_idx = i
            break
    
    if header_idx != -1:
        df = df.iloc[header_idx+1:].reset_index(drop=True)
    
    # 3. 🏷️ 欄位重新對應 (包含元大專屬名稱)
    new_cols = {}
    for col in df.columns:
        c = str(col).strip()
        c_clean = re.sub(r'[^\w%]', '', c)
        if any(x in c_clean for x in ['代號', '代碼', '證券代號', '商品代碼']): new_cols[col] = '股票代號'
        elif any(x in c_clean for x in ['名稱', '商品名稱']): new_cols[col] = '股票名稱'
        elif any(x in c_clean for x in ['股數', '張數', '數量', '持股數', '商品數量']): new_cols[col] = '持股股數_純數字'
        elif any(x in c_clean for x in ['權重', '比例', '商品權重']): new_cols[col] = '權重%'
    
    df = df.rename(columns=new_cols)
    
    if '股票代號' in df.columns:
        df['股票代號'] = df['股票代號'].astype(str).str.strip().str.replace('.0', '', regex=False)
        df = df[df['股票代號'].str.contains(r'^\d+|_|[A-Z]', na=False)]
    
    if '持股股數_純數字' in df.columns:
        df['持股股數_純數字'] = pd.to_numeric(df['持股股數_純數字'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0)
    
    if '權重%' in df.columns:
        df['權重%'] = df['權重%'].astype(str).str.replace('%', '').str.strip()

    df['__NAV_VALUE'] = fund_nav
    return df

def run_comparison(today_df, prev_filename):
    try:
        df_prev = robust_read_file(prev_filename)
        df_prev = clean_df_columns(df_prev)
        today_df = clean_df_columns(today_df)
        
        t_nav = today_df['__NAV_VALUE'].iloc[0] if not today_df.empty else 0.0
        p_nav = df_prev['__NAV_VALUE'].iloc[0] if not df_prev.empty else 0.0
        
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        df_stocks = df_diff[df_diff['股票代號'].str.contains(r'^\d+|[A-Z]', na=False)].copy()
        
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
def render_manual_upload():
    st.header("📥 手動新增持股資料 (基地增援)")
    col1, col2 = st.columns(2)
    with col1:
        selected_etf = st.selectbox("1. 選擇標的：", ETF_LIST, index=ETF_LIST.index("00990A"))
        upload_date = st.date_input("2. 選擇日期：", datetime.now())
    with col2:
        uploaded_file = st.file_uploader("3. 上傳檔案", type=["xlsx", "csv", "xls"])
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1]
        target_filename = f"holdings_{selected_etf}_{upload_date.strftime('%Y%m%d')}.{file_ext}"
        with open(target_filename, "wb") as f: f.write(uploaded_file.getbuffer())
        st.success(f"✨ 成功入庫：`{target_filename}`"); st.balloons()

def render_gods_eye():
    st.header("👑 全市場投信籌碼總匯")
    all_files = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and not f.startswith('~$')]
    if not all_files: return st.info("💡 雲端目前是空的喔！")
    all_changes = []
    for etf_code in ETF_LIST:
        fs = [f for f in all_files if f.startswith(f'holdings_{etf_code}_')]; fs.sort(reverse=True)
        today_f = next((f for f in fs if TODAY_STR in f), (fs[0] if fs else None))
        prev_f = next((f for f in fs if f != today_f), None)
        if today_f and prev_f:
            try:
                df_today = robust_read_file(today_f); df_change, _, _ = run_comparison(df_today, prev_f)
                if df_change is not None and not df_change.empty: all_changes.append(df_change[['股票代號', '股票名稱', '增減張數']])
            except: pass
    if all_changes:
        master_df = pd.concat(all_changes, ignore_index=True); summary_df = master_df.groupby(['股票代號', '股票名稱'], as_index=False)['增減張數'].sum()
        top_buys = summary_df[summary_df['增減張數'] > 0].sort_values(by='增減張數', ascending=False)
        top_sells = summary_df[summary_df['增減張數'] < 0].sort_values(by='增減張數', ascending=True)
        c1, c2 = st.columns(2)
        with c1: st.subheader("🚀 買超排行"); st.dataframe(top_buys, use_container_width=True, hide_index=True)
        with c2: st.subheader("📉 賣超排行"); st.dataframe(top_sells, use_container_width=True, hide_index=True)

def render_etf_mode(etf_code):
    info = ETF_INFO.get(etf_code, {}); st.header(f"📊 {etf_code} {info.get('名稱','')} 分析儀")
    all_fs = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and f.startswith(f'holdings_{etf_code}_')]; all_fs.sort(reverse=True)
    today_f = next((f for f in all_fs if TODAY_STR in f), (all_fs[0] if all_fs else None))
    prev_f = next((f for f in all_fs if f != today_f), None)
    if today_f:
        try:
            df_full = robust_read_file(today_f); df_full = clean_df_columns(df_full)
            if prev_f:
                df_change, t_nav, p_nav = run_comparison(df_full, prev_f)
                st.subheader("💰 基金總資產資金水位監控")
                c1, c2, c3 = st.columns(3)
                # ✨ 如果偵測到 0 元，顯示友善提示
                st_t_nav = f"{t_nav:,.0f} 元" if t_nav > 0 else "資料未包含總額"
                st_p_nav = f"{p_nav:,.0f} 元" if p_nav > 0 else "資料未包含總額"
                with c1: st.metric("今日總資金", st_t_nav)
                with c2: st.metric("近期總資金", st_p_nav)
                with c3:
                    if t_nav > 0 and p_nav > 0:
                        st.metric("資金增減", f"{(t_nav - p_nav):,.0f} 元", delta=(t_nav - p_nav))
                    else: st.metric("資金增減", "--")
                if df_change is not None:
                    st.subheader("🔥 今日動開獎")
                    st.dataframe(df_change[['股票代號', '股票名稱', '昨張數', '今張數', '增減張數', '權重%']], use_container_width=True, hide_index=True)
            st.subheader(f"📋 持股明細 ({today_f})")
            display_cols = [c for c in ['股票代號', '股票名稱', '持股股數_純數字', '權重%'] if c in df_full.columns]
            st.dataframe(df_full[display_cols], use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"🌸 小粉報告：錯誤：{e}")
    else: st.warning("⚠️ 尚無資料。")

# ==========================================
# 🌸 第五區：【導航中心】
# ==========================================
st.sidebar.header("📁 監控目錄")
selected = st.sidebar.radio("請點擊目標：", ["🌟 全市場籌碼總匯", "📖 ETF 總覽清單", "📥 手動新增資料"] + ETF_LIST)
if selected == "🌟 全市場籌碼總匯": render_gods_eye()
elif selected == "📖 ETF 總覽清單": st.table(pd.DataFrame(ETF_INFO).T)
elif selected == "📥 手動新增資料": render_manual_upload()
else: render_etf_mode(selected)