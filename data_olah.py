import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

import tempfile
import io
import os

# ------------------------------------------------------------------
# MULTI-LANGUAGE SUPPORT
# ------------------------------------------------------------------
LANGUAGES = {
    "en": {
        "page_title": "📊 The Relationship between Fear of Missing Out (FOMO) and Social Media Addiction among Generation Z",
        "subtitle": "Statistics 1 • Class 1",
        "sidebar_members": "👥 Group Members",
        "language_selector": "🌐 Language",
        "upload_dataset": "1. Upload Dataset",
        "upload_instruction": "Upload a CSV or Excel file:",
        "upload_info": "Please upload a dataset first.",
        "preview_data": "Preview data (First 5 rows, before age cleaning):",
        "see_columns": "See all column names (headers):",
        "age_detected": "Age column detected as:",
        "age_not_found": "Age column not found. Make sure there's a column with 'Age' or 'Umur' in the name.",
        "data_clean_success": "✅ Data cleaning & age grouping completed.",
        "data_clean_summary": "**Data Cleaning Summary:**",
        "respondents_before": "Respondents before cleaning:",
        "respondents_after": "Respondents after cleaning (13–28 years only):",
        "respondents_removed": "Removed respondents:",
        "age_distribution": "**Age Group Distribution:**",
        "num_respondents": "Number of respondents",
        "preview_after_clean": "Preview data after cleaning & age grouping:",
        "select_variables": "2. Select Variables X and Y (fixed item set)",
        "fomo_items": "FOMO (X) – Choose Items:",
        "fomo_help": "Select X1–X5 items (As per Questionnaire).",
        "addiction_items": "Social Media Addiction (Y) – Choose Items:",
        "addiction_help": "Select Y1–Y5 items (As per Questionnaire).",
        "selected_fomo": "**Selected FOMO items:**",
        "selected_addiction": "**Selected Addiction items:**",
        "min_selection": "Please select at least 1 item for X and 1 item for Y.",
        "composite_scores": "3. Composite Scores (X_total & Y_total)",
        "composite_method": "Composite score method:",
        "mean_items": "Mean of items (recommended)",
        "sum_items": "Sum of items",
        "composite_success": "✅ Composite scores X_total and Y_total have been successfully created.",
        "normality_test": "Normality Test (Shapiro–Wilk)",
        "result": "### Result:",
        "variable": "Variable",
        "statistic": "Shapiro-Wilk Statistic",
        "p_value": "p-value",
        "normality": "Normality",
        "normal": "Normal",
        "not_normal": "Not Normal",
        "recommended_method": "✅ Recommended association method based on normality test:",
        "valid_respondents": "Valid respondents (after age filter)",
        "avg_fomo": "Average FOMO (X_total)",
        "avg_addiction": "Average Addiction (Y_total)",
        "association_analysis": "4. Association Analysis – Choose Method",
        "association_method": "Association method for X and Y (based on normality recommendation):",
        "pearson": "Pearson Correlation",
        "spearman": "Spearman Rank Correlation",
        "chi_square": "Chi-square Test (categorical X & Y)",
        "chi_instruction": "**Chi-square Test – Select categorical X and Y variables (Likert).**",
        "categorical_x": "Categorical X variable:",
        "categorical_y": "Categorical Y variable:",
        "tab_desc": "📋 Descriptive Statistics",
        "tab_vis": "📈 Visualizations",
        "tab_assoc": "🔗 Analysis Result",
        "tab_pdf": "📄 PDF Report",
        "demographic_summary": "### 5.0 Demographic Summary",
        "age_group_dist": "**Age Group Distribution**",
        "gender_dist": "**Gender Distribution**",
        "gender_not_detected": "Gender column was not detected, so gender distribution is not shown.",
        "desc_items": "### 5.1 Descriptive Statistics – Each Survey Item",
        "desc_composite": "### 5.2 Descriptive Statistics – Composite Scores (X_total & Y_total)",
        "freq_table": "### 5.3 Frequency & Percentage Table (All X and Y Items)",
        "freq_caption": "Table shows frequency distribution for each questionnaire item X1 to Y5. Charts available in '📈 Visualizations' tab.",
        "result_for_item": "#### Result for Item:",
        "frequency": "Frequency",
        "percentage": "Percentage (%)",
        "likert_note": "Note: STS=Strongly Disagree, SS=Strongly Agree.",
        "visualizations": "### 6. Visualizations",
        "age_chart": "#### 6.1 Distribution of Respondents by Age Group",
        "hist_x": "#### 6.2 Distribution of X_total (FOMO)",
        "hist_y": "#### 6.3 Distribution of Y_total (Social Media Addiction)",
        "scatter": "#### 6.4 Scatterplot: X_total (FOMO) vs Y_total (Social Media Addiction)",
        "item_charts": "#### 6.5 Interactive Bar Charts for Each Survey Item",
        "item_caption": "Bar charts show response distribution for each questionnaire item.",
        "stacked_chart": "#### 6.6 Interactive Stacked Bar Chart: Response Percentage Across All Items",
        "stacked_caption": "This chart shows percentage distribution of responses for all questionnaire items (X1-Y5).",
        "item": "Item:",
        "assoc_result": "### 7. Association Analysis",
        "result_corr": "#### Result",
        "corr_coef": "Correlation Coefficient (r)",
        "direction": "Direction",
        "strength": "Strength",
        "significance": "Significance",
        "interpretation": "#### Interpretation:",
        "visual_check": "#### Visual Check: Scatterplot",
        "chi_result": "#### Chi-square Test Result between",
        "chi_value": "Chi-square Value (χ²)",
        "dof": "Degrees of Freedom (dof)",
        "contingency": "#### Contingency Table",
        "select_method": "Please select an association method in section **4. Association Analysis** above.",
        "pdf_export": "### 8. Export PDF Report",
        "pdf_filename": "PDF file name (without .pdf):",
        "pdf_layout": "**PDF Visualization Layout Settings:**",
        "charts_per_row": "Charts per Row:",
        "select_content": "Select content to include in PDF:",
        "include_items": "Descriptive statistics – items (X & Y)",
        "include_comp": "Descriptive statistics – composite scores (X_total & Y_total)",
        "include_corr": "Association analysis summary",
        "include_demo": "Demographic summary (Age & Gender)",
        "include_normality": "Normality test result (Shapiro–Wilk)",
        "visualizations_pdf": "**Visualizations**",
        "include_freq": "Frequency bar charts (All X and Y items)",
        "include_stacked": "Stacked Bar Chart (All Item Response Percentage)",
        "include_hist_x": "Histogram X_total",
        "include_hist_y": "Histogram Y_total",
        "include_scatter": "Scatterplot X_total vs Y_total",
        "include_age": "Demographic bar chart (Age Group)",
        "generate_pdf": "Generate PDF Report",
        "pdf_success": "✅ PDF Report '{}' successfully created and ready for download.",
        "pdf_error": "Failed to build PDF. Make sure all charts fit on the page (Try changing 'Charts per Row' to 1 or 2). Error details: {}",
        "download_pdf": "Download PDF Report",
        "age_group": "Age Group",
        "x_total_score": "X_total Score (FOMO)",
        "y_total_score": "Y_total Score (Social Media Addiction)",
        "response_score": "Response Score",
        "survey_item": "Survey Item",
        "regression_line": "Regression line",
    },
    "id": {
        "page_title": "📊 Hubungan antara Fear of Missing Out (FOMO) dan Kecanduan Media Sosial pada Generasi Z",
        "subtitle": "Statistika 1 • Kelas 1",
        "sidebar_members": "👥 Anggota Kelompok",
        "language_selector": "🌐 Bahasa",
        "upload_dataset": "1. Unggah Dataset",
        "upload_instruction": "Unggah file CSV atau Excel:",
        "upload_info": "Silakan unggah dataset terlebih dahulu.",
        "preview_data": "Preview data (5 baris pertama, sebelum pembersihan usia):",
        "see_columns": "Lihat semua nama kolom (header):",
        "age_detected": "Kolom usia terdeteksi sebagai:",
        "age_not_found": "Kolom usia tidak ditemukan. Pastikan ada kolom dengan nama mengandung 'Age' atau 'Umur'.",
        "data_clean_success": "✅ Pembersihan data & pengelompokan usia selesai.",
        "data_clean_summary": "**Ringkasan Pembersihan Data:**",
        "respondents_before": "Responden sebelum pembersihan:",
        "respondents_after": "Responden setelah pembersihan (usia 13–28 tahun saja):",
        "respondents_removed": "Responden dihapus:",
        "age_distribution": "**Distribusi Kelompok Usia:**",
        "num_respondents": "Jumlah responden",
        "preview_after_clean": "Preview data setelah pembersihan & pengelompokan usia:",
        "select_variables": "2. Pilih Variabel X dan Y (set item tetap)",
        "fomo_items": "FOMO (X) – Pilih Item:",
        "fomo_help": "Pilih item X1–X5 (Sesuai Kuesioner).",
        "addiction_items": "Kecanduan Media Sosial (Y) – Pilih Item:",
        "addiction_help": "Pilih item Y1–Y5 (Sesuai Kuesioner).",
        "selected_fomo": "**Item FOMO yang dipilih:**",
        "selected_addiction": "**Item Kecanduan yang dipilih:**",
        "min_selection": "Minimal pilih 1 item untuk X dan 1 item untuk Y.",
        "composite_scores": "3. Skor Komposit (X_total & Y_total)",
        "composite_method": "Metode skor komposit:",
        "mean_items": "Rata-rata item (direkomendasikan)",
        "sum_items": "Jumlah item",
        "composite_success": "✅ Skor komposit X_total dan Y_total berhasil dibuat.",
        "normality_test": "Uji Normalitas (Shapiro–Wilk)",
        "result": "### Hasil:",
        "variable": "Variabel",
        "statistic": "Statistik Shapiro-Wilk",
        "p_value": "nilai-p",
        "normality": "Normalitas",
        "normal": "Normal",
        "not_normal": "Tidak Normal",
        "recommended_method": "✅ Metode asosiasi yang direkomendasikan berdasarkan uji normalitas:",
        "valid_respondents": "Responden valid (setelah filter usia)",
        "avg_fomo": "Rata-rata FOMO (X_total)",
        "avg_addiction": "Rata-rata Kecanduan (Y_total)",
        "association_analysis": "4. Analisis Asosiasi – Pilih Metode",
        "association_method": "Metode asosiasi untuk X dan Y (berdasarkan rekomendasi normalitas):",
        "pearson": "Korelasi Pearson",
        "spearman": "Korelasi Rank Spearman",
        "chi_square": "Uji Chi-square (X & Y kategorikal)",
        "chi_instruction": "**Uji Chi-square – Pilih variabel X dan Y kategorikal (Likert).**",
        "categorical_x": "Variabel X kategorikal:",
        "categorical_y": "Variabel Y kategorikal:",
        "tab_desc": "📋 Statistik Deskriptif",
        "tab_vis": "📈 Visualisasi",
        "tab_assoc": "🔗 Hasil Analisis",
        "tab_pdf": "📄 Laporan PDF",
        "demographic_summary": "### 5.0 Ringkasan Demografi",
        "age_group_dist": "**Distribusi Kelompok Usia**",
        "gender_dist": "**Distribusi Jenis Kelamin**",
        "gender_not_detected": "Kolom jenis kelamin tidak terdeteksi, sehingga distribusi jenis kelamin tidak ditampilkan.",
        "desc_items": "### 5.1 Statistik Deskriptif – Setiap Item Survei",
        "desc_composite": "### 5.2 Statistik Deskriptif – Skor Komposit (X_total & Y_total)",
        "freq_table": "### 5.3 Tabel Frekuensi & Persentase (Semua Item X dan Y)",
        "freq_caption": "Tabel menunjukkan distribusi frekuensi untuk setiap item kuesioner X1 hingga Y5. Grafik tersedia di tab '📈 Visualisasi'.",
        "result_for_item": "#### Hasil untuk Item:",
        "frequency": "Frekuensi",
        "percentage": "Persentase (%)",
        "likert_note": "Keterangan: STS=Sangat Tidak Setuju, SS=Sangat Setuju.",
        "visualizations": "### 6. Visualisasi",
        "age_chart": "#### 6.1 Distribusi Responden Berdasarkan Kelompok Usia",
        "hist_x": "#### 6.2 Distribusi X_total (FOMO)",
        "hist_y": "#### 6.3 Distribusi Y_total (Kecanduan Media Sosial)",
        "scatter": "#### 6.4 Scatterplot: X_total (FOMO) vs Y_total (Kecanduan Media Sosial)",
        "item_charts": "#### 6.5 Grafik Batang Interaktif untuk Setiap Item Survei",
        "item_caption": "Grafik batang menunjukkan distribusi jawaban untuk setiap item kuesioner.",
        "stacked_chart": "#### 6.6 Grafik Batang Bertumpuk Interaktif: Persentase Respons untuk Semua Item",
        "stacked_caption": "Grafik ini menunjukkan persentase distribusi jawaban untuk semua item kuesioner (X1-Y5).",
        "item": "Item:",
        "assoc_result": "### 7. Analisis Asosiasi",
        "result_corr": "#### Hasil",
        "corr_coef": "Koefisien Korelasi (r)",
        "direction": "Arah",
        "strength": "Kekuatan",
        "significance": "Signifikansi",
        "interpretation": "#### Interpretasi:",
        "visual_check": "#### Pemeriksaan Visual: Scatterplot",
        "chi_result": "#### Hasil Uji Chi-square antara",
        "chi_value": "Nilai Chi-square (χ²)",
        "dof": "Derajat Kebebasan (dof)",
        "contingency": "#### Tabel Kontingensi",
        "select_method": "Silakan pilih metode asosiasi di bagian **4. Analisis Asosiasi** di atas.",
        "pdf_export": "### 8. Ekspor Laporan PDF",
        "pdf_filename": "Nama file PDF (tanpa .pdf):",
        "pdf_layout": "**Pengaturan Layout Visualisasi dalam PDF:**",
        "charts_per_row": "Grafik per Baris:",
        "select_content": "Pilih konten yang ingin dimasukkan ke PDF:",
        "include_items": "Statistik deskriptif – item (X & Y)",
        "include_comp": "Statistik deskriptif – skor komposit (X_total & Y_total)",
        "include_corr": "Ringkasan analisis asosiasi",
        "include_demo": "Ringkasan demografi (Usia & Jenis Kelamin)",
        "include_normality": "Hasil uji normalitas (Shapiro–Wilk)",
        "visualizations_pdf": "**Visualisasi**",
        "include_freq": "Grafik batang frekuensi (Semua item X dan Y)",
        "include_stacked": "Grafik Batang Bertumpuk (Persentase Respons Semua Item)",
        "include_hist_x": "Histogram X_total",
        "include_hist_y": "Histogram Y_total",
        "include_scatter": "Scatterplot X_total vs Y_total",
        "include_age": "Grafik batang demografi (Kelompok Usia)",
        "generate_pdf": "Buat Laporan PDF",
        "pdf_success": "✅ Laporan PDF '{}' berhasil dibuat dan siap diunduh.",
        "pdf_error": "Gagal membangun PDF. Pastikan semua grafik muat di halaman (Coba ubah 'Grafik per Baris' menjadi 1 atau 2). Detail Error: {}",
        "download_pdf": "Unduh Laporan PDF",
        "age_group": "Kelompok Usia",
        "x_total_score": "Skor X_total (FOMO)",
        "y_total_score": "Skor Y_total (Kecanduan Media Sosial)",
        "response_score": "Skor Respons",
        "survey_item": "Item Survei",
        "regression_line": "Garis regresi",
    }
}

