# 🌍 個人環境監測站 — Streamlit Dashboard

這是一個整合台灣環境部 (MOENV) 開放資料 API 的即時儀表板，提供使用者個人化的空氣品質、紫外線指數，以及空品預報資訊。採用 Streamlit 開發，具備快速反應與現代化深色 UI 介面設計。

![儀表板截圖](/home/toymsi/.gemini/antigravity/brain/c1be00b0-0d4f-4c52-aac1-da3433e6d90b/dashboard_success.png)

## ✨ 核心功能
*   **🏭 空氣品質監測**：即時抓取指定測站的 AQI、PM2.5、主要污染物等數據，並依據指數危害程度自動標示顏色（良好、普通、不健康…等）。
*   **☀️ 紫外線指數**：即時展示紫外線 (UVI) 數值與圖文並茂的曝曬防護等級建議。
*   **🗺️ 未來空品預報**：整合空品區（如北部、竹苗等）的未來趨勢預測與詳細文字預報說明。
*   **動態下拉選單**：支援一鍵切換不同測站、自動載入各縣市測站選單，資料重新計算不延遲。
*   **📊 詳細報表與地圖**：提供全台測站 AQI 排行榜以及測站地圖落點檢視。

## 🛠️ 技術限制與解法
*   此專案串接了 3 支環境部 API，因設有速率限制 (Rate limit)，程式核心內建了 `@st.cache_data(ttl=600)` 以確保資料具有 10 分鐘快取，藉此保證服務穩定。
*   考慮到部分伺服器或本機環境的 SSL 憑證驗證問題，已在 `requests` 請求中處理了 SSL 容錯。

## ⚙️ 安裝與啟動教學

### 1. 取得環境部 API 金鑰
請先至 [環境部開放資料平台](https://data.moenv.gov.tw/) 註冊並取得您的 API Key。

### 2. 環境設定
建議使用 Conda 建立虛擬環境 （專案預設使用名為 `toby` 的環境）。
```bash
# 複製環境變數設定檔
cp .env.example .env

# 在 .env 檔案中填入您的環境部 API Key
MOENV_API_KEY=您的金鑰
```

本專案依賴以下 Python 套件（可透過 `pip install -r requirements.txt`，若有的話安裝）：
* `streamlit`
* `requests`
* `pandas`
* `python-dotenv`
* `urllib3`

### 3. 本地端執行
```bash
streamlit run app.py
```
執行後，瀏覽器將會自動開啟 `http://localhost:8501`。

## 📁 專案結構
*   `app.py`: Streamlit 主程式
*   `ai_notice/GUIDELINES.md`: 專案 AI 開發筆記與特別注意事項
*   `.env.example`: 環境變數範例檔
