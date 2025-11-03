import streamlit as st
import pandas as pd
import requests
import yaml
import locale
from datetime import date
from pathlib import Path

# 自作モジュール
from utils.csv_io import export_csv, import_csv

API_URL = os.getenv("API_URL", "https://blood-pressure-api.onrender.com")


# --- 言語ファイルロード ---
LOCALE_DIR = Path(__file__).parent / "locales"


def load_translations():
    translations = {}
    for file in LOCALE_DIR.glob("*.yaml"):
        lang_code = file.stem
        with open(file, "r", encoding="utf-8") as f:
            translations[lang_code] = yaml.safe_load(f)
    return translations


TEXTS = load_translations()


# --- OSロケールで初期言語を自動設定 ---
def detect_language():
    try:
        system_lang = locale.getdefaultlocale()[0]
    except Exception:
        system_lang = "en"
    if system_lang.startswith("ja"):
        return "ja"
    elif system_lang.startswith("zh"):
        return "zh"
    else:
        return "en"


default_lang = detect_language()

# --- 言語選択 ---
lang_code = st.sidebar.selectbox(
    "🌐 Language / 言語",
    list(TEXTS.keys()),
    index=list(TEXTS.keys()).index(default_lang),
)
T = TEXTS[lang_code]

# --- Streamlit 設定 ---
st.set_page_config(page_title="Blood Pressure App", page_icon="🩺")
st.title(T["title"])

# --- 入力フォーム ---
st.subheader(T["form_title"])

with st.form("bp_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        d = st.date_input(T["date"], value=date.today())
    with col2:
        sys = st.number_input(T["systolic"], min_value=0, max_value=250, value=120)
    with col3:
        dia = st.number_input(T["diastolic"], min_value=0, max_value=200, value=80)
    pulse = st.number_input(T["pulse"], min_value=0, max_value=200, value=70)
    note = st.text_input(T["note"])

    submitted = st.form_submit_button(T["submit"])

    if submitted:
        payload = {
            "date": str(d),
            "systolic": sys,
            "diastolic": dia,
            "pulse": pulse,
            "note": note,
        }
        res = requests.post(f"{API_URL}/bp", json=payload)
        if res.status_code == 200:
            st.success(T["success"])
        else:
            st.error(f"{T['error']}: {res.status_code}")

# --- データ表示 ---
st.subheader(T["table"])
res = requests.get(f"{API_URL}/bp")

if res.status_code == 200:
    data = res.json()
    df = pd.DataFrame(data)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=True)
        df["weekday"] = df["date"].dt.weekday
        df["day_type"] = df["weekday"].apply(
            lambda x: T["holiday"] if x >= 5 else T["workday"]
        )

        # --- 表とグラフ ---
        st.dataframe(df[["date", "day_type", "systolic", "diastolic", "pulse", "note"]])
        st.line_chart(df.set_index("date")[["systolic", "diastolic"]])

        # --- 統計 ---
        st.subheader(T["stats"])
        avg_sys = df["systolic"].mean()
        avg_dia = df["diastolic"].mean()
        max_sys = df["systolic"].max()
        min_sys = df["systolic"].min()
        max_dia = df["diastolic"].max()
        min_dia = df["diastolic"].min()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("平均 / Avg (High)", f"{avg_sys:.1f}")
            st.metric("平均 / Avg (Low)", f"{avg_dia:.1f}")
        with col2:
            st.metric("最高 / Max (High)", f"{max_sys}")
            st.metric("最高 / Max (Low)", f"{max_dia}")
        with col3:
            st.metric("最低 / Min (High)", f"{min_sys}")
            st.metric("最低 / Min (Low)", f"{min_dia}")

        # --- 平日/休日統計 ---
        st.subheader(T["weekday_stats"])
        grouped = (
            df.groupby("day_type")[["systolic", "diastolic", "pulse"]].mean().round(1)
        )
        st.table(
            grouped.rename(
                columns={
                    "systolic": "Systolic / 上",
                    "diastolic": "Diastolic / 下",
                    "pulse": "Pulse / 脈拍",
                }
            )
        )

        # --- 最新値 ---
        st.subheader(T["latest"])
        latest = df.iloc[-1]
        st.write(f"{T['date']}: {latest['date'].date()}（{latest['day_type']}）")
        st.write(f"{T['systolic']}: {latest['systolic']} mmHg")
        st.write(f"{T['diastolic']}: {latest['diastolic']} mmHg")
        st.write(f"{T['pulse']}: {latest['pulse']} bpm")
        if latest["note"]:
            st.write(f"{T['note']}: {latest['note']}")

        # --- 📤 CSVエクスポート ---
        st.subheader("📤 CSVエクスポート")
        csv_data = export_csv(df)
        st.download_button(
            label="💾 CSVをダウンロード / Download CSV",
            data=csv_data,
            file_name="blood_pressure_records.csv",
            mime="text/csv",
        )

        # --- 📥 CSVインポート ---
        st.subheader("📥 CSVインポート")

        # ✅ サンプルCSVのダウンロードボタンを追加
        sample_df = pd.DataFrame(
            {
                "date": ["2025-11-01", "2025-11-02", "2025-11-03"],
                "systolic": [125, 118, 122],
                "diastolic": [80, 76, 78],
                "pulse": [70, 68, 72],
                "note": ["朝測定", "夜測定", "昼食後"],
            }
        )

        st.markdown("以下の形式でCSVを作成してください：")
        st.dataframe(sample_df)

        sample_csv = sample_df.to_csv(index=False)
        st.download_button(
            label="📄 サンプルCSVをダウンロード / Download sample CSV",
            data=sample_csv,
            file_name="sample_blood_pressure.csv",
            mime="text/csv",
        )

        # --- CSVファイルアップロード ---
        uploaded = st.file_uploader("CSVファイルを選択 / Choose CSV file", type=["csv"])
        if uploaded is not None:
            try:
                df_preview = pd.read_csv(uploaded)
                st.write("プレビュー / Preview:")
                st.dataframe(df_preview.head())

                if st.button("⬆️ DBにインポート / Import to DB"):
                    success_count = import_csv(uploaded, API_URL)
                    st.success(f"✅ {success_count} 件のレコードを追加しました！")
            except Exception as e:
                st.error(f"❌ 読み込みエラー: {e}")