RESPONSE_LABELS_EN = {
    1: "1 (SD: Strongly Disagree)",
    2: "2 (D: Disagree)",
    3: "3 (N: Neutral)",
    4: "4 (A: Agree)",
    5: "5 (SA: Strongly Agree)",
}

RESPONSE_LABELS_ID = {
    1: "1 (STS: Sangat Tidak Setuju)",
    2: "2 (TS: Tidak Setuju)",
    3: "3 (N: Netral)",
    4: "4 (S: Setuju)",
    5: "5 (SS: Sangat Setuju)",
}

FOMO_LABELS_EN = {
    "X1": "I feel anxious if I don't know the latest updates on social media.",
    "X2": "I feel the urge to constantly check social media to stay connected.",
    "X3": "I'm afraid of being left behind when others talk about trending topics.",
    "X4": "I feel the need to follow viral trends to stay 'included'.",
    "X5": "I feel uncomfortable when I see others participating in activities that I am not part of.",
}

FOMO_LABELS_ID = {
    "X1": "Saya merasa cemas jika tidak tahu update terbaru di media sosial.",
    "X2": "Saya merasa perlu terus mengecek media sosial agar tetap terhubung.",
    "X3": "Saya takut ketinggalan saat orang lain membahas topik yang sedang tren.",
    "X4": "Saya merasa perlu mengikuti tren viral agar tetap 'masuk'.",
    "X5": "Saya merasa tidak nyaman saat melihat orang lain mengikuti aktivitas yang tidak saya ikuti.",
}

