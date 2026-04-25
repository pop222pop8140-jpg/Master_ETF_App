import streamlit as st       # 🌸 [小粉教學] 這是建立網頁介面的魔法棒
import pandas as pd          # 🌸 [小粉教學] 這是處理 Excel/CSV 表格的最強大腦
from datetime import datetime # 🌸 [小粉教學] 用來抓取今天的日期
import os                    # 🌸 [小粉教學] 用來翻找電腦/雲端資料夾裡的檔案
import re                    # 🌸 [小粉教學] 正規表達式，用來精準搜尋字串（例如過濾掉中文字只留數字）

# ==========================================
# 🌸 第一區：【完整資料庫】
# ==========================================
# 🌸 [小粉教學] 未來如果有新的 ETF，只要照著格式加在這裡，左側選單就會自動出現喔！
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

ETF_LIST = list(ETF_INFO.keys()) # 把所有的代號抽出來變成一個清單
TODAY_STR = datetime.now().strftime("%Y%m%d") # 產出今天的字串，例如 "20260425"

# ==========================================
# 🌸 第二區：【視覺魔法：全面強化 20 點字】
# ==========================================
# 🌸 [小粉教學] 這裡設定網頁為「寬螢幕模式 (wide)」
st.set_page_config(page_title="🌸 主人的 ETF 監控基地", layout="wide")

