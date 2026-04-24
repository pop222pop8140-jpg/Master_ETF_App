import requests
import pandas as pd
from datetime import datetime
import os

# --- 🛠️ 基地設定區域 ---
# 主人可以在這裡隨時新增想要採集的標的
ETF_TARGETS = {
    "00400A": "EA",
    "00981A": "I7",
    "00982A": "I8",
    "00992A": "I9"  # 假設的代碼，請主人依此類推
}

def collect_etf_data(etf_name, fund_code):
    print(f"🌸 --------------------------------------------")
    print(f"🚀 小蜜蜂出動！目標：{etf_name} (代碼: {fund_code})")
    
    api_url = f"https://cwapi.cathaysite.com.tw/api/ETF/GetETFDetailStockList?FundCode={fund_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        json_data = response.json()
        
        # 🕵️‍♀️ 偵錯雷達
        print(f"🔍 API 回傳狀態: {json_data.get('success', '未知')}")
        stock_list = json_data.get('result', [])

        if not stock_list:
            print(f"⚠️ 警告：{etf_name} 金庫空空的，API 沒給資料！(可能還沒更新)")
            return

        data = []
        for item in stock_list:
            stock_code = str(item.get("stockCode", "")).strip()
            if stock_code:
                data.append({
                    "股票代號": stock_code,
                    "股票名稱": str(item.get("stockName", "")).strip(),
                    "持股股數_純數字": str(item.get("volumn", "")).replace(',', '').strip(),
                    "權重%": str(item.get("weights", "")).strip(),
                    "採集時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        if data:
            today_str = datetime.now().strftime("%Y%m%d")
            filename = f"holdings_{etf_name}_{today_str}.csv"
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ {etf_name} 採集成功！產出：{filename}")
        
    except Exception as e:
        print(f"❌ {etf_name} 發生意外了：{e}")

# --- 🎬 執行區 ---
if __name__ == "__main__":
    print(f"✨ 啟動時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for name, code in ETF_TARGETS.items():
        collect_etf_data(name, code)
    print("🌸 所有採集任務已完成，小粉下班囉！")