ADDICTION_LABELS_EN = {
    "Y1": "I find it difficult to reduce the amount of time I spend on social media.",
    "Y2": "I prefer using social media over doing offline activities.",
    "Y3": "Social media usage disrupts my sleep, study time, or other important activities.",
    "Y4": "I often spend more time on social media than I originally planned.",
    "Y5": "I often open social media automatically without any clear purpose.",
}

ADDICTION_LABELS_ID = {
    "Y1": "Saya kesulitan mengurangi waktu yang saya habiskan di media sosial.",
    "Y2": "Saya lebih suka menggunakan media sosial daripada melakukan aktivitas offline.",
    "Y3": "Penggunaan media sosial mengganggu tidur, waktu belajar, atau aktivitas penting lainnya.",
    "Y4": "Saya sering menghabiskan lebih banyak waktu di media sosial dari yang saya rencanakan.",
    "Y5": "Saya sering membuka media sosial secara otomatis tanpa tujuan yang jelas.",
}

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="FOMO & Social Media Addiction – Group 3",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------
# LANGUAGE SELECTOR IN SIDEBAR
# ------------------------------------------------------------------
st.sidebar.markdown("### 🌐 Language / Bahasa")
selected_lang = st.sidebar.radio(
    "Select Language",
    options=["en", "id"],
    format_func=lambda x: "🇺🇸 English" if x == "en" else "🇮🇩 Indonesia",
    horizontal=True,
    label_visibility="collapsed"
)

# Get translations for selected language
t = LANGUAGES[selected_lang]
RESPONSE_LABELS = RESPONSE_LABELS_EN if selected_lang == "en" else RESPONSE_LABELS_ID
FOMO_LABELS = FOMO_LABELS_EN if selected_lang == "en" else FOMO_LABELS_ID
ADDICTION_LABELS = ADDICTION_LABELS_EN if selected_lang == "en" else ADDICTION_LABELS_ID

