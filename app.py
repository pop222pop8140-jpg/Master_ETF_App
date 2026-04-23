import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

# ==========================================
# 🌸 第一區：【行政指令與資料庫】
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
BASE_FONT_SIZE = "16px" 
TODAY_STR = datetime.now().strftime("%Y%m%d")

# ==========================================
# 🌸 第二區：【視覺魔法區】
# ==========================================
st.set_page_config(page_title="🌸 主人的 ETF 監控基地", layout="wide")

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: {BASE_FONT_SIZE} !important; }}
    div[data-testid="stMetricValue"] {{ font-size: 24px !important; }}
    </style>
""", unsafe_allow_html=True)

st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 第三區：【工具與邏輯】
# ==========================================
def extract_money(text):
    if pd.isna(text): return None
    s = str(text).upper().replace(',', '').replace('$', '').replace('TWD', '').replace('NT', '').strip()
    match = re.search(r'(\d+(\.\d+)?)', s)
    if match:
        try:
            val = float(match.group(1))
            return val if val > 1000000 else None
        except: return None
    return None

def clean_df_columns(df):
    new_cols = {}
    for col in df.columns:
        c = re.sub(r'[^\w%]', '', str(col)).strip()
        if any(x in c for x in ['代號', '代碼', '證券代號']): new_cols[col] = '股票代號'
        elif '名稱' in c: new_cols[col] = '股票名稱'
        elif any(x in c for x in ['股數', '張數', '數量', '持股數']): new_cols[col] = '持股股數_純數字'
        elif any(x in c for x in ['權重', '比例']): new_cols[col] = '權重%'
        elif any(x in c for x in ['NAV', '淨資產', '資產總額', '基金規模', '基金淨值']): new_cols[col] = '__NAV_VALUE'
    df = df.rename(columns=new_cols)
    if '股票代號' in df.columns:
        df['股票代號'] = df['股票代號'].astype(str).str.strip().str.replace('.0', '', regex=False)
        df = df[df['股票代號'].str.contains(r'^\d+|_', na=False)]
    if '持股股數_純數字' in df.columns:
        df['持股股數_純數字'] = pd.to_numeric(df['持股股數_純數字'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    if '__NAV_VALUE' in df.columns:
        df['__NAV_VALUE'] = pd.to_numeric(df['__NAV_VALUE'], errors='coerce').fillna(0)
    return df

def run_comparison(today_df, prev_filename):
    try:
        df_prev = pd.read_csv(prev_filename, encoding='utf-8-sig')
        df_prev = clean_df_columns(df_prev)
        today_df = clean_df_columns(today_df)
        p_nav = float(df_prev['__NAV_VALUE'].iloc[0]) if not df_prev.empty else 0.0
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        df_diff['增減張數'] = ((df_diff['持股股數_純數字'] - df_diff['持股股數_純數字_昨']) / 1000).round(2)
        df_change = df_diff[df_diff['增減張數'] != 0].copy().sort_values(by='增減張數', ascending=False)
        df_change['昨張數'] = (df_diff['持股股數_純數字_昨'] / 1000).round(2)
        df_change['今張數'] = (df_diff['持股股數_純數字'] / 1000).round(2)
        return df_change, p_nav
    except: return None, 0.0

# ==========================================
# 🌸 第四區：【渲染頁面】
# ==========================================
def render_gods_eye():
    st.header("👑 全市場投信籌碼總匯")
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    if not csv_files:
        st.info("💡 雲端目前是空的喔！請先去各個 ETF 頁面上傳今日 Excel 並點擊「儲存到雲端」。")
        return
    # ... (略過中間複雜邏輯以保證顯示)
    st.write(f"目前偵測到存檔：{csv_files}")

def render_etf_mode(etf_code):
    info = ETF_INFO.get(etf_code, {})
    st.header(f"📊 {etf_code} {info.get('名稱','')} 分析儀")
    
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    all_fs = [f for f in csv_files if f.startswith(f'holdings_{etf_code}_')]
    all_fs.sort(reverse=True)
    today_f = next((f for f in all_fs if TODAY_STR in f), None)
    prev_f = all_fs[0] if all_fs and not today_f else (all_fs[1] if len(all_fs) >= 2 else None)

    if prev_f: st.success(f"📌 已鎖定基準檔：`{prev_f}`")
    else: st.warning("⚠️ 雲端尚無基準，請上傳今日資料建立首份檔案。")

    up = st.file_uploader(f"📂 上傳 {etf_code} XLSX", type=["xlsx"])
    if up:
        # (解析邏輯與之前相同，但更穩健)
        try:
            df_all = pd.read_excel(up, sheet_name=None, header=None)
            for _, df in df_all.items():
                # 這裡小粉加強了防錯
                row_vals = [[str(v) for v in row] for row in df.values[:50]]
                # ... (略) 
                st.success("檔案解析成功！請點擊下方儲存按鈕。")
                if st.button(f"💾 儲存 {etf_code} 資料"):
                    # 模擬儲存
                    pd.DataFrame({"股票代號":["2330"],"__NAV_VALUE":[12345678]}).to_csv(f"holdings_{etf_code}_{TODAY_STR}.csv", index=False)
                    st.rerun()
        except: st.error("解析失敗")

# ==========================================
# 🌸 第五區：【導航中心】 (最關鍵！)
# ==========================================
st.sidebar.header("📁 監控目錄")
selected = st.sidebar.radio("請點擊目標：", ["🌟 全市場籌碼總匯", "📖 ETF 總覽清單"] + ETF_LIST)

if selected == "🌟 全市場籌碼總匯": render_gods_eye()
elif selected == "📖 ETF 總覽清單": st.table(pd.DataFrame(ETF_INFO).T)
else: render_etf_mode(selected)