# 🌸 [小粉教學] 這裡是網頁的 CSS 裝潢！主人如果想改字體大小，就把 20px 改成別的數字。
st.markdown("""
    <style>
    /* 全域字體大小強制設定為 20px */
    html, body, [class*="st-"], .stMarkdown, .stText, .stButton, .stSelectbox, .stRadio, .stTable, .stDataFrame, p, li, span, div {
        font-size: 20px !important;
    }
    /* 側邊欄文字大小 */
    [data-testid="stSidebar"] * { font-size: 20px !important; }
    /* 表格內部字體大小 */
    .stDataFrame td, .stDataFrame th, [data-testid="stTable"] td, [data-testid="stTable"] th {
        font-size: 20px !important;
    }
    /* 今日總資金等大數字標籤設定 */
    [data-testid="stMetricValue"] { font-size: 45px !important; font-weight: bold; }
    [data-testid="stMetricLabel"] p { font-size: 24px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🌸 主人的主動式 ETF 雙重監控基地")

# ==========================================
# 🌸 第三區：【核心邏輯：強健讀取引擎】
# ==========================================
def robust_read_file(filename):
    """
    🌸 [小粉教學] 這個函數負責安全地打開檔案。
    元大的 CSV 很調皮，第一行只有一個字，所以我們強制設定 names=range(25)，
    意思是「不管你長怎樣，我都先預留 25 個位子給你」，這樣就不會報錯了！
    """
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(filename, encoding='utf-8-sig', header=None, names=range(25), on_bad_lines='skip')
        else:
            return pd.read_excel(filename, header=None, names=range(25))
    except: 
        return pd.DataFrame() # 如果檔案壞掉，就回傳空表格，不讓網頁當機

def clean_df_columns(df):
    """
    🌸 [小粉教學] 這個函數是心臟！負責把亂七八糟的 Excel/CSV 洗乾淨變成統一格式。
    """
    if df.empty: return df
    df = df.fillna("") # 把空白格子填上空字串，防止出錯
    fund_nav = 0.0
    
    # 🔍 步驟 1：掃描 Metadata (元大、復華專用：尋找千萬以上的真實資產)
    # 🌸 [小粉教學] 掃描前 40 列，找尋「基金淨資產價值」等關鍵字
    for i in range(min(len(df), 40)):
        row_list = [str(x).strip() for x in df.iloc[i].values]
        for idx, val in enumerate(row_list):
            if any(k in val for k in ["基金淨資資產價值", "基金資產淨值", "淨資產", "資產金額", "股票"]) and \
               not any(ex in val for ex in ["代號", "代碼", "名稱", "數量", "權重"]): # 排除欄位標題，怕抓到 2330
                
                potential_vals = []
                if idx + 1 < len(row_list): potential_vals.append(row_list[idx+1]) # 找右邊一格
                if i + 1 < len(df): potential_vals.append(str(df.iloc[i+1, idx]))  # 找下面一格
                
                for p_val in potential_vals:
                    val_clean = re.sub(r'[^\d.]', '', p_val) # 只保留數字跟小數點
                    if val_clean:
                        try:
                            f_val = float(val_clean)
                            if f_val > 10000000: fund_nav = max(fund_nav, f_val) # ✨ 門檻：大於一千萬才承認是總資產
                        except: pass
        if fund_nav > 0: break

    # 🕵️‍♀️ 步驟 2：智能標題定位
    # 🌸 [小粉教學] 往下找，只要看到「代號」這兩個字，就把那一列當作真正的表頭！
    header_idx = -1
    for i in range(min(len(df), 40)):
        row_values = [str(x).strip() for x in df.iloc[i].values]
        if any(re.search(r'代號|代碼|證券代號|商品代碼', x) for x in row_values):
            df.columns = row_values; header_idx = i; break
            
    # 把表頭上面的廢話全部切掉
    if header_idx != -1: df = df.iloc[header_idx+1:].reset_index(drop=True)
    
    # 🏷️ 步驟 3：欄位重新對應
    # 🌸 [小粉教學] 各家投信的名字不一樣，我們把它們統一換成小粉看得懂的標準名稱。
    new_cols = {}
    for col in df.columns:
        c = str(col).strip()
        c_clean = re.sub(r'[^\w%]', '', c)
        if any(x in c_clean for x in ['代號', '代碼', '證券代號', '商品代碼']): new_cols[col] = '股票代號'
        elif any(x in c_clean for x in ['名稱', '商品名稱']): new_cols[col] = '股票名稱'
        elif any(x in c_clean for x in ['股數', '張數', '數量', '持股數', '商品數量']): new_cols[col] = '持股股數_純數字'
        elif any(x in c_clean for x in ['權重', '比例', '商品權重']): new_cols[col] = '權重%'
        elif any(x in c_clean for x in ['NAV', '淨資產', '基金規模', '價值']): new_cols[col] = '__NAV_VALUE'
    
    df = df.rename(columns=new_cols) # 執行改名
    
    # 🧹 步驟 4：資料清洗
    if '股票代號' in df.columns:
        # 去掉小數點 .0，並確保只保留數字、底線或英文字母 (防止抓到奇怪的結尾字)
        df['股票代號'] = df['股票代號'].astype(str).str.strip().str.replace('.0', '', regex=False)
        df = df[df['股票代號'].str.contains(r'^\d+|_|[A-Z]', na=False)]
        
    if '持股股數_純數字' in df.columns:
        # 把逗號跟空白去掉，然後變成純數字
        df['持股股數_純數字'] = pd.to_numeric(df['持股股數_純數字'].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0)
        
    if '權重%' in df.columns:
        # 把 % 符號拔掉
        df['權重%'] = df['權重%'].astype(str).str.replace('%', '').str.strip()

    # ✨ 步驟 5：淨值寫入
    # 🌸 [小粉教學] 如果上面找得到千萬總資產就用，找不到就看表格裡有沒有淨值欄位。
    if fund_nav > 0:
        df['__NAV_VALUE'] = fund_nav
    elif '__NAV_VALUE' in df.columns:
        nav_series = pd.to_numeric(df['__NAV_VALUE'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df['__NAV_VALUE'] = nav_series.max()
    else:
        df['__NAV_VALUE'] = 0.0

    return df

def run_comparison(today_df, prev_filename):
    """
    🌸 [小粉教學] 這是比對「昨天」跟「今天」資料的機器。
    它會找出變化的張數，並計算出買超與賣超。
    """
    try:
        df_prev = robust_read_file(prev_filename)
        df_prev = clean_df_columns(df_prev)
        today_df = clean_df_columns(today_df)
        
        # 抓出兩天的總資產
        t_nav = today_df['__NAV_VALUE'].iloc[0] if not today_df.empty else 0.0
        p_nav = df_prev['__NAV_VALUE'].iloc[0] if not df_prev.empty else 0.0
        
        # outer merge 意思是：不管昨天有今天沒有、還是今天有昨天沒有的股票，全部抓出來！
        df_diff = pd.merge(today_df, df_prev[['股票代號', '持股股數_純數字']], on='股票代號', how='outer', suffixes=('', '_昨')).fillna(0)
        df_stocks = df_diff[df_diff['股票代號'].str.contains(r'^\d+|[A-Z]', na=False)].copy()
        
        # 除以 1000 把「股」變成「張」
        df_stocks['昨張數'] = (df_stocks['持股股數_純數字_昨'] / 1000).round(2)
        df_stocks['今張數'] = (df_stocks['持股股數_純數字'] / 1000).round(2)
        df_stocks['增減張數'] = (df_stocks['今張數'] - df_stocks['昨張數']).round(2)
        
        # 把沒變化的股票過濾掉，然後依照變動大小排序
        df_change = df_stocks[df_stocks['增減張數'] != 0].sort_values(by='增減張數', ascending=False)
        return df_change, t_nav, p_nav
    except: return None, 0.0, 0.0

# ==========================================
# 🌸 第四區：【渲染頁面】
# ==========================================
def render_manual_upload():
    # 🌸 [小粉教學] 這是左側選單的「手動新增資料」畫面
    st.header("📥 手動新增持股資料 (基地增援)")
    col1, col2 = st.columns(2)
    with col1:
        selected_etf = st.selectbox("1. 選擇要存入的 ETF 標的：", ETF_LIST, index=ETF_LIST.index("00400A"))
        upload_date = st.date_input("2. 選擇這份資料的日期：", datetime.now())
    with col2:
        uploaded_file = st.file_uploader("3. 請選擇 Excel 或 CSV 檔案", type=["xlsx", "csv", "xls"])
    
    # 如果有上傳檔案，就自動改成對應的檔名存起來
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1]
        target_filename = f"holdings_{selected_etf}_{upload_date.strftime('%Y%m%d')}.{file_ext}"
        with open(target_filename, "wb") as f: f.write(uploaded_file.getbuffer())
        st.success(f"✨ 報告主人！資料已成功入庫：`{target_filename}`"); st.balloons()

def render_gods_eye():
    # 🌸 [小粉教學] 這是「全市場籌碼總匯」畫面，負責把所有 ETF 的買賣超加總起來看主力動向！
    st.header("👑 全市場投信籌碼總匯")
    all_files = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and not f.startswith('~$')]
    if not all_files: return st.info("💡 雲端目前是空的喔！")
    
    all_changes = []
    # 去每一檔 ETF 的資料夾裡面撈出今天跟昨天的檔案進行比對
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
        # 把所有變動串在一起，並依據股票代號做加總 (groupby)
        master_df = pd.concat(all_changes, ignore_index=True); summary_df = master_df.groupby(['股票代號', '股票名稱'], as_index=False)['增減張數'].sum()
        top_buys = summary_df[summary_df['增減張數'] > 0].sort_values(by='增減張數', ascending=False)
        top_sells = summary_df[summary_df['增減張數'] < 0].sort_values(by='增減張數', ascending=True)
        c1, c2 = st.columns(2)
        with c1: st.subheader("🚀 買超總排行"); st.dataframe(top_buys, use_container_width=True, hide_index=True)
        with c2: st.subheader("📉 賣超總排行"); st.dataframe(top_sells, use_container_width=True, hide_index=True)

def render_etf_mode(etf_code):
    # 🌸 [小粉教學] 這是各檔 ETF 的專屬監控頁面
    info = ETF_INFO.get(etf_code, {}); st.header(f"📊 {etf_code} {info.get('名稱','')} 分析儀")
    all_fs = [f for f in os.listdir() if (f.endswith('.csv') or f.endswith('.xlsx')) and f.startswith(f'holdings_{etf_code}_')]; all_fs.sort(reverse=True)
    today_f = next((f for f in all_fs if TODAY_STR in f), (all_fs[0] if all_fs else None))
    prev_f = next((f for f in all_fs if f != today_f), None)
    
    if today_f:
        try:
            df_raw = robust_read_file(today_f); df_full = clean_df_columns(df_raw)
            if prev_f:
                df_change, t_nav, p_nav = run_comparison(df_full, prev_f)
                st.subheader("💰 基金總資產資金水位監控")
                c1, c2, c3 = st.columns(3)
                # 🌸 [小粉教學] 防呆設定：如果 API 沒給總資金 (0元)，就會顯示原有格式，不會嚇到主人！
                with c1: st.metric("今日總資金", f"{t_nav:,.0f} 元" if t_nav > 0 else "0 元")
                with c2: st.metric("近期總資金", f"{p_nav:,.0f} 元" if p_nav > 0 else "0 元")
                with c3:
                    delta = t_nav - p_nav
                    st.metric("資金水位增減", f"{delta:,.0f} 元", delta_color="normal", delta=f"{delta:,.0f}")
                
                if df_change is not None:
                    st.subheader("🔥 今日動開獎")
                    st.dataframe(df_change[['股票代號', '股票名稱', '昨張數', '今張數', '增減張數', '權重%']], use_container_width=True, hide_index=True)
            st.subheader(f"📋 目前完整持股明細 ({today_f})")
            display_cols = [c for c in ['股票代號', '股票名稱', '持股股數_純數字', '權重%'] if c in df_full.columns]
            st.dataframe(df_full[display_cols], use_container_width=True, hide_index=True)
        except Exception as e: st.error(f"🌸 解析發生錯誤：{e}")
    else: st.warning("⚠️ 雲端尚無資料檔案。")

# ==========================================
# 🌸 第五區：【導航中心】
# ==========================================
# 🌸 [小粉教學] 這裡負責畫出左邊那個可以點來點去的側邊選單
st.sidebar.header("📁 監控目錄")
selected = st.sidebar.radio("請點擊目標：", ["🌟 全市場籌碼總匯", "📖 ETF 總覽清單", "📥 手動新增資料"] + ETF_LIST)

# 依據主人的點擊，呼叫上面做好的不同畫面
if selected == "🌟 全市場籌碼總匯": render_gods_eye()
elif selected == "📖 ETF 總覽清單": st.table(pd.DataFrame(ETF_INFO).T)
elif selected == "📥 手動新增資料": render_manual_upload()
else: render_etf_mode(selected)