# ------------------------------------------------------------------
# TITLE & SIDEBAR
# ------------------------------------------------------------------
st.title(t["page_title"])
st.caption(t["subtitle"])

st.sidebar.markdown("---")
st.sidebar.header(t["sidebar_members"])
st.sidebar.write("- Delon Raphael Andianto (004202200050)")
st.sidebar.write("- Kallista Viasta (004202200039)")
st.sidebar.write("- Nabila Putri Amalia (004202200049)")
st.sidebar.write("- Pingkan R G Lumingkewas (004202200035)")

# ------------------------------------------------------------------
# 1. UPLOAD DATASET
# ------------------------------------------------------------------
st.subheader(t["upload_dataset"])

uploaded = st.file_uploader(
    t["upload_instruction"],
    type=["csv", "xlsx"]
)

if uploaded is None:
    st.info(t["upload_info"])
    st.stop()

if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

st.write(t["preview_data"])
st.dataframe(df.head(), width='stretch')

with st.expander(t["see_columns"]):
    st.write(list(df.columns))

# ------------------------------------------------------------------
# 1A. DATA CLEANING – AGE CATEGORIES
# ------------------------------------------------------------------
AGE_COLUMN = None
for col in df.columns:
    col_lower = str(col).lower()
    if "age" in col_lower or "umur" in col_lower:
        AGE_COLUMN = col
        break

if AGE_COLUMN is None:
    st.error(t["age_not_found"])
    st.stop()

st.write(f"{t['age_detected']} **{AGE_COLUMN}**")

allowed_age_categories = [
    "13–18 years / tahun",
    "19–23 years / tahun",
    "24–28 years / tahun",
    "13-18 years / tahun",
    "19-23 years / tahun",
    "24-28 years / tahun",
]

before_clean = len(df)
df = df[df[AGE_COLUMN].isin(allowed_age_categories)]
after_clean = len(df)

df["Age_Group"] = df[AGE_COLUMN].astype("category")

st.success(t["data_clean_success"])
st.write(t["data_clean_summary"])
st.write(f"- {t['respondents_before']} {before_clean}")
st.write(f"- {t['respondents_after']} {after_clean}")
st.write(f"- {t['respondents_removed']} {before_clean - after_clean}")

st.write(t["age_distribution"])
st.dataframe(df["Age_Group"].value_counts().rename(t["num_respondents"]), width='stretch')

st.write(t["preview_after_clean"])
st.dataframe(df.head(), width='stretch')

# ------------------------------------------------------------------
# DEMOGRAPHIC SUMMARY
# ------------------------------------------------------------------
age_counts = df["Age_Group"].value_counts().sort_index()
age_demo_df = pd.DataFrame({
    t["age_group"]: age_counts.index,
    t["frequency"]: age_counts.values,
})
age_demo_df[t["percentage"]] = (age_demo_df[t["frequency"]] / age_demo_df[t["frequency"]].sum() * 100).round(2)

GENDER_COLUMN = None
for col in df.columns:
    col_lower = str(col).lower()
    if "gender" in col_lower or "jenis kelamin" in col_lower:
        GENDER_COLUMN = col
        break

gender_demo_df = None
if GENDER_COLUMN is not None:
    gender_counts = df[GENDER_COLUMN].value_counts().sort_index()
    gender_demo_df = pd.DataFrame({
        "Gender": gender_counts.index,
        t["frequency"]: gender_counts.values,
    })
    gender_demo_df[t["percentage"]] = (gender_demo_df[t["frequency"]] / gender_demo_df[t["frequency"]].sum() * 100).round(2)

# ------------------------------------------------------------------
# 2. VARIABLE MAPPING
# ------------------------------------------------------------------
fixed_x_all = list(FOMO_LABELS.keys())
fixed_y_all = list(ADDICTION_LABELS.keys())

if not all(c in df.columns for c in fixed_x_all + fixed_y_all):
    PHRASES = {
        "X1": "anxious if i don't know the latest updates",
        "X2": "urge to constantly check social media",
        "X3": "afraid of being left behind when others talk about trending topics",
        "X4": "need to follow viral trends to stay",
        "X5": "uncomfortable when i see others participating in activities that i am not part of",
        "Y1": "difficult to reduce the amount of time i spend on social media",
        "Y2": "prefer using social media over doing offline activities",
        "Y3": "disrupts my sleep, study time, or other important activities",
        "Y4": "spend more time on social media than i originally planned",
        "Y5": "open social media automatically without any clear purpose",
    }

    lower_cols = {c: str(c).lower() for c in df.columns}
    renamed = {}

    for code, phrase in PHRASES.items():
        phrase_low = phrase.lower()
        for col, col_low in lower_cols.items():
            if phrase_low in col_low:
                renamed[col] = code

    df = df.rename(columns=renamed)

missing_x = [c for c in fixed_x_all if c not in df.columns]
missing_y = [c for c in fixed_y_all if c not in df.columns]

if missing_x or missing_y:
    error_msg = f"Missing FOMO (X): {missing_x}\nMissing Addiction (Y): {missing_y}"
    st.error(error_msg)
    st.write("Current headers:", list(df.columns))
    st.stop()

# ------------------------------------------------------------------
# 3. SELECT VARIABLES
# ------------------------------------------------------------------
st.subheader(t["select_variables"])

cA, cB = st.columns(2)

with cA:
    x_items = st.multiselect(
        t["fomo_items"],
        options=fixed_x_all,
        default=fixed_x_all,
        help=t["fomo_help"],
    )
    st.markdown(t["selected_fomo"])
    for code in x_items:
        st.caption(f"**{code}** — {FOMO_LABELS[code]}")

with cB:
    y_items = st.multiselect(
        t["addiction_items"],
        options=fixed_y_all,
        default=fixed_y_all,
        help=t["addiction_help"],
    )
    st.markdown(t["selected_addiction"])
    for code in y_items:
        st.caption(f"**{code}** — {ADDICTION_LABELS[code]}")

if len(x_items) == 0 or len(y_items) == 0:
    st.warning(t["min_selection"])
    st.stop()

for col in x_items + y_items:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------------
# 4. COMPOSITE SCORES
# ------------------------------------------------------------------
st.subheader(t["composite_scores"])

comp_method = st.radio(
    t["composite_method"],
    [t["mean_items"], t["sum_items"]],
    horizontal=True,
)

if t["mean_items"] in comp_method:
    df["X_total"] = df[x_items].mean(axis=1)
    df["Y_total"] = df[y_items].mean(axis=1)
