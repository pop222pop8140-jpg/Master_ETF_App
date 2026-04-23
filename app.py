import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import random
import altair as alt

# ==========================================
# 🌸 第一區：【行政指令與資料庫】(小粉的萬物寶典)
# ==========================================
# 根據主人的 APP 截圖，小粉完美建檔的 ETF 總資料庫！
ETF_INFO = {
    "00981A": {"名稱": "主動統一台股增", "成立日期": "2025/05/27", "殖利率": "1.52%", "配息": "季配"},
    "00992A": {"名稱": "主動群益科技創", "成立日期": "2025/12/30", "殖利率": "-", "配息": "季配"},
    "00992":  {"名稱": "群益科技創(舊代碼)", "成立日期": "-", "殖利率": "-", "配息": "-"}, 
    "00982A": {"名稱": "主動群益台灣強", "成立日期": "2025/05/22", "殖利率": "4.53%", "配息": "季配"},
    "00991A": {"名稱": "主動復華未來50", "成立日期": "2025/12/10", "殖利率": "-", "配息": "半年配"},
    "00990A": {"名稱": "主動元大AI高股", "成立日期": "2025/12/22", "殖利率": "-", "配息": "不配息"},
    "00988A": {"名稱": "主動統一全球創", "成立日期": "2025/11/05", "殖利率": "-", "配息": "年配"},
    "00400A": {"名稱": "主動國泰動能高", "成立日期": "2026/04/09", "殖利率": "-", "配息": "月配"},
    "00980A": {"名稱": "主動野村臺灣優", "成立日期": "2025/05/05", "殖利率": "3.26%", "配息": "季配"},
    "00993A": {"名稱": "主動文驊台灣", "成立日期": "2026/02/03", "殖利率": "-", "配息": "年配"},
    "00997A": {"名稱": "主動群益美國增", "成立日期": "2026/04/14", "殖利率": "-", "配息": "季配"},
    "00985A": {"名稱": "主動野村台灣50", "成立日期": "2025/07/21", "殖利率": "-", "配息": "年配"},
    "009B1D": {"名稱": "主動中信非投等", "成立日期": "2025/09/15", "殖利率": "3.77%", "配息": "月配"},
    "00984A": {"名稱": "主動安聯台灣高", "成立日期": "2025/07/14", "殖利率": "4.54%", "配息": "季配"},
    "00995A": {"名稱": "主動中信台灣增", "成立日期": "2026/01/22", "殖利率": "-", "配息": "季配"},
    "00994A": {"名稱": "主動第一金台股", "成立日期": "2026/01/02", "殖利率": "-", "配息": "季配"},
    "00996A": {"名稱": "主動兆豐台灣優", "成立日期": "2026/03/25", "殖利率": "-", "配息": "季配"},
    "00983A": {"名稱": "主動中信ARK創", "成立日期": "2025/08/18", "殖利率": "-", "配息": "年配"},
    "00986D": {"名稱": "主動復華金融債", "成立日期": "2026/04/15", "殖利率": "-", "配息": "月配"},
    "00401A": {"名稱": "主動華南台灣高", "成立日期": "2026/04/10", "殖利率": "-", "配息": "月配"},
    "00998A": {"名稱": "主動復華金融股", "成立日期": "2026/04/15", "殖利率": "-", "配息": "季配"},
    "00987A": {"名稱": "主動台新價值成", "成立日期": "2025/12/30", "殖利率": "-", "配息": "年配"},
    "00980D": {"名稱": "主動野村傳投高", "成立日期": "2025/08/04", "殖利率": "3.90%", "配息": "月配"},
    "00989A": {"名稱": "主動富邦美國科", "成立日期": "2025/11/22", "殖利率": "-", "配息": "季配"},
    "00984D": {"名稱": "主動安聯傳全球", "成立日期": "2026/02/04", "殖利率": "0.84%", "配息": "月配"},
    "00983D": {"名稱": "主動富邦複合收", "成立日期": "2025/10/14", "殖利率": "2.36%", "配息": "月配"},
    "00985D": {"名稱": "主動貝萊德優投", "成立日期": "2026/02/03", "殖利率": "-", "配息": "月配"},
    "00982D": {"名稱": "主動富邦動能入", "成立日期": "2025/10/14", "殖利率": "2.08%", "配息": "月配"},
    "00986A": {"名稱": "主動台新龍頭成", "成立日期": "2025/08/27", "殖利率": "-", "配息": "年配"},
    "00928":  {"名稱": "自訂監控清單", "成立日期": "-", "殖利率": "-", "配息": "-"},
    "020000": {"名稱": "自訂監控清單", "成立日期": "-", "殖利率": "-", "配息": "-"}
}

