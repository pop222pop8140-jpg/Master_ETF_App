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
    /* 讓現金顯示得更漂亮 */
    .stDataFrame td {{ color: #FF69B4; }} 
    </style>
""", unsafe_allow_html=True)

st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 第三區：【工具與邏輯】
# ==========================================
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
        # ✨ 關鍵修改：允許數字開頭或底線開頭（例如 _CASH）
        df = df[df['股票代號'].str.contains(r'^\d+|_', na=False)]
        
    if '持股股數_純數字' in df.columns:
        df['持股股數_純數字'] = pd.to_numeric(df['持股股數_純數字'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    if '__NAV_VALUE' in df.columns:
        # 如果整欄有數值，取第一個非零值作為基準
        nav_series = pd.to_numeric(df['__NAV_VALUE'], errors='coerce').fillna(0)
        df['__NAV_VALUE'] = nav_series.max()
        
    return df

def run_comparison(today_df, prev_filename):
    try:
        # 判斷基準檔格式
        if prev_filename.endswith('.csv'):
            df_prev = pd.read_csv(prev_filename, encoding='utf-8-sig')
        else:
            df_prev = pd.read_excel(prev_filename)
            
        df_prev = clean_df_columns(df_prev)
        today_df = clean_df_columns(today_df)
        
        p_nav = float(df_prev['__NAV_VALUE'].iloc[0]) if not df_prev.empty else 0.0
        
        # 合併比對
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        
        # 只有股票（純數字代號）才算張數，現金類直接比金額
        df_diff['增減張數'] = df_diff.apply(
            lambda x: round((x['持股股數_純數字'] - x['持股股數_純數字_昨']) / 1000, 2) if not str(x['股票代號']).startswith('_') else round(x['持股股數_純數字'] - x['持股股數_純數字_昨'], 0),
            axis=1
        )
        
        df_change = df_diff[df_diff['增減張數'] != 0].copy().sort_values(by='增減張數', ascending=False)
        return df_change, p_nav
    except Exception as e:
        st.error(f"比對失敗：{e}")
        return None, 0.0

# ==========================================
# 🌸 第四區：【渲染頁面】
# ==========================================
def render_gods_eye():
    st.header("👑 全市場投信籌碼總匯")
    # 掃描 csv 和 xlsx
    all_files = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and not f.startswith('~$')]
    if not all_files:
        st.info("💡 雲端目前是空的喔！")
        return
    st.write(f"✅ 目前偵測到系統內共有 {len(all_files)} 份持股檔案")
    st.caption("小粉提示：自動採集的 CSV 與手動上傳的 XLSX 都能識別囉！")

def render_etf_mode(etf_code):
    info = ETF_INFO.get(etf_code, {})
    st.header(f"📊 {etf_code} {info.get('名稱','')} 分析儀")
    
    # ✨ 關鍵修改：同時搜尋 CSV 和 XLSX
    all_fs = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) 
              and f.startswith(f'holdings_{etf_code}_') and not f.startswith('~$')]
    all_fs.sort(reverse=True)
    
    today_f = next((f for f in all_fs if TODAY_STR in f), None)
    # 抓取「非今日」的最新的那一份當基準
    prev_f = None
    if today_f:
        other_fs = [f for f in all_fs if f != today_f]
        if other_fs: prev_f = other_fs[0]
    elif all_fs:
        prev_f = all_fs[0]

    if prev_f: st.success(f"📌 已鎖定基準檔：`{prev_f}`")
    else: st.warning("⚠️ 雲端尚無基準，請執行 Actions 採集或手動上傳。")

    # ✨ 關鍵修改：uploader 支援 csv
    up = st.file_uploader(f"📂 手動補傳 {etf_code} 資料 (支援 XLSX / CSV)", type=["xlsx", "csv"])
    
    if up:
        try:
            if up.name.endswith('.csv'):
                df_target = pd.read_csv(up, encoding='utf-8-sig')
            else:
                # 簡單處理 Excel
                df_target = pd.read_excel(up)
            
            df_cleaned = clean_df_columns(df_target)
            st.dataframe(df_cleaned.head(10))
            
            if st.button(f"💾 儲存 {etf_code} 覆蓋雲端"):
                # 統一存成 CSV
                df_cleaned.to_csv(f"holdings_{etf_code}_{TODAY_STR}.csv", index=False, encoding='utf-8-sig')
                st.success("儲存成功！")
                st.rerun()
        except Exception as e:
            st.error(f"解析失敗：{e}")

    # 比對與顯示邏輯
    if today_f and prev_f:
        df_today = pd.read_csv(today_f) if today_f.endswith('.csv') else pd.read_excel(today_f)
        df_change, p_nav = run_comparison(df_today, prev_f)
        if df_change is not None:
            st.subheader("🚀 今日籌碼變動排行")
            st.dataframe(df_change[['股票代號', '股票名稱', '增減張數', '權重%']])

# ==========================================
# 🌸 第五區：【導航中心】
# ==========================================
st.sidebar.header("📁 監控目錄")
selected = st.sidebar.radio("請點擊目標：", ["🌟 全市場籌碼總匯", "📖 ETF 總覽清單"] + ETF_LIST)

if selected == "🌟 全市場籌碼總匯": render_gods_eye()
elif selected == "📖 ETF 總覽清單": st.table(pd.DataFrame(ETF_INFO).T)
else: render_etf_mode(selected)