else:
    df["X_total"] = df[x_items].sum(axis=1)
    df["Y_total"] = df[y_items].sum(axis=1)

st.success(t["composite_success"])

valid_xy = df[["X_total", "Y_total"]].dropna()
n_valid = valid_xy.shape[0]
mean_x = valid_xy["X_total"].mean()
mean_y = valid_xy["Y_total"].mean()

# ------------------------------------------------------------------
# NORMALITY TEST
# ------------------------------------------------------------------
st.subheader(t["normality_test"])

shapiro_x = stats.shapiro(valid_xy["X_total"])
shapiro_y = stats.shapiro(valid_xy["Y_total"])

normal_x = t["normal"] if shapiro_x.pvalue >= 0.05 else t["not_normal"]
normal_y = t["normal"] if shapiro_y.pvalue >= 0.05 else t["not_normal"]

st.write(t["result"])

result_norm = pd.DataFrame({
    t["variable"]: ["X_total", "Y_total"],
    t["statistic"]: [shapiro_x.statistic, shapiro_y.statistic],
    t["p_value"]: [shapiro_x.pvalue, shapiro_y.pvalue],
    t["normality"]: [normal_x, normal_y]
})

st.dataframe(result_norm.round(4), width='stretch')

if normal_x == t["normal"] and normal_y == t["normal"]:
    recommended_method = t["pearson"]
else:
    recommended_method = t["spearman"]

st.info(f"{t['recommended_method']} **{recommended_method}**")

m1, m2, m3 = st.columns(3)
m1.metric(t["valid_respondents"], n_valid)
m2.metric(t["avg_fomo"], f"{mean_x:.2f}")
m3.metric(t["avg_addiction"], f"{mean_y:.2f}")

# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------
def descriptive_table(data: pd.DataFrame, cols):
    rows = []
    for col in cols:
        s = data[col].dropna()
        if s.empty:
            continue
        mode_vals = s.mode()
        mode_val = mode_vals.iloc[0] if not mode_vals.empty else np.nan
        rows.append({
            t["variable"]: col,
                "N": len(s),
                "Mean": s.mean(),
                "Median": s.median(),
                "Mode": mode_val,
                "Min": s.min(),
                "Max": s.max(),
                "Std Dev": s.std(ddof=1),
        })
    return pd.DataFrame(rows).set_index(t["variable"]).round(3)

# ------------------------------------------------------------------
# 6. ASSOCIATION METHOD
# ------------------------------------------------------------------
st.subheader(t["association_analysis"])

assoc_method = st.radio(
    t["association_method"],
    [t["pearson"], t["spearman"], t["chi_square"]],
    index=0,
)

assoc_stats = {}
assoc_summary_text = ""

if assoc_method in [t["pearson"], t["spearman"]]:
    x_corr = valid_xy["X_total"]
    y_corr = valid_xy["Y_total"]

    if t["pearson"] in assoc_method:
        r_value, p_value = stats.pearsonr(x_corr, y_corr)
        method_short = "Pearson"
    else:
        r_value, p_value = stats.spearmanr(x_corr, y_corr)
        method_short = "Spearman"

    def interpret_strength(r):
        a = abs(r)
        if a < 0.2:
            return "very weak" if selected_lang == "en" else "sangat lemah"
        elif a < 0.4:
            return "weak" if selected_lang == "en" else "lemah"
        elif a < 0.6:
            return "moderate" if selected_lang == "en" else "sedang"
        elif a < 0.8:
            return "strong" if selected_lang == "en" else "kuat"
        else:
            return "very strong" if selected_lang == "en" else "sangat kuat"

    direction = "positive" if r_value > 0 else "negative"
    if selected_lang == "id":
        direction = "positif" if r_value > 0 else "negatif"
    
    strength = interpret_strength(r_value)
    signif_text = "significant (p < 0.05)" if p_value < 0.05 else "not significant (p ≥ 0.05)"
    if selected_lang == "id":
        signif_text = "signifikan (p < 0,05)" if p_value < 0.05 else "tidak signifikan (p ≥ 0,05)"

    assoc_stats = {
        "type": "correlation",
        "method": method_short,
        "r": r_value,
        "p": p_value,
        "direction": direction,
        "strength": strength,
        "signif_text": signif_text,
    }

    if selected_lang == "en":
        assoc_summary_text = (
            f"Using the {method_short} correlation, there is a {direction} and {strength} "
            f"relationship between FOMO (X_total) and social media addiction (Y_total), "
            f"with r = {r_value:.3f} and p = {p_value:.4f}, indicating that the association is "
            f"{signif_text}."
        )
    else:
        assoc_summary_text = (
            f"Menggunakan korelasi {method_short}, terdapat hubungan {direction} dan {strength} "
            f"antara FOMO (X_total) dan kecanduan media sosial (Y_total), "
            f"dengan r = {r_value:.3f} dan p = {p_value:.4f}, menunjukkan bahwa asosiasi tersebut "
            f"{signif_text}."
        )

else:
    st.markdown(t["chi_instruction"])
    cat_options = x_items + y_items
    chi_x_col = st.selectbox(t["categorical_x"], cat_options, key="chi_x")
    chi_y_col = st.selectbox(t["categorical_y"], cat_options, key="chi_y")

    contingency = pd.crosstab(df[chi_x_col], df[chi_y_col])
    chi2_value, p_chi, dof, expected = stats.chi2_contingency(contingency)
    signif_text = "significant (p < 0.05)" if p_chi < 0.05 else "not significant (p ≥ 0.05)"
    if selected_lang == "id":
        signif_text = "signifikan (p < 0,05)" if p_chi < 0.05 else "tidak signifikan (p ≥ 0,05)"

    assoc_stats = {
        "type": "chi-square",
        "method": "Chi-square",
        "chi2": chi2_value,
        "p": p_chi,
        "dof": dof,
        "x": chi_x_col,
        "y": chi_y_col,
        "signif_text": signif_text,
    }

    if selected_lang == "en":
        assoc_summary_text = (
            f"Using the Chi-square test between {chi_x_col} and {chi_y_col}, "
            f"the chi-square statistic is χ² = {chi2_value:.3f} with {dof} degrees of freedom "
            f"and p = {p_chi:.4f}, indicating that the association is {signif_text}."
        )
    else:
        assoc_summary_text = (
            f"Menggunakan uji Chi-square antara {chi_x_col} dan {chi_y_col}, "
            f"statistik chi-square adalah χ² = {chi2_value:.3f} dengan {dof} derajat kebebasan "
            f"dan p = {p_chi:.4f}, menunjukkan bahwa asosiasi tersebut {signif_text}."
        )

