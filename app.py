import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

# ==========================================
# 🌸 行政指令區
# ==========================================
ETF_INFO = {
    "00981A": {"名稱": "主動統一台股增", "成立日期": "2025/05/27", "殖利率": "1.52%", "配息": "季配"},
    "00988A": {"名稱": "主動統一全球創", "成立日期": "2025/11/05", "殖利率": "-", "配息": "年配"},
    "00992A": {"名稱": "主動群益科技創", "成立日期": "2025/12/30", "殖利率": "-", "配息": "季配"},
    "00982A": {"名稱": "主動群益台灣強", "成立日期": "2025/05/22", "殖利率": "4.53%", "配息": "季配"},
}
ETF_LIST = list(ETF_INFO.keys())
TODAY_STR = datetime.now().strftime("%Y%m%d")

st.set_page_config(page_title="🌸 主人的 ETF 監控基地", layout="wide")
st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 核心邏輯區
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
        
        p_nav = float(df_prev['__NAV_VALUE'].iloc[0]) if not df_prev.empty else 0.0
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        
        # ✨ 優化：區分股票(張)與資本(百萬元)
        def calc_change(row):
            diff = row['持股股數_純數字'] - row['持股股數_純數字_昨']
            if str(row['股票代號']).startswith('_'):
                return round(diff / 1000000, 2) # 資本類轉成百萬元
            else:
                return round(diff / 1000, 2) # 股票類轉成張
        
        df_diff['變動量'] = df_diff.apply(calc_change, axis=1)
        df_diff['單位'] = df_diff['股票代號'].apply(lambda x: '百萬元' if str(x).startswith('_') else '張')
        
        df_change = df_diff[df_diff['變動量'] != 0].copy().sort_values(by='變動量', ascending=False)
        return df_change, p_nav
    except Exception as e:
        st.error(f"比對失敗：{e}")
        return None, 0.0

# ==========================================
# 🌸 渲染頁面
# ==========================================
def render_gods_eye():
    st.header("👑 全市場投信籌碼總匯")
    all_files = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and not f.startswith('~$')]
    st.write(f"✅ 目前偵測到系統內共有 {len(all_files)} 份持股檔案")
    if all_files: st.info(f"最新存檔列表：{sorted(all_files, reverse=True)[:5]}")

def render_etf_mode(etf_code):
    info = ETF_INFO.get(etf_code, {})
    st.header(f"📊 {etf_code} {info.get('名稱','')} 分析儀")
    
    all_fs = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and f.startswith(f'holdings_{etf_code}_') and not f.startswith('~$')]
    all_fs.sort(reverse=True)
    
    today_f = next((f for f in all_fs if TODAY_STR in f), (all_fs[0] if all_fs else None))
    prev_f = next((f for f in all_fs if f != today_f), None)

    if prev_f: st.success(f"📌 基準檔：`{prev_f}` | 今日檔：`{today_f}`")
    else: st.warning("⚠️ 雲端尚無足夠檔案進行比對（至少需要兩份不同日期的檔案）。")

    # 顯示比對結果
    if today_f:
        df_today = pd.read_csv(today_f) if today_f.endswith('.csv') else pd.read_excel(today_f)
        df_today = clean_df_columns(df_today)
        
        if prev_f:
            df_change, _ = run_comparison(df_today, prev_f)
            if df_change is not None:
                st.subheader("🚀 今日籌碼變動排行")
                # ✨ 使用 Streamlit 新版表格格式化
                st.dataframe(
                    df_change[['股票代號', '股票名稱', '變動量', '單位', '權重%']],
                    column_config={
                        "變動量": st.column_config.NumberColumn("增減幅度", format="%.2f"),
                        "權重%": st.column_config.NumberColumn("目前權重", format="%.2f%%")
                    },
                    use_container_width=True
                )
        
        st.subheader(f"📋 目前完整持股清單 ({today_f})")
        st.dataframe(df_today[['股票代號', '股票名稱', '持股股數_純數字', '權重%']], use_container_width=True)

# ==========================================
# 🌸 導航中心
# ==========================================
st.sidebar.header("📁 監控目錄")
selected = st.sidebar.radio("請點擊目標：", ["🌟 全市場籌碼總匯"] + ETF_LIST)

if selected == "🌟 全市場籌碼總匯": render_gods_eye()
else: render_etf_mode(selected)