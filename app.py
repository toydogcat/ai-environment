"""
🌍 個人環境監測站 — Streamlit Dashboard
整合環境部開放 API，即時呈現空氣品質、紫外線指數、空品預報。
"""

import os
import streamlit as st
import requests
import pandas as pd
import urllib3
from dotenv import load_dotenv

# 抑制 urllib3 的 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ──────────────────────────────────────────────
# 0. 環境變數 & 頁面設定
# ──────────────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("MOENV_API_KEY", "")

st.set_page_config(
    page_title="🌍 個人環境監測站",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# 自訂 CSS — 進階視覺風格
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── 全域字體 & 背景 ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', 'Noto Sans TC', sans-serif;
}

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(56,189,248,0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(52,211,153,0.06) 0%, transparent 40%);
    animation: shimmer 8s ease-in-out infinite alternate;
}
@keyframes shimmer {
    0%   { transform: translate(0, 0); }
    100% { transform: translate(-5%, 3%); }
}
.hero-header h1 {
    color: #f0fdfa;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    position: relative;
    z-index: 1;
    letter-spacing: -0.5px;
}
.hero-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0.4rem 0 0;
    position: relative;
    z-index: 1;
}

/* ── Metric 卡片 ── */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}
div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-weight: 700;
    font-size: 2rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(148,163,184,0.1);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown {
    color: #cbd5e1 !important;
}