# ------------------------------------------------------------------
# 7. TABS
# ------------------------------------------------------------------
tab_desc, tab_vis, tab_assoc, tab_pdf = st.tabs([
    t["tab_desc"], t["tab_vis"], t["tab_assoc"], t["tab_pdf"]
])

# ------------------ TAB DESCRIPTIVES ------------------
with tab_desc:
    st.markdown(t["demographic_summary"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(t["age_group_dist"])
        st.dataframe(age_demo_df, width='stretch')

    with col2:
        if gender_demo_df is not None:
            st.markdown(t["gender_dist"])
            st.dataframe(gender_demo_df, width='stretch')
        else:
            st.info(t["gender_not_detected"])

    st.markdown(t["desc_items"])
    desc_items = descriptive_table(df, x_items + y_items)
    st.dataframe(desc_items, width='stretch')

    st.markdown(t["desc_composite"])
    desc_comp = descriptive_table(df, ["X_total", "Y_total"])
    st.dataframe(desc_comp, width='stretch')

    st.markdown(t["freq_table"])
    st.caption(t["freq_caption"])

    all_items = x_items + y_items

    # Display frequency tables in 2 columns for better UX
    cols = st.columns(2)

    for idx, var_freq in enumerate(all_items):
        with cols[idx % 2]:
            st.markdown(f"#### {t['result_for_item']} **{var_freq}**")
            
            s_freq = df[var_freq].dropna()
            freq = s_freq.value_counts().sort_index()
            perc = (freq / freq.sum() * 100).round(2)
            freq_table = pd.DataFrame({t["frequency"]: freq, t["percentage"]: perc})

            if freq_table.index.dtype in [int, float] and freq_table.index.max() <= 5:
                labeled_index = freq_table.index.map(lambda x: RESPONSE_LABELS.get(x, x))
                freq_table.index = labeled_index
                st.caption(t["likert_note"])

            st.dataframe(freq_table, width='stretch')

# ------------------ TAB VISUALIZATIONS (PLOTLY INTERACTIVE) ------------------
with tab_vis:
    st.markdown(t["visualizations"])
    
    # 1. Age Group Distribution - Interactive Bar Chart
    st.markdown(t["age_chart"])
    fig_age = px.bar(
        x=age_counts.index,
        y=age_counts.values,
        labels={'x': t["age_group"], 'y': t["frequency"]},
        title=t["age_chart"].replace("#### ", ""),
        color=age_counts.values,
        color_continuous_scale='Blues'
    )
    fig_age.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_age, width='stretch')
    
    st.markdown("---")
    
    # 2 & 3. Histograms in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(t["hist_x"])
        fig_hist_x = px.histogram(
            valid_xy,
            x="X_total",
            nbins=20,
            labels={'X_total': t["x_total_score"]},
            title=t["hist_x"].replace("#### ", ""),
            color_discrete_sequence=['#FF6B6B']
        )
        fig_hist_x.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_hist_x, width='stretch')
    
    with col2:
        st.markdown(t["hist_y"])
        fig_hist_y = px.histogram(
            valid_xy,
            x="Y_total",
            nbins=20,
            labels={'Y_total': t["y_total_score"]},
            title=t["hist_y"].replace("#### ", ""),
            color_discrete_sequence=['#4ECDC4']
        )
        fig_hist_y.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_hist_y, width='stretch')
    
    st.markdown("---")
    
    # 4. Interactive Scatterplot with animation
    st.markdown(t["scatter"])
    
    # Calculate regression line
    z = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
    p = np.poly1d(z)
    x_line = np.linspace(valid_xy["X_total"].min(), valid_xy["X_total"].max(), 100)
    y_line = p(x_line)
    
    # Create scatter plot
    fig_scatter = px.scatter(
        valid_xy,
        x="X_total",
        y="Y_total",
        labels={
            'X_total': t["x_total_score"],
            'Y_total': t["y_total_score"]
        },
        title=t["scatter"].replace("#### ", ""),
        color="X_total",
        color_continuous_scale='Viridis',
        opacity=0.7
    )
    
    # Add regression line
    fig_scatter.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            name=t["regression_line"],
            line=dict(color='red', dash='dash', width=2)
        )
    )
    
    fig_scatter.update_layout(height=500)
    fig_scatter.update_traces(marker=dict(size=8), selector=dict(mode='markers'))
    st.plotly_chart(fig_scatter, width='stretch')
    
    st.markdown("---")
    
    # 5. Interactive Bar Charts for Each Item - in 2 columns
    st.markdown(t["item_charts"])
    st.caption(t["item_caption"])
    
    all_items = x_items + y_items
    
    # Display charts in 2 columns
    cols = st.columns(2)
    
    for idx, item_code in enumerate(all_items):
        with cols[idx % 2]:
            st.markdown(f"##### {t['item']} **{item_code}**")
            
            if item_code in FOMO_LABELS:
                st.caption(f"*{FOMO_LABELS[item_code]}*")
            elif item_code in ADDICTION_LABELS:
                st.caption(f"*{ADDICTION_LABELS[item_code]}*")
            
            s_freq = df[item_code].dropna()
            freq = s_freq.value_counts().sort_index()
            
            if not freq.empty:
                fig_item = px.bar(
                    x=freq.index.astype(str),
                    y=freq.values,
                    labels={'x': item_code, 'y': t["frequency"]},
                    title=f"{item_code}",
                    color=freq.values,
                    color_continuous_scale='RdYlGn'
                )
                fig_item.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig_item, width='stretch')
    
            st.markdown("---")
    
    # 6. Interactive Stacked Bar Chart
            st.markdown(t["stacked_chart"])
    st.caption(t["stacked_caption"])
    
    freq_data = df[all_items].apply(lambda x: x.value_counts(normalize=True)).T * 100
    freq_data = freq_data.fillna(0).sort_index()
    
    for i in range(1, 6):
        if i not in freq_data.columns:
            freq_data[i] = 0.0
    freq_data = freq_data.sort_index(axis=1)
    
    # Prepare data for plotly
    freq_data_reset = freq_data.reset_index()
    freq_data_reset.columns = [t["survey_item"]] + [str(i) for i in range(1, 6)]
    
    fig_stacked = go.Figure()
    colors_list = px.colors.sequential.RdBu
    
    for i, col in enumerate([str(j) for j in range(1, 6)]):
        fig_stacked.add_trace(go.Bar(
            name=RESPONSE_LABELS[i+1],
            x=freq_data_reset[t["survey_item"]],
            y=freq_data_reset[col],
            text=freq_data_reset[col].round(1),
            textposition='inside',
            hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
        ))
    
    fig_stacked.update_layout(
        barmode='stack',
        title=t["stacked_chart"].replace("#### ", ""),
        xaxis_title=t["survey_item"],
        yaxis_title=t["percentage"],
        height=500,
        legend_title=t["response_score"]
    )
    
    st.plotly_chart(fig_stacked, width='stretch')

