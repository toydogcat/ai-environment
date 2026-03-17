# 個人環境監測站 — 開發注意事項

## 環境設定
- **Python 環境**：使用 Conda `toby` 環境
  - 路徑：`/home/toymsi/miniconda3/envs/toby/bin/python`
  - 啟用方式：`conda activate toby`
- **環境變數**：複製 `.env.example` 為 `.env` 並填入實際值
- **已安裝套件**：`streamlit`, `requests`, `pandas`, `python-dotenv`

## API 使用注意

### MOENV 環境部開放資料 API
- **API 金鑰** 存放在 `.env` 的 `MOENV_API_KEY`
- **Rate Limit**：請務必使用 `@st.cache_data(ttl=600)` 快取 10 分鐘，避免超出請求限制
- **API 基底 URL**：`https://data.moenv.gov.tw/api/v2`

### 三支 API 端點

| 端點 | 資料集 ID | 說明 |
|------|-----------|------|
| 空氣品質即時 | `aqx_p_432` | ~85 個測站，含 AQI、PM2.5、O3 等 |
| 紫外線即時 | `uv_s_01` | ~30 個測站（來源：中央氣象署 / 環境部） |
| 空品預報 | `aqf_p_01` | 9 個空品區，含多日預報 |

### 已知 API 行為
- **UVI 值 `-999`**：表示無資料（通常為夜間），UI 需友善處理
- **紫外線與空品測站名不同**：UV 用城市名（如「臺北」），AQI 用行政區名（如「士林」）
- **預報有重複站點**：同一 `area` 有多筆 `forecastdate`，需依日期排序

## 啟動方式
```bash
conda activate toby
cd /home/toymsi/documents/projects/Github/ai-environment
streamlit run app.py --server.port 8501
```

## 專案結構
```
ai-environment/
├── app.py              # Streamlit 主程式
├── ai_notice/
│   └── GUIDELINES.md   # 本文件：開發注意事項
├── .env                # 環境變數（含 API 金鑰，已 gitignore）
├── .env.example        # 環境變數範例
├── .gitignore
├── LICENSE
└── README.md
```