/* ── Expander ── */
details[data-testid="stExpander"] {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid rgba(148,163,184,0.1);
    border-radius: 14px;
    margin-top: 0.5rem;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* ── 狀態標籤 ── */
.status-badge {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.3px;
}
.aqi-good       { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
.aqi-moderate   { background: rgba(250,204,21,0.15); color: #facc15; border: 1px solid rgba(250,204,21,0.3); }
.aqi-unhealthy-s{ background: rgba(251,146,60,0.15); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); }
.aqi-unhealthy  { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.aqi-very-unh   { background: rgba(168,85,247,0.15); color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }
.aqi-hazardous  { background: rgba(127,29,29,0.3); color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }

/* ── 小資訊卡 ── */
.info-card {
    background: rgba(30,41,59,0.7);
    border: 1px solid rgba(148,163,184,0.1);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    backdrop-filter: blur(8px);
}
.info-card h4 {
    color: #e2e8f0;
    margin: 0 0 0.3rem;
    font-size: 0.9rem;
}
.info-card p {
    color: #94a3b8;
    margin: 0;
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ── 更新時間 ── */
.update-time {
    text-align: right;
    color: #64748b;
    font-size: 0.78rem;
    padding: 0.2rem 0;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 1. 輔助函數
# ──────────────────────────────────────────────

def _aqi_color_class(aqi_val: int) -> str:
    """根據 AQI 數值回傳 CSS class 名稱。"""
    if aqi_val <= 50:
        return "aqi-good"
    elif aqi_val <= 100:
        return "aqi-moderate"
    elif aqi_val <= 150:
        return "aqi-unhealthy-s"
    elif aqi_val <= 200:
        return "aqi-unhealthy"
    elif aqi_val <= 300:
        return "aqi-very-unh"
    else:
        return "aqi-hazardous"


def _aqi_status_text(aqi_val: int) -> str:
    """AQI 等級中文文字。"""
    if aqi_val <= 50:
        return "🟢 良好"
    elif aqi_val <= 100:
        return "🟡 普通"
    elif aqi_val <= 150:
        return "🟠 對敏感族群不健康"
    elif aqi_val <= 200:
        return "🔴 不健康"
    elif aqi_val <= 300:
        return "🟣 非常不健康"
    else:
        return "🟤 危害"


def _uvi_level(uvi_val: float) -> tuple[str, str]:
    """回傳 (等級文字, emoji)。"""
    if uvi_val < 0:
        return "無資料", "🌙"
    elif uvi_val <= 2:
        return "低量", "😊"
    elif uvi_val <= 5:
        return "中量", "🙂"
    elif uvi_val <= 7:
        return "高量", "😎"
    elif uvi_val <= 10:
        return "過量", "🥵"
    else:
        return "危險", "☠️"


# ──────────────────────────────────────────────
# 2. API 獲取函數（均快取 10 分鐘）
# ──────────────────────────────────────────────
BASE_URL = "https://data.moenv.gov.tw/api/v2"


@st.cache_data(ttl=600)
def fetch_aqi_data() -> list[dict]:
    """空氣品質即時資料（aqx_p_432）。"""
    try:
        resp = requests.get(
            f"{BASE_URL}/aqx_p_432",
            params={"format": "JSON", "limit": 1000, "api_key": API_KEY},
            timeout=15,
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", data) if isinstance(data, dict) else data
        return records if isinstance(records, list) else []
    except Exception as e:
        st.warning(f"⚠️ 空氣品質 API 請求失敗：{e}")
        return []


@st.cache_data(ttl=600)
def fetch_uv_data() -> list[dict]:
    """紫外線即時監測資料（uv_s_01）。"""
    try:
        resp = requests.get(
            f"{BASE_URL}/uv_s_01",
            params={"format": "JSON", "limit": 1000, "api_key": API_KEY},
            timeout=15,
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", data) if isinstance(data, dict) else data
        return records if isinstance(records, list) else []
    except Exception as e:
        st.warning(f"⚠️ 紫外線 API 請求失敗：{e}")
        return []


@st.cache_data(ttl=600)
def fetch_forecast_data() -> list[dict]:
    """空氣品質預報資料（aqf_p_01）。"""
    try:
        resp = requests.get(
            f"{BASE_URL}/aqf_p_01",
            params={"format": "JSON", "limit": 1000, "api_key": API_KEY},
            timeout=15,
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        records = data.get("records", data) if isinstance(data, dict) else data
        return records if isinstance(records, list) else []
    except Exception as e:
        st.warning(f"⚠️ 空品預報 API 請求失敗：{e}")
        return []


# ──────────────────────────────────────────────
# 3. 載入資料
# ──────────────────────────────────────────────
aqi_records = fetch_aqi_data()
uv_records = fetch_uv_data()
forecast_records = fetch_forecast_data()

# 取得可選站點 / 空品區
aqi_sites = sorted(set(r.get("sitename", "") for r in aqi_records if r.get("sitename")))
uv_sites_raw = [r.get("sitename", "") for r in uv_records if r.get("sitename")]
uv_sites = sorted(set(uv_sites_raw))
forecast_areas = sorted(set(r.get("area", "") for r in forecast_records if r.get("area")))

# ──────────────────────────────────────────────
# 4. Sidebar — 下拉選單 & 控制面板
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 監測設定")
    st.markdown("---")

    # 空品測站
    default_aqi = aqi_sites.index("士林") if "士林" in aqi_sites else 0
    selected_aqi_site = st.selectbox(
        "🏭 空品測站",
        aqi_sites if aqi_sites else ["（無可用測站）"],
        index=default_aqi,
        help="選擇空氣品質即時監測站",
    )

    # UV 測站
    default_uv = uv_sites.index("臺北") if "臺北" in uv_sites else 0
    selected_uv_site = st.selectbox(
        "☀️ 紫外線測站",
        uv_sites if uv_sites else ["（無可用測站）"],
        index=default_uv,
        help="選擇紫外線監測站（來源：中央氣象署 / 環境部）",
    )

    # 空品區
    default_area = forecast_areas.index("北部") if "北部" in forecast_areas else 0
    selected_area = st.selectbox(
        "🗺️ 預報空品區",
        forecast_areas if forecast_areas else ["（無可用空品區）"],
        index=default_area,
        help="選擇空氣品質預報區域",
    )

    st.markdown("---")

    # 刷新按鈕
    if st.button("🔄 重新整理資料", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<p style="color:#64748b;font-size:0.75rem;">'
        "資料來源：環境部開放資料平台<br>"
        "快取時間：10 分鐘"
        "</p>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# 5. Hero Header
# ──────────────────────────────────────────────
st.markdown(
    '<div class="hero-header">'
    "<h1>🌍 個人環境監測站</h1>"
    "<p>即時空氣品質 ・ 紫外線指數 ・ 空品預報 — 資料來自環境部開放平台</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 6. 篩選資料
# ──────────────────────────────────────────────

# — AQI —
site_aqi_data = next((r for r in aqi_records if r.get("sitename") == selected_aqi_site), None)

if site_aqi_data:
    try:
        aqi_val = int(site_aqi_data.get("aqi", 0))
    except (ValueError, TypeError):
        aqi_val = None
    try:
        pm25_val = float(site_aqi_data.get("pm2.5", 0))
    except (ValueError, TypeError):
        pm25_val = None
    aqi_status = site_aqi_data.get("status", "N/A")
    aqi_pollutant = site_aqi_data.get("pollutant", "—")
    aqi_publish = site_aqi_data.get("publishtime", "—")
    aqi_county = site_aqi_data.get("county", "")
else:
    aqi_val = pm25_val = None
    aqi_status = aqi_pollutant = aqi_publish = "N/A"
    aqi_county = ""

# — UV —
# 取最新一筆（datacreationdate 最大的）
site_uv_list = [r for r in uv_records if r.get("sitename") == selected_uv_site]
site_uv_list.sort(key=lambda x: x.get("datacreationdate", ""), reverse=True)
site_uv_data = site_uv_list[0] if site_uv_list else None

if site_uv_data:
    try:
        uvi_val = float(site_uv_data.get("uvi", -999))
    except (ValueError, TypeError):
        uvi_val = -999.0
    uv_time = site_uv_data.get("datacreationdate", "—")
else:
    uvi_val = -999.0
    uv_time = "N/A"

uvi_level_text, uvi_emoji = _uvi_level(uvi_val)

# — 預報 —
area_forecasts = [r for r in forecast_records if r.get("area") == selected_area]
# 依預報日期排序
area_forecasts.sort(key=lambda x: x.get("forecastdate", ""))
# 取最近日期的預報
next_forecast = area_forecasts[0] if area_forecasts else None

if next_forecast:
    try:
        fc_aqi = int(next_forecast.get("aqi", 0))
    except (ValueError, TypeError):
        fc_aqi = None
    fc_pollutant = next_forecast.get("majorpollutant", "—")
    fc_date = next_forecast.get("forecastdate", "—")
    fc_publish = next_forecast.get("publishtime", "—")
else:
    fc_aqi = None
    fc_pollutant = fc_date = fc_publish = "N/A"

# ──────────────────────────────────────────────
# 7. 核心 Metric 三欄
# ──────────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(f"##### 🏭 {selected_aqi_site} 空氣品質")
    if aqi_val is not None:
        st.metric("AQI 指數", aqi_val)
        css_cls = _aqi_color_class(aqi_val)
        status_txt = _aqi_status_text(aqi_val)
        st.markdown(f'<span class="status-badge {css_cls}">{status_txt}</span>', unsafe_allow_html=True)
        st.metric("PM2.5", f"{pm25_val} μg/m³" if pm25_val is not None else "N/A")
        st.markdown(
            f'<div class="info-card"><h4>主要污染物</h4><p>{aqi_pollutant}</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.metric("AQI 指數", "N/A")
        st.info(f"⚠️ 找不到 **{selected_aqi_site}** 的空品資料")

with col2:
    st.markdown(f"##### ☀️ {selected_uv_site} 紫外線")
    if uvi_val >= 0:
        st.metric("UVI 指數", f"{uvi_val:.1f}")
        st.markdown(
            f'<div class="info-card"><h4>{uvi_emoji} 曝曬等級</h4>'
            f"<p>{uvi_level_text}</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.metric("UVI 指數", "—")
        st.info("🌙 目前無紫外線資料（可能為夜間或維護中）")
    # UVI 等級對照
    with st.expander("📖 UVI 等級說明"):
        st.markdown(
            "| UVI | 等級 | 建議 |\n"
            "|-----|------|------|\n"
            "| 0-2 | 😊 低量 | 無需特別防護 |\n"
            "| 3-5 | 🙂 中量 | 建議戴帽、擦防曬 |\n"
            "| 6-7 | 😎 高量 | 減少戶外活動 |\n"
            "| 8-10 | 🥵 過量 | 避免外出 |\n"
            "| 11+ | ☠️ 危險 | 絕對避免外出 |"
        )

with col3:
    st.markdown(f"##### 🗺️ {selected_area} 空品預報")
    if fc_aqi is not None:
        st.metric("預報 AQI", fc_aqi, delta=None)
        fc_cls = _aqi_color_class(fc_aqi)
        fc_status = _aqi_status_text(fc_aqi)
        st.markdown(f'<span class="status-badge {fc_cls}">{fc_status}</span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="info-card"><h4>預報日期</h4><p>{fc_date}</p></div>'
            f'<div class="info-card"><h4>主要污染物</h4><p>{fc_pollutant}</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.metric("預報 AQI", "N/A")
        st.info(f"⚠️ 找不到 **{selected_area}** 的預報資料")

# 上次更新時間
st.markdown(
    f'<div class="update-time">'
    f"空品發佈：{aqi_publish} ｜ UVI 觀測：{uv_time} ｜ 預報發佈：{fc_publish}"
    f"</div>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# 8. 詳細資料展開區
# ──────────────────────────────────────────────
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 空品完整數據", "📅 多日預報", "📝 預報文字說明"])

with tab1:
    if site_aqi_data:
        detail_keys = {
            "測站": "sitename",
            "縣市": "county",
            "AQI": "aqi",
            "狀態": "status",
            "PM2.5 (μg/m³)": "pm2.5",
            "PM10 (μg/m³)": "pm10",
            "O₃ (ppb)": "o3",
            "O₃ 8hr (ppb)": "o3_8hr",
            "CO (ppm)": "co",
            "CO 8hr (ppm)": "co_8hr",
            "SO₂ (ppb)": "so2",
            "NO₂ (ppb)": "no2",
            "NOx (ppb)": "nox",
            "NO (ppb)": "no",
            "風速 (m/s)": "wind_speed",
            "風向 (°)": "wind_direc",
            "發佈時間": "publishtime",
        }
        detail_data = {k: site_aqi_data.get(v, "—") for k, v in detail_keys.items()}
        df_detail = pd.DataFrame([detail_data])
        st.dataframe(df_detail, use_container_width=True, hide_index=True)
    else:
        st.info("無空品資料可顯示")

with tab2:
    if area_forecasts:
        fc_rows = []
        for f in area_forecasts:
            fc_rows.append({
                "預報日期": f.get("forecastdate", "—"),
                "空品區": f.get("area", "—"),
                "AQI": f.get("aqi", "—"),
                "主要污染物": f.get("majorpollutant", "—"),
                "次要污染物": f.get("minorpollutant", "—") or "—",
                "發佈時間": f.get("publishtime", "—"),
            })
        df_fc = pd.DataFrame(fc_rows)
        st.dataframe(df_fc, use_container_width=True, hide_index=True)
    else:
        st.info("無預報資料可顯示")

with tab3:
    if area_forecasts:
        # 只取最新發佈的一筆 content
        latest_fc = max(area_forecasts, key=lambda x: x.get("publishtime", ""))
        content_text = latest_fc.get("content", "（無內容）")
        # content 中的 \\n 轉為換行
        content_text = content_text.replace("\\n", "\n")
        st.markdown(
            f'<div class="info-card"><p>{content_text}</p></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("無預報說明可顯示")

# ──────────────────────────────────────────────
# 9. 全台空品地圖（附加功能）
# ──────────────────────────────────────────────
st.markdown("---")
with st.expander("🗺️ 全台空品測站總覽", expanded=False):
    if aqi_records:
        map_rows = []
        for r in aqi_records:
            try:
                lat = float(r.get("latitude", 0))
                lon = float(r.get("longitude", 0))
                if lat > 0 and lon > 0:
                    map_rows.append({
                        "lat": lat,
                        "lon": lon,
                        "sitename": r.get("sitename", ""),
                        "aqi": r.get("aqi", ""),
                    })
            except (ValueError, TypeError):
                continue
        if map_rows:
            df_map = pd.DataFrame(map_rows)
            st.map(df_map, latitude="lat", longitude="lon", use_container_width=True)

            # 全站 AQI 排名
            st.markdown("#### 📈 全台 AQI 排行")
            ranking_rows = []
            for r in aqi_records:
                try:
                    a = int(r.get("aqi", 0))
                except (ValueError, TypeError):
                    a = 0
                ranking_rows.append({
                    "測站": r.get("sitename", ""),
                    "縣市": r.get("county", ""),
                    "AQI": a,
                    "狀態": r.get("status", ""),
                    "PM2.5": r.get("pm2.5", ""),
                    "主要污染物": r.get("pollutant", ""),
                })
            df_rank = pd.DataFrame(ranking_rows).sort_values("AQI", ascending=False)
            st.dataframe(df_rank, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("無法載入測站資料")