ETF_LIST = list(ETF_INFO.keys())
BASE_FONT_SIZE = "16px" 
TODAY_STR = datetime.now().strftime("%Y%m%d")

# ==========================================
# 🌸 第二區：【視覺魔法區】
# ==========================================
st.set_page_config(page_title="🌸 主人的 ETF 監控基地", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
    <style>
    html, body, [class*="css"] {{ font-size: {BASE_FONT_SIZE} !important; }}
    div[data-testid="stDataFrame"] {{ font-size: {BASE_FONT_SIZE} !important; }}
    div[data-testid="stMetricValue"] {{ font-size: 24px !important; }}
    div[data-testid="stMetricLabel"] > label > div {{ font-size: {BASE_FONT_SIZE} !important; }}
    div[role="radiogroup"] label {{ font-size: {BASE_FONT_SIZE} !important; }}
    </style>
""", unsafe_allow_html=True)

st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 第三區：【核心工具區】(真理大腦)
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
        df = df[df['股票代號'].str.contains(r'^\d+$', na=False)]
        
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
        
        p_nav = float(df_prev['__NAV_VALUE'].iloc[0]) if not df_prev.empty and '__NAV_VALUE' in df_prev.columns else 0.0
        
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        df_diff['增減張數'] = ((df_diff['持股股數_純數字'] - df_diff['持股股數_純數字_昨']) / 1000).round(2)
        
        df_change = df_diff[df_diff['增減張數'] != 0].copy().sort_values(by='增減張數', ascending=False)
        df_change['昨張數'] = (df_diff['持股股數_純數字_昨'] / 1000).round(2)
        df_change['今張數'] = (df_diff['持股股數_純數字'] / 1000).round(2)
        
        if '股票名稱' in df_change.columns:
            df_change['股票名稱'] = df_change['股票名稱'].replace(0, "已刪除/異動股票")
            
        return df_change, p_nav
    except:
        return None, 0.0

# ==========================================
# 🌸 第四區：【功能模組區】
# ==========================================

def render_etf_info_board():
    st.header("📖 總覽：全市場主動式 ETF 基本資料")
    st.caption("小粉根據主人的 APP 截圖，完美復刻的情報看板！一眼看穿所有成立時間與殖利率 ✨")
    
    # 將字典轉換為漂亮的 DataFrame
    df_info = pd.DataFrame.from_dict(ETF_INFO, orient='index').reset_index()
    df_info.rename(columns={'index': '代號'}, inplace=True)
    
    st.dataframe(
        df_info,
        column_config={
            "代號": st.column_config.TextColumn("標的代號"),
            "名稱": st.column_config.TextColumn("標的名稱"),
            "成立日期": st.column_config.TextColumn("成立日期"),
            "殖利率": st.column_config.TextColumn("殖利率"),
            "配息": st.column_config.TextColumn("配息頻率"),
        },
        use_container_width=True,
        hide_index=True,
        height=800
    )

def render_gods_eye_mode():
    st.header("👑 全市場投信籌碼總匯 (上帝視角)")
    all_changes, total_nav_diff, valid_etf_count = [], 0.0, 0
    for etf in ETF_LIST:
        f = [f for f in os.listdir() if f.startswith(f'holdings_{etf}_') and f.endswith('.csv')]
        f.sort(reverse=True)
        if len(f) >= 2:
            try:
                df_l = clean_df_columns(pd.read_csv(f[0], encoding='utf-8-sig'))
                df_d, p_nav = run_comparison(df_l, f[1])
                if df_d is not None: 
                    all_changes.append(df_d)
                    cur_nav = float(df_l['__NAV_VALUE'].iloc[0]) if not df_l['__NAV_VALUE'].empty else 0.0
                    if cur_nav > 0 and p_nav > 0:
                        total_nav_diff += (cur_nav - p_nav)
                        valid_etf_count += 1
            except: continue
            
    if all_changes:
        st.divider()
        st.subheader("💰 整個市場聯合資金動能")
        st.metric(f"綜合資金淨流向 (共 {valid_etf_count} 檔 ETF)", f"{total_nav_diff:,.0f} 元", delta=f"{total_nav_diff:,.0f}")
        
        mega = pd.concat(all_changes, ignore_index=True)
        sum_df = mega.groupby('股票代號').agg({'股票名稱': 'first', '昨張數': 'sum', '今張數': 'sum', '增減張數': 'sum'}).reset_index()
        
        def get_s(r):
            if r['昨張數'] == 0: return "✨ 新增"
            if r['今張數'] == 0: return "🗑️ 刪除"
            return "🔥 加碼" if r['增減張數'] > 0 else "❄️ 減碼"
        
        sum_df['狀態'] = sum_df.apply(get_s, axis=1)
        sum_df = sum_df[sum_df['增減張數'] != 0].copy().sort_values(by='增減張數', ascending=False)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.info(f"✨ 新增 {len(sum_df[sum_df['狀態']=='✨ 新增'])}")
        c2.error(f"🗑️ 刪除 {len(sum_df[sum_df['狀態']=='🗑️ 刪除'])}")
        c3.success(f"🔥 加碼 {len(sum_df[sum_df['狀態']=='🔥 加碼'])}")
        c4.warning(f"❄️ 減碼 {len(sum_df[sum_df['狀態']=='❄️ 減碼'])}")
        
        st.dataframe(sum_df[['股票代號', '股票名稱', '狀態', '昨張數', '今張數', '增減張數']].style.applymap(
            lambda x: 'color: green; font-weight: bold' if x > 0 else 'color: red; font-weight: bold', subset=['增減張數']
        ).format({'昨張數': '{:,.2f}', '今張數': '{:,.2f}', '增減張數': '{:+,.2f}'}), use_container_width=True, height=600)
    else: st.info("💡 目前資料不足喔！請確認各 ETF 都有至少兩天以上的存檔。")

def render_etf_mode(selected_etf):
    etf_name = ETF_INFO.get(selected_etf, {}).get("名稱", "")
    st.header(f"📊 {selected_etf} {etf_name} 分析儀表板")
    all_fs = [f for f in os.listdir() if f.startswith(f'holdings_{selected_etf}_') and f.endswith('.csv')]
    all_fs.sort(reverse=True)
    today_f = next((f for f in all_fs if TODAY_STR in f), None)
    prev_f = all_fs[0] if all_fs and not today_f else (all_fs[1] if len(all_fs) >= 2 else None)

    status_box = st.empty()
    if prev_f: status_box.success(f"📌 已鎖定基準檔：`{prev_f}`")
    else: status_box.warning(f"⚠️ 找不到歷史基準，本次上傳將建立第一份基準檔案。")

    uploaded_file = st.file_uploader(f"📂 上傳今日 {selected_etf} 的 XLSX 檔案", type=["xlsx"], key=f"up_{selected_etf}")
    final_df, current_df_today, today_nav, prev_nav = None, None, 0.0, 0.0

    if uploaded_file:
        all_sh = pd.read_excel(uploaded_file, sheet_name=None, header=None)
        for _, df in all_sh.items():
            for r_idx in range(min(len(df), 50)):
                row_vals = df.iloc[r_idx].astype(str).tolist()
                row_text = "".join(row_vals)
                if any(k in row_text for k in ["基金", "淨資產", "淨值", "規模"]) and ("每單位" not in row_text):
                    for offset in range(0, 3):
                        if r_idx + offset < len(df):
                            search_row = df.iloc[r_idx + offset].astype(str).tolist()
                            for cell in search_row:
                                num = extract_money(cell)
                                if num: today_nav = num; break
                        if today_nav: break
                if today_nav: break
            
            for i in range(min(len(df), 60)):
                vals = [str(v).strip() for v in df.iloc[i].values]
                has_code = any(any(k in v for k in ["股票代號", "股票代碼", "證券代號"]) for v in vals)
                has_name_or_shares = any(any(k in v for k in ["名稱", "股數", "張數", "數量", "權重"]) for v in vals)
                
                if has_code and has_name_or_shares:
                    df.columns = vals
                    df_t = clean_df_columns(df[i+1:].copy())
                    
                    if '股票代號' in df_t.columns:
                        target_cols = ['股票代號', '股票名稱', '持股股數_純數字', '權重%']
                        valid_cols = [c for c in target_cols if c in df_t.columns]
                        current_df_today = df_t[valid_cols].dropna(subset=['股票代號'])
                        current_df_today['__NAV_VALUE'] = today_nav
                        if prev_f: final_df, prev_nav = run_comparison(current_df_today, prev_f)
                    break
            if current_df_today is not None: break

    elif today_f:
        status_box.info(f"✨ 已自動讀取今日最新歸檔的比對結果！")
        df_saved = clean_df_columns(pd.read_csv(today_f, encoding='utf-8-sig'))
        today_nav = float(df_saved['__NAV_VALUE'].iloc[0]) if not df_saved.empty and '__NAV_VALUE' in df_saved.columns else 0.0
        current_df_today = df_saved
        if prev_f: final_df, prev_nav = run_comparison(df_saved, prev_f)

    if today_nav > 0:
        st.divider()
        st.subheader("💰 基金總資金水位監控")
        c1, c2, c3 = st.columns(3)
        c1.metric("今日總資金", f"{today_nav:,.0f} 元")
        if prev_nav > 0:
            c2.metric("昨日總資金", f"{prev_nav:,.0f} 元")
            c3.metric("資金水位增減", f"{today_nav-prev_nav:,.0f} 元", delta=f"{today_nav-prev_nav:,.0f}")

    if final_df is not None:
        st.divider()
        st.subheader("🔥 今日波動開獎")
        st.dataframe(final_df.style.applymap(
            lambda x: 'color: green; font-weight: bold' if x > 0 else 'color: red; font-weight: bold', 
            subset=['增減張數']
        ).format({'昨張數': '{:,.2f}', '今張數': '{:,.2f}', '增減張數': '{:+,.2f}'}), use_container_width=True)

    if current_df_today is not None:
        if final_df is None:
            st.divider()
            st.subheader("📋 今日持股預覽 (建立基準中)")
            st.dataframe(current_df_today, use_container_width=True)
        if uploaded_file:
            if st.button(f"💾 儲存 {selected_etf} 今日分析結果"):
                current_df_today.to_csv(f"holdings_{selected_etf}_{TODAY_STR}.csv", index=False, encoding='utf-8-sig')
                st.success(f"✅ {selected_etf} 數據已完美入庫！")
                st.balloons()

# ==========================================
# 🌸 第五區：【基地導航中心】
# ==========================================
st.sidebar.header("📁 監控目錄")
MENU_OPTIONS = ["🌟 全市場籌碼總匯", "📖 ETF 總覽清單"] + ETF_LIST
selected_mode = st.sidebar.radio("請點擊要查看的目標：", MENU_OPTIONS)

if selected_mode == "🌟 全市場籌碼總匯": 
    render_gods_eye_mode()
elif selected_mode == "📖 ETF 總覽清單":
    render_etf_info_board()
else: 
    render_etf_mode(selected_mode)

st.divider()
st.caption(f"🌸 目前基地存檔：{[f for f in os.listdir() if f.endswith('.csv')]}")