# ------------------ TAB ASSOCIATION ------------------
with tab_assoc:
    st.markdown(f"{t['assoc_result']} ({assoc_method})")

    if assoc_stats["type"] == "correlation":
        st.markdown(f"{t['result_corr']} {assoc_stats['method']}")
        
        corr_data = pd.DataFrame({
            "Metric": [t["corr_coef"], t["p_value"], t["direction"], t["strength"], t["significance"]],
            "Value": [
                f"{assoc_stats['r']:.3f}", 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['direction'].capitalize(), 
                assoc_stats['strength'].capitalize(), 
                assoc_stats['signif_text'].capitalize()
            ]
        }).set_index("Metric")
        
        st.dataframe(corr_data, width='stretch')

        st.markdown(t["interpretation"])
        st.success(assoc_summary_text)

        st.markdown("---")
        st.markdown(t["visual_check"])
        
        # Calculate regression line
        z = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(valid_xy["X_total"].min(), valid_xy["X_total"].max(), 100)
        y_line = p(x_line)
        
        # Interactive scatterplot with regression line
        fig_assoc = px.scatter(
            valid_xy,
            x="X_total",
            y="Y_total",
            labels={
                'X_total': t["x_total_score"],
                'Y_total': t["y_total_score"]
            },
            title=f"Scatterplot (r={assoc_stats['r']:.3f})",
            color="X_total",
            color_continuous_scale='Plasma'
        )
        
        # Add regression line
        fig_assoc.add_trace(
            go.Scatter(
                x=x_line,
                y=y_line,
                mode='lines',
                name=t["regression_line"],
                line=dict(color='red', dash='dash', width=2)
            )
        )
        
        fig_assoc.update_layout(height=500)
        st.plotly_chart(fig_assoc, width='stretch')

    elif assoc_stats["type"] == "chi-square":
        st.markdown(f"{t['chi_result']} {assoc_stats['x']} dan {assoc_stats['y']}")
        
        chi_data = pd.DataFrame({
            "Metric": [t["chi_value"], t["dof"], t["p_value"], t["significance"]],
            "Value": [
                f"{assoc_stats['chi2']:.3f}", 
                assoc_stats['dof'], 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['signif_text'].capitalize()
            ]
        }).set_index("Metric")
        
        st.dataframe(chi_data, width='stretch')
        st.markdown(t["interpretation"])
        st.success(assoc_summary_text)
        
        st.markdown("---")
        st.markdown(t["contingency"])
        contingency = pd.crosstab(df[assoc_stats['x']], df[assoc_stats['y']])
        st.dataframe(contingency, width='stretch')

    else:
        st.warning(t["select_method"])

# ------------------ TAB PDF REPORT ------------------
with tab_pdf:
    st.markdown(t["pdf_export"])

    pdf_filename = st.text_input(
        t["pdf_filename"],
        value=""
    )
    
    st.markdown("---")
    st.write(t["pdf_layout"])
    cols_per_row = st.radio(
        t["charts_per_row"],
        options=[1],
        index=0,
        horizontal=True
    )
    
    st.markdown("---")
    st.write(t["select_content"])

    include_items = st.checkbox(t["include_items"], value=True)
    include_comp = st.checkbox(t["include_comp"], value=True)
    include_corr = st.checkbox(t["include_corr"], value=True)
    include_demo = st.checkbox(t["include_demo"], value=True)
    include_normality = st.checkbox(t["include_normality"], value=True)
    
    st.markdown("---")
    st.markdown(t["visualizations_pdf"])
    
    include_freq_plot = st.checkbox(t["include_freq"], value=True)
    include_stacked_plot = st.checkbox(t["include_stacked"], value=True)
    include_hist_x_plot = st.checkbox(t["include_hist_x"], value=True)
    include_hist_y_plot = st.checkbox(t["include_hist_y"], value=True)
    include_scatter_plot = st.checkbox(t["include_scatter"], value=True)
    include_age_plot = st.checkbox(t["include_age"], value=True)

    if st.button(t["generate_pdf"]):
        styles = getSampleStyleSheet()
        story = []
        temp_imgs = []

        safe_filename = "".join(c for c in pdf_filename if c.isalnum() or c in (' ', '_')).rstrip()
        final_filename = (safe_filename if safe_filename else "Laporan_Analisis") + ".pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        
        def add_table(title, df_table):
            story.append(Paragraph(title, styles["Heading3"]))
            df_reset = df_table.reset_index()
            table_data = [df_reset.columns.tolist()] + df_reset.values.tolist()
            tbl = Table(table_data)
            tbl.setStyle(
                TableStyle([
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ])
            )
            story.append(tbl)
            story.append(Spacer(1, 10))
            
        def add_plot_to_list(fig, title_text, temp_list, width, height):
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_file.name, bbox_inches="tight")
            plt.close(fig)
            temp_list.append(tmp_file.name)
            return {'title': title_text, 'file': tmp_file.name, 'width': width, 'height': height}
        
        story.append(Paragraph("Survey Analysis Report", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("FOMO & Social Media Addiction – Statistics 1 (Group 3)", styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Group Members:", styles["Heading3"]))
        story.append(Paragraph("- Delon Raphael Andianto (004202200050)<br/>- Kallista Viasta (004202200039)<br/>- Nabila Putri Amalia (004202200049)<br/>- Pingkan R G Lumingkewas (004202200035)", styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Data Cleaning (Age Filter & Grouping):", styles["Heading3"]))
        story.append(Paragraph("Only respondents whose age category was 13–18 years, 19–23 years, or 24–28 years were included in the analysis to represent Generation Z. Other age categories such as below 13 or above 28 years were excluded.", styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Respondents before cleaning: {before_clean}<br/>Respondents after cleaning: {after_clean}<br/>Removed respondents: {before_clean - after_clean}", styles["Normal"]))
        story.append(Spacer(1, 12))

        if include_normality: add_table("Normality Test (Shapiro–Wilk)", result_norm)
        if include_demo: 
            add_table("Demographic Summary – Age Group", age_demo_df)
            if gender_demo_df is not None: add_table("Demographic Summary – Gender", gender_demo_df)
        if include_items: add_table("Descriptive Statistics – Selected Items", desc_items)
        if include_comp: add_table("Descriptive Statistics – Composite Scores (X_total & Y_total)", desc_comp)
        if include_corr:
            story.append(Paragraph("Association Analysis Summary", styles["Heading3"]))
            story.append(Paragraph(assoc_summary_text, styles["Normal"]))
            story.append(Spacer(1, 10))

        if cols_per_row == 1:
            plot_width = 450
            plot_height = 300
            
        effective_page_width = 500.0
        col_unit_width = effective_page_width / cols_per_row
        image_render_width = col_unit_width * 0.95
        
        plots_to_render = []
        
        if include_age_plot:
            fig_pdf_age, ax_pdf_age = plt.subplots(figsize=(8, 5))
            age_counts.plot(kind='bar', ax=ax_pdf_age, color='skyblue', edgecolor='black')
            ax_pdf_age.set_title("Distribution of Respondents by Age Group")
            ax_pdf_age.set_xlabel("Age Group")
            ax_pdf_age.set_ylabel("Frequency")
            ax_pdf_age.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plots_to_render.append(add_plot_to_list(fig_pdf_age, "Demographic – Age Group", temp_imgs, 400, 300))

        if include_freq_plot:
            all_items = x_items + y_items
            for var in all_items:
                fig_pdf_bar, ax_pdf_bar = plt.subplots(figsize=(6, 4))
                s_freq = df[var].dropna()
                freq = s_freq.value_counts().sort_index()
                ax_pdf_bar.bar(freq.index.astype(str), freq.values)
                ax_pdf_bar.set_xlabel(var)
                ax_pdf_bar.set_ylabel("Frequency")
                ax_pdf_bar.set_title(f"Frequency of {var}")
                plots_to_render.append(add_plot_to_list(fig_pdf_bar, f"Freq. – {var}", temp_imgs, plot_width, plot_height))
                
        if include_stacked_plot:
            all_items = x_items + y_items
            freq_data = df[all_items].apply(lambda x: x.value_counts(normalize=True)).T * 100
            freq_data = freq_data.fillna(0).sort_index()

            for i in range(1, 6):
                if i not in freq_data.columns:
                    freq_data[i] = 0.0
            freq_data = freq_data.sort_index(axis=1)

            fig_stacked, ax_stacked = plt.subplots(figsize=(10, 6))
            freq_data.plot(kind='bar', stacked=True, ax=ax_stacked, 
                           color=plt.cm.RdYlBu(np.linspace(0.1, 0.9, 5)))
            
            ax_stacked.set_title("Response Percentage Across All Items (X & Y)")
            ax_stacked.set_xlabel("Survey Item")
            ax_stacked.set_ylabel("Percentage (%)")
            ax_stacked.legend(title="Response Score", bbox_to_anchor=(1.05, 1), loc='upper left')
            ax_stacked.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            plots_to_render.append(add_plot_to_list(fig_stacked, "Stacked Bar Chart (X & Y Items)", temp_imgs, 400, 300))

        if include_hist_x_plot:
            fig_pdf_hist_x, ax_pdf_hist_x = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["X_total"].dropna()
            ax_pdf_hist_x.hist(d_hist, bins=5, edgecolor="black", color='lightcoral')
            ax_pdf_hist_x.set_title("Histogram X_total (FOMO)")
            ax_pdf_hist_x.set_xlabel("X_total Score (FOMO)")
            ax_pdf_hist_x.set_ylabel("Frequency")
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_x, "Histogram X_total", temp_imgs, plot_width, plot_height))
            
        if include_hist_y_plot:
            fig_pdf_hist_y, ax_pdf_hist_y = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["Y_total"].dropna()
            ax_pdf_hist_y.hist(d_hist, bins=5, edgecolor="black", color='lightgreen')
            ax_pdf_hist_y.set_title("Histogram Y_total (Addiction)")
            ax_pdf_hist_y.set_xlabel("Y_total Score (Addiction)")
            ax_pdf_hist_y.set_ylabel("Frequency")
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_y, "Histogram Y_total", temp_imgs, plot_width, plot_height))

        if include_scatter_plot:
            fig_pdf_sc, ax_pdf_sc = plt.subplots(figsize=(6, 4))
            ax_pdf_sc.scatter(valid_xy["X_total"], valid_xy["Y_total"])
            ax_pdf_sc.set_xlabel("X_total (FOMO)")
            ax_pdf_sc.set_ylabel("Y_total (Social media addiction)")
            ax_pdf_sc.set_title("Scatterplot X_total vs Y_total")
            plots_to_render.append(add_plot_to_list(fig_pdf_sc, "Scatterplot X vs Y", temp_imgs, plot_width, plot_height))

        if plots_to_render:
            story.append(Paragraph("Visualizations", styles["Heading2"]))
            
            rows = []
            
            for i in range(0, len(plots_to_render), cols_per_row):
                row_plots = plots_to_render[i:i + cols_per_row]
                
                title_row = [Paragraph(p['title'], styles['Normal']) for p in row_plots]
                
                image_row = []
                for p in row_plots:
                    img = RLImage(p['file'], width=image_render_width)
                    image_row.append(img)
                
                if len(row_plots) < cols_per_row:
                    diff = cols_per_row - len(row_plots)
                    for _ in range(diff):
                        title_row.append(Paragraph("", styles['Normal']))
                        image_row.append(Spacer(1, 1))
                
                rows.append(title_row)
                rows.append(image_row)
            
            col_widths = [col_unit_width] * cols_per_row
            tbl = Table(rows, colWidths=col_widths)
            tbl.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 10))

        try:
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            
            st.download_button(
                t["download_pdf"],
                data=pdf_bytes,
                file_name=final_filename, 
                mime="application/pdf",
            )
            st.success(t["pdf_success"].format(final_filename))
            
        except Exception as e:
            st.error(t["pdf_error"].format(e))
            
        finally:
            for path in temp_imgs:
                try:
                    os.remove(path)
                except OSError:
                    pass