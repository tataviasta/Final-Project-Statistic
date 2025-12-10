import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
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

# --- DICTIONARY BAHASA (Dual Language Strings) ---
LANG_STRINGS = {
    "en": {
        "page_title": "FOMO & Social Media Addiction – Group 3",
        "app_title": "📊 The Relationship between Fear of Missing Out (FOMO) and Social Media Addiction among Generation Z",
        "caption": "Statistics 1 • Class 1",
        "sidebar_header": "👥 Group Members",
        "section_1_title": "1. Upload Dataset",
        "upload_label": "Upload a CSV or Excel file:",
        "upload_info": "Please upload the dataset first.",
        "preview_data": "Preview data (The first 5 lines, before age cleaning):",
        "col_names_expander": "See all column names (headers):",
        "age_col_detected": "Age column detected as: **{}**",
        "age_col_error": "Age column not found. Make sure there is a column named containing 'Age' or 'Umur'.",
        "clean_success": "✅ Data cleaning & age grouping completed.",
        "clean_summary": "**Data Cleaning Summary:**",
        "before_clean": "- Respondents before cleaning: {}",
        "after_clean": "- Respondents after cleaning (13–28 years group only): {}",
        "removed": "- Removed respondents: {}",
        "age_dist_header": "**Age Group Distribution:**",
        "respondent_col": "Number of respondents",
        "preview_after_clean": "Preview data after cleaning & age grouping:",
        "missing_x_y_error": "Some question columns were not found.",
        "missing_x": "Missing FOMO (X): {}",
        "missing_y": "Missing Addiction (Y): {}",
        "safe_change_header": "The safest way: change the headers in Excel/Sheets to X1..X5 and Y1..Y5, then re-upload.",
        "current_header": "Current Headers:",
        "section_2_title": "2. Select Variables X and Y (fixed item set)",
        "x_label": "FOMO (X) – Items Choose:",
        "x_help": "Just X1–X5 (Like Questionnaire).",
        "x_selected": "**Selected FOMO items:**",
        "y_label": "Social Media Addiction (Y) – Items Choose:",
        "y_help": "Just Y1–Y5 (Like Questionnaire).",
        "y_selected": "**Selected Addiction items:**",
        "min_items_warning": "Minimum Choose 1 item X and 1 item Y.",
        "section_3_title": "3. Composite Scores (X_total & Y_total)",
        "comp_method_label": "Composite score method:",
        "comp_mean": "Mean of items (recommended)",
        "comp_sum": "Sum of items",
        "comp_success": "✅ Composite scores X_total and Y_total have been successfully created.",
        "normality_title": "Normality Test (Shapiro–Wilk)",
        "normality_result": "### Result:",
        "normality_recommendation": "✅ Recommended association method based on normality test: **{}**",
        "valid_resp_metric": "Valid respondents (after age filter)",
        "avg_fomo_metric": "Average FOMO (X_total)",
        "avg_addiction_metric": "Average Addiction (Y_total)",
        "section_4_title": "4. Association Analysis – Choose One Method",
        "assoc_method_label": "Association method for X and Y (based on normality recommendation):",
        "pearson_corr": "Pearson Correlation",
        "spearman_corr": "Spearman Rank Correlation",
        "chi_square_test": "Chi-square Test (categorical X & Y)",
        "chi_square_note": "**Chi-square Test – select categorical X and Y (Likert).**",
        "chi_x_label": "Categorical X variable:",
        "chi_y_label": "Categorical Y variable:",
        "corr_table_metric": ["Correlation Coefficient (r)", "p-value", "Direction", "Strength", "Significance"],
        "corr_table_direction_pos": "Positive",
        "corr_table_direction_neg": "Negative",
        "corr_table_strength_vweak": "Very Weak",
        "corr_table_strength_weak": "Weak",
        "corr_table_strength_mod": "Moderate",
        "corr_table_strength_strong": "Strong",
        "corr_table_strength_vstrong": "Very Strong",
        "corr_table_signif_sig": "Significant (p < 0.05)",
        "corr_table_signif_ns": "Not Significant (p ≥ 0.05)",
        "corr_interpretation": "#### Interpretation:",
        "corr_summary": "Using the {} correlation, there is a {} and {} relationship between FOMO (X_total) and social media addiction (Y_total), with r = {:.3f} and p = {:.4f}, indicating that the association is {}.",
        "scatter_title": "Visual Check: Scatterplot",
        "chi_table_metric": ["Chi-square Value ($\\chi^2$)", "Degrees of Freedom (dof)", "p-value", "Significance"],
        "contingency_table": "#### Contingency Table",
        "chi_summary": "Using the Chi-square test between {} and {}, the chi-square statistic is $\chi^2$ = {:.3f} with {} degrees of freedom and p = {:.4f}, indicating that the association is {}.",
        "choose_assoc_warning": "Please select an association method in section **4. Association Analysis** above.",
        "tab_desc_title": "📋 Descriptive Statistics",
        "tab_vis_title": "📈 Visualizations",
        "tab_assoc_title": "🔗 Analysis Result",
        "tab_pdf_title": "📄 PDF Report",
        "desc_50_title": "### 5.0 Demographic Summary",
        "desc_age_dist": "**Age Group Distribution**",
        "desc_gender_dist": "**Gender Distribution**",
        "desc_gender_info": "Gender column was not detected, so gender distribution is not shown.",
        "desc_51_title": "### 5.1 Descriptive Statistics – Each Survey Item",
        "desc_52_title": "### 5.2 Descriptive Statistics – Composite Scores (X_total & Y_total)",
        "desc_53_title": "### 5.3 Frequency & Percentage Table (All X and Y Items)",
        "desc_freq_caption": "The table shows the frequency distribution for each questionnaire item X1 to Y5. Graphs are available in the '📈 Visualizations' tab.",
        "freq_item_header": "#### Result for Item: **{}**",
        "likert_note": "Note: STS=Strongly Disagree, SS=Strongly Agree.",
        "desc_assoc_title": "### 7. Association Analysis ({})",
        "desc_corr_result": "#### Result {} Correlation",
        "desc_chi_result": "#### Result Chi-square Test between {} and {}",
        "section_8_title": "### 8. Export PDF Report",
        "pdf_filename_label": "The name of the PDF file to be downloaded (without .pdf):",
        "pdf_vis_setting": "**Visualization Layout Settings in PDF:**",
        "pdf_cols_per_row": "Number of Plots per Row:",
        "pdf_content_select": "Select content to be included in the PDF:",
        "pdf_include_items": "Descriptive statistics – items (X & Y)",
        "pdf_include_comp": "Descriptive statistics – composite scores (X_total & Y_total)",
        "pdf_include_corr": "Association analysis summary",
        "pdf_include_demo": "Demographic summary (Age & Gender)",
        "pdf_include_normality": "Normality test result (Shapiro–Wilk)",
        "pdf_visualizations": "**Visualizations**",
        "pdf_include_freq_plot": "Frequency bar charts (All X and Y items)",
        "pdf_include_stacked_plot": "Stacked Bar Chart (All Item Response Percentage)",
        "pdf_include_hist_x_plot": "Histogram X_total",
        "pdf_include_hist_y_plot": "Histogram Y_total",
        "pdf_include_scatter_plot": "Scatterplot X_total vs Y_total",
        "pdf_include_age_plot": "Demographic bar chart (Age Group)",
        "pdf_button": "Generate PDF Report",
        "pdf_title_report": "Survey Analysis Report",
        "pdf_title_group": "FOMO & Social Media Addiction – Statistics 1 (Group 3)",
        "pdf_member_title": "Group Members:",
        "pdf_clean_title": "Data Cleaning (Age Filter & Grouping):",
        "pdf_clean_desc": "Only respondents whose age category was 13–18 years, 19–23 years, or 24–28 years were included in the analysis to represent Generation Z. Other age categories such as below 13 or above 28 years were excluded.",
        "pdf_clean_summary": "Respondents before cleaning: {}<br/>Respondents after cleaning: {}<br/>Removed respondents: {}",
        "pdf_table_normality": "Normality Test (Shapiro–Wilk)",
        "pdf_table_demo_age": "Demographic Summary – Age Group",
        "pdf_table_demo_gender": "Demographic Summary – Gender",
        "pdf_table_desc_items": "Descriptive Statistics – Selected Items",
        "pdf_table_desc_comp": "Descriptive Statistics – Composite Scores (X_total & Y_total)",
        "pdf_table_assoc": "Association Analysis Summary",
        "pdf_vis_title": "Visualizations",
        "pdf_download_button": "Download PDF Report",
        "pdf_success": "✅ PDF Report '{}' successfully created and ready for download.",
        "pdf_error": "Failed to build PDF. Make sure all plots fit on the page (Try changing 'Number of Plots per Row' to 1 or 2). Error Details: {}",
        "plot_age_title": "Distribution of Respondents by Age Group",
        "plot_age_x": "Age Group",
        "plot_age_y": "Frequency",
        "plot_hist_x_title": "Histogram of X_total (FOMO)",
        "plot_hist_x_x": "X_total Score (FOMO)",
        "plot_hist_y_title": "Histogram of Y_total (Social Media Addiction)",
        "plot_hist_y_y": "Y_total Score (Addiction)",
        "plot_scatter_title": "Scatterplot X_total vs Y_total",
        "plot_scatter_x": "X_total (FOMO)",
        "plot_scatter_y": "Y_total (Social media addiction)",
        "plot_bar_title": "Frequency of {}",
        "plot_bar_x": "{}",
        "plot_bar_y": "Frequency",
        "plot_download": "Download {} Bar Chart as PNG",
        "plot_stack_title": "Response Percentage Across All Items (X & Y)",
        "plot_stack_x": "Survey Item",
        "plot_stack_y": "Percentage (%)",
        "plot_stack_legend": "Response Score",
        "pdf_age_plot_title": "Demographic – Age Group",
        "pdf_freq_plot_title": "Freq. – {}",
        "pdf_stack_plot_title": "Stacked Bar Chart (X & Y Items)",
        "pdf_hist_x_plot_title": "Histogram X_total",
        "pdf_hist_y_plot_title": "Histogram Y_total",
        "pdf_scatter_plot_title": "Scatterplot X vs Y",
    },
    "id": {
        "page_title": "FOMO & Adiksi Media Sosial – Kelompok 3",
        "app_title": "📊 Hubungan antara Fear of Missing Out (FOMO) dan Adiksi Media Sosial pada Generasi Z",
        "caption": "Statistika 1 • Kelas 1",
        "sidebar_header": "👥 Anggota Kelompok",
        "section_1_title": "1. Unggah Dataset",
        "upload_label": "Unggah file CSV atau Excel:",
        "upload_info": "Silakan unggah dataset terlebih dahulu.",
        "preview_data": "Pratinjau data (5 baris pertama, sebelum pembersihan umur):",
        "col_names_expander": "Lihat semua nama kolom (header):",
        "age_col_detected": "Kolom usia terdeteksi sebagai: **{}**",
        "age_col_error": "Kolom usia tidak ditemukan. Pastikan ada kolom dengan nama mengandung 'Age' atau 'Umur'.",
        "clean_success": "✅ Pembersihan data & pengelompokan usia selesai.",
        "clean_summary": "**Ringkasan Pembersihan Data:**",
        "before_clean": "- Responden sebelum pembersihan: {}",
        "after_clean": "- Responden setelah pembersihan (hanya kelompok usia 13–28 tahun): {}",
        "removed": "- Responden dihapus: {}",
        "age_dist_header": "**Distribusi Kelompok Usia:**",
        "respondent_col": "Jumlah responden",
        "preview_after_clean": "Pratinjau data setelah pembersihan & pengelompokan usia:",
        "missing_x_y_error": "Beberapa kolom pertanyaan tidak ditemukan.",
        "missing_x": "FOMO (X) Hilang: {}",
        "missing_y": "Adiksi (Y) Hilang: {}",
        "safe_change_header": "Cara paling aman: ubah header di Excel/Sheets jadi X1..X5 dan Y1..Y5, lalu unggah ulang.",
        "current_header": "Header saat ini:",
        "section_2_title": "2. Pilih Variabel X dan Y (set item tetap)",
        "x_label": "FOMO (X) – Pilih Item:",
        "x_help": "Hanya X1–X5 (Sesuai Kuesioner).",
        "x_selected": "**Item FOMO yang Dipilih:**",
        "y_label": "Adiksi Media Sosial (Y) – Pilih Item:",
        "y_help": "Hanya Y1–Y5 (Sesuai Kuesioner).",
        "y_selected": "**Item Adiksi yang Dipilih:**",
        "min_items_warning": "Minimal Pilih 1 item X dan 1 item Y.",
        "section_3_title": "3. Skor Komposit (X_total & Y_total)",
        "comp_method_label": "Metode skor komposit:",
        "comp_mean": "Rata-rata item (direkomendasikan)",
        "comp_sum": "Jumlah item",
        "comp_success": "✅ Skor komposit X_total dan Y_total berhasil dibuat.",
        "normality_title": "Uji Normalitas (Shapiro–Wilk)",
        "normality_result": "### Hasil:",
        "normality_recommendation": "✅ Metode asosiasi yang direkomendasikan berdasarkan uji normalitas: **{}**",
        "valid_resp_metric": "Responden valid (setelah filter usia)",
        "avg_fomo_metric": "Rata-rata FOMO (X_total)",
        "avg_addiction_metric": "Rata-rata Adiksi (Y_total)",
        "section_4_title": "4. Analisis Asosiasi – Pilih Satu Metode",
        "assoc_method_label": "Metode asosiasi untuk X dan Y (berdasarkan rekomendasi normalitas):",
        "pearson_corr": "Korelasi Pearson",
        "spearman_corr": "Korelasi Rank Spearman",
        "chi_square_test": "Uji Chi-square (X & Y kategorik)",
        "chi_square_note": "**Uji Chi-square – pilih X dan Y kategorik (Likert).**",
        "chi_x_label": "Variabel X Kategorik:",
        "chi_y_label": "Variabel Y Kategorik:",
        "corr_table_metric": ["Koefisien Korelasi (r)", "nilai-p", "Arah", "Kekuatan", "Signifikansi"],
        "corr_table_direction_pos": "Positif",
        "corr_table_direction_neg": "Negatif",
        "corr_table_strength_vweak": "Sangat Lemah",
        "corr_table_strength_weak": "Lemah",
        "corr_table_strength_mod": "Sedang",
        "corr_table_strength_strong": "Kuat",
        "corr_table_strength_vstrong": "Sangat Kuat",
        "corr_table_signif_sig": "Signifikan (p < 0.05)",
        "corr_table_signif_ns": "Tidak Signifikan (p ≥ 0.05)",
        "corr_interpretation": "#### Interpretasi:",
        "corr_summary": "Menggunakan korelasi {}, terdapat hubungan {} dan {} antara FOMO (X_total) dan adiksi media sosial (Y_total), dengan r = {:.3f} dan p = {:.4f}, menunjukkan bahwa asosiasi tersebut {} ({}).",
        "scatter_title": "Pemeriksaan Visual: Scatterplot",
        "chi_table_metric": ["Nilai Chi-square ($\\chi^2$)", "Derajat Kebebasan (dof)", "nilai-p", "Signifikansi"],
        "contingency_table": "#### Tabel Kontingensi",
        "chi_summary": "Menggunakan Uji Chi-square antara {} dan {}, nilai statistik chi-square adalah $\chi^2$ = {:.3f} dengan {} derajat kebebasan dan p = {:.4f}, menunjukkan bahwa asosiasi tersebut {}.",
        "choose_assoc_warning": "Silakan pilih metode asosiasi di bagian **4. Analisis Asosiasi** di atas.",
        "tab_desc_title": "📋 Statistik Deskriptif",
        "tab_vis_title": "📈 Visualisasi",
        "tab_assoc_title": "🔗 Hasil Analisis",
        "tab_pdf_title": "📄 Laporan PDF",
        "desc_50_title": "### 5.0 Ringkasan Demografi",
        "desc_age_dist": "**Distribusi Kelompok Usia**",
        "desc_gender_dist": "**Distribusi Jenis Kelamin**",
        "desc_gender_info": "Kolom Jenis Kelamin tidak terdeteksi, jadi distribusi jenis kelamin tidak ditampilkan.",
        "desc_51_title": "### 5.1 Statistik Deskriptif – Setiap Item Kuesioner",
        "desc_52_title": "### 5.2 Statistik Deskriptif – Skor Komposit (X_total & Y_total)",
        "desc_53_title": "### 5.3 Tabel Frekuensi & Persentase (Semua Item X dan Y)",
        "desc_freq_caption": "Tabel menunjukkan distribusi frekuensi untuk setiap item kuesioner X1 hingga Y5. Grafik tersedia di tab '📈 Visualisasi'.",
        "freq_item_header": "#### Hasil untuk Item: **{}**",
        "likert_note": "Keterangan: STS=Sangat Tidak Setuju, SS=Sangat Setuju.",
        "desc_assoc_title": "### 7. Analisis Asosiasi ({})",
        "desc_corr_result": "#### Hasil Korelasi {}",
        "desc_chi_result": "#### Hasil Uji Chi-square antara {} dan {}",
        "section_8_title": "### 8. Ekspor Laporan PDF",
        "pdf_filename_label": "Nama file PDF yang akan diunduh (tanpa .pdf):",
        "pdf_vis_setting": "**Pengaturan Tata Letak Visualisasi dalam PDF:**",
        "pdf_cols_per_row": "Jumlah Grafik per Baris:",
        "pdf_content_select": "Pilih konten yang ingin dimasukkan ke PDF:",
        "pdf_include_items": "Statistik deskriptif – item (X & Y)",
        "pdf_include_comp": "Statistik deskriptif – skor komposit (X_total & Y_total)",
        "pdf_include_corr": "Ringkasan analisis asosiasi",
        "pdf_include_demo": "Ringkasan demografi (Usia & Jenis Kelamin)",
        "pdf_include_normality": "Hasil uji normalitas (Shapiro–Wilk)",
        "pdf_visualizations": "**Visualisasi**",
        "pdf_include_freq_plot": "Diagram batang frekuensi (Semua item X dan Y)",
        "pdf_include_stacked_plot": "Diagram Batang Bertumpuk (Persentase Respon Semua Item)",
        "pdf_include_hist_x_plot": "Histogram X_total",
        "pdf_include_hist_y_plot": "Histogram Y_total",
        "pdf_include_scatter_plot": "Scatterplot X_total vs Y_total",
        "pdf_include_age_plot": "Diagram batang demografi (Kelompok Usia)",
        "pdf_button": "Hasilkan Laporan PDF",
        "pdf_title_report": "Laporan Analisis Survei",
        "pdf_title_group": "FOMO & Adiksi Media Sosial – Statistika 1 (Kelompok 3)",
        "pdf_member_title": "Anggota Kelompok:",
        "pdf_clean_title": "Pembersihan Data (Filter & Pengelompokan Usia):",
        "pdf_clean_desc": "Hanya responden dengan kategori usia 13–18 tahun, 19–23 tahun, atau 24–28 tahun yang dimasukkan dalam analisis untuk mewakili Generasi Z. Kategori usia lain seperti di bawah 13 atau di atas 28 tahun dikeluarkan.",
        "pdf_clean_summary": "Responden sebelum pembersihan: {}<br/>Responden setelah pembersihan: {}<br/>Responden dihapus: {}",
        "pdf_table_normality": "Uji Normalitas (Shapiro–Wilk)",
        "pdf_table_demo_age": "Ringkasan Demografi – Kelompok Usia",
        "pdf_table_demo_gender": "Ringkasan Demografi – Jenis Kelamin",
        "pdf_table_desc_items": "Statistik Deskriptif – Item yang Dipilih",
        "pdf_table_desc_comp": "Statistik Deskriptif – Skor Komposit (X_total & Y_total)",
        "pdf_table_assoc": "Ringkasan Analisis Asosiasi",
        "pdf_vis_title": "Visualisasi",
        "pdf_download_button": "Unduh Laporan PDF",
        "pdf_success": "✅ Laporan PDF '{}' berhasil dibuat dan siap diunduh.",
        "pdf_error": "Gagal membangun PDF. Pastikan semua grafik muat di halaman (Coba ubah 'Jumlah Grafik per Baris' menjadi 1 atau 2). Detail Error: {}",
        "plot_age_title": "Distribusi Responden berdasarkan Kelompok Usia",
        "plot_age_x": "Kelompok Usia",
        "plot_age_y": "Frekuensi",
        "plot_hist_x_title": "Histogram X_total (FOMO)",
        "plot_hist_x_x": "Skor X_total (FOMO)",
        "plot_hist_y_title": "Histogram Y_total (Adiksi Media Sosial)",
        "plot_hist_y_y": "Skor Y_total (Adiksi)",
        "plot_scatter_title": "Scatterplot X_total vs Y_total",
        "plot_scatter_x": "X_total (FOMO)",
        "plot_scatter_y": "Y_total (Adiksi media sosial)",
        "plot_bar_title": "Frekuensi {}",
        "plot_bar_x": "{}",
        "plot_bar_y": "Frekuensi",
        "plot_download": "Unduh Diagram Batang {} sebagai PNG",
        "plot_stack_title": "Persentase Respon di Semua Item (X & Y)",
        "plot_stack_x": "Item Kuesioner",
        "plot_stack_y": "Persentase (%)",
        "plot_stack_legend": "Skor Respon",
        "pdf_age_plot_title": "Demografi – Kelompok Usia",
        "pdf_freq_plot_title": "Freq. – {}",
        "pdf_stack_plot_title": "Diagram Batang Bertumpuk (Item X & Y)",
        "pdf_hist_x_plot_title": "Histogram X_total",
        "pdf_hist_y_plot_title": "Histogram Y_total",
        "pdf_scatter_plot_title": "Scatterplot X vs Y",
    }
}

# ------------------------------------------------------------------
# CONFIGURASI BAHASA
# ------------------------------------------------------------------
st.sidebar.header("Language / Bahasa")
selected_lang = st.sidebar.radio(
    "Choose language / Pilih bahasa:",
    options=["English (EN)", "Bahasa Indonesia (ID)"],
    index=1,
)
lang_code = "id" if "Bahasa Indonesia" in selected_lang else "en"
T = LANG_STRINGS[lang_code]

# ------------------------------------------------------------------
# RESPONSE LABELS (TIDAK BERUBAH)
# ------------------------------------------------------------------
RESPONSE_LABELS = {
    1: "1 (STS: Sangat Tidak Setuju)",
    2: "2 (TS: Tidak Setuju)",
    3: "3 (N: Netral)",
    4: "4 (S: Setuju)",
    5: "5 (SS: Sangat Setuju)",
}

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title=T["page_title"],
    layout="wide"
)

st.title(T["app_title"])
st.caption(T["caption"])

# ------------------------------------------------------------------
# SIDEBAR – GROUP MEMBERS
# ------------------------------------------------------------------
st.sidebar.header(T["sidebar_header"])
st.sidebar.write("- Delon Raphael Andianto (004202200050)")
st.sidebar.write("- Kallista Viasta (004202200039)")
st.sidebar.write("- Nabila Putri Amalia (004202200049)")
st.sidebar.write("- Pingkan R G Lumingkewas (004202200035)")

# ------------------------------------------------------------------
# 1. UPLOAD DATASET
# ------------------------------------------------------------------
st.subheader(T["section_1_title"])

uploaded = st.file_uploader(
    T["upload_label"],
    type=["csv", "xlsx"]
)

if uploaded is None:
    st.info(T["upload_info"])
    st.stop()

if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

st.write(T["preview_data"])
st.dataframe(df.head())

with st.expander(T["col_names_expander"]):
    st.write(list(df.columns))

# ------------------------------------------------------------------
# 1A. DATA CLEANING – PAKAI KATEGORI UMUR 13–18 / 19–23 / 24–28
# --------------------------------------------------

# Deteksi kolom umur otomatis (mengandung 'age' atau 'umur')
AGE_COLUMN = None
for col in df.columns:
    col_lower = str(col).lower()
    if "age" in col_lower or "umur" in col_lower:
        AGE_COLUMN = col
        break

if AGE_COLUMN is None:
    st.error(T["age_col_error"])
    st.stop()

st.write(T["age_col_detected"].format(AGE_COLUMN))

# Nilai Age di file contoh: string kategori, misalnya:
allowed_age_categories = [
    "13–18 years / tahun",
    "19–23 years / tahun",
    "24–28 years / tahun",
    "13-18 years / tahun",
    "19-23 years / tahun",
    "24-28 years / tahun",
]

before_clean = len(df)

# Hanya ambil responden dengan Age di tiga kategori ini
df = df[df[AGE_COLUMN].isin(allowed_age_categories)]

after_clean = len(df)

# Buat kolom Age_Group sama dengan Age (sudah kategori)
df["Age_Group"] = df[AGE_COLUMN].astype("category")

st.success(T["clean_success"])
st.write(T["clean_summary"])
st.write(T["before_clean"].format(before_clean))
st.write(T["after_clean"].format(after_clean))
st.write(T["removed"].format(before_clean - after_clean))

st.write(T["age_dist_header"])
st.dataframe(df["Age_Group"].value_counts().rename(T["respondent_col"]))

st.write(T["preview_after_clean"])
st.dataframe(df.head())

# ------------------------------------------------------------------
# DEMOGRAPHIC SUMMARY (Age_Group + optional Gender)
# ------------------------------------------------------------------

# Summary Age_Group (frequency + percentage)
age_counts = df["Age_Group"].value_counts().sort_index()
age_demo_df = pd.DataFrame({
    "Age Group": age_counts.index,
    T["corr_table_metric"][0] if lang_code == "id" else "Frequency": age_counts.values, # Menggunakan string dari T
})
age_demo_df["Percentage (%)"] = (age_demo_df[age_demo_df.columns[1]] / age_demo_df[age_demo_df.columns[1]].sum() * 100).round(2)


# Deteksi kolom gender otomatis (optional)
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
        T["corr_table_metric"][0] if lang_code == "id" else "Gender": gender_counts.index, # Menggunakan string dari T
        T["corr_table_metric"][0] if lang_code == "id" else "Frequency": gender_counts.values,
    })
    gender_demo_df["Percentage (%)"] = (gender_demo_df[gender_demo_df.columns[1]] / gender_demo_df[gender_demo_df.columns[1]].sum() * 100).round(2)
    gender_demo_df.columns = ["Gender" if lang_code == "en" else "Jenis Kelamin", gender_demo_df.columns[1], "Percentage (%)"]

# ------------------------------------------------------------------
# 2. FIXED DEFINITIONS UNTUK X & Y (SESUIAI KUESIONER)
# ------------------------------------------------------------------
FOMO_LABELS = {
    "X1": "I feel anxious if I don't know the latest updates on social media.",
    "X2": "I feel the urge to constantly check social media to stay connected.",
    "X3": "I'm afraid of being left behind when others talk about trending topics.",
    "X4": "I feel the need to follow viral trends to stay “included”.",
    "X5": "I feel uncomfortable when I see others participating in activities that I am not part of.",
}

ADDICTION_LABELS = {
    "Y1": "I find it difficult to reduce the amount of time I spend on social media.",
    "Y2": "I prefer using social media over doing offline activities.",
    "Y3": "Social media usage disrupts my sleep, study time, or other important activities.",
    "Y4": "I often spend more time on social media than I originally planned.",
    "Y5": "I often open social media automatically without any clear purpose.",
}

fixed_x_all = list(FOMO_LABELS.keys())
fixed_y_all = list(ADDICTION_LABELS.keys())

# ------------------------------------------------------------------
# 2A. FLEXIBLE MAPPING HEADER → X1..Y5 (DARI TEKS PERTANYAAN)
# ------------------------------------------------------------------
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
    st.error(
        T["missing_x_y_error"] + "\n\n"
        + T["missing_x"].format(missing_x) + "\n"
        + T["missing_y"].format(missing_y) + "\n\n"
        + T["safe_change_header"]
    )
    st.write(T["current_header"], list(df.columns))
    st.stop()

# ------------------------------------------------------------------
# 3. PILIH SUBSET X & Y
# ------------------------------------------------------------------
st.subheader(T["section_2_title"])

cA, cB = st.columns(2)

with cA:
    x_items = st.multiselect(
        T["x_label"],
        options=fixed_x_all,
        default=fixed_x_all,
        help=T["x_help"],
    )
    st.markdown(T["x_selected"])
    for code in x_items:
        st.caption(f"**{code}** — {FOMO_LABELS[code]}")

with cB:
    y_items = st.multiselect(
        T["y_label"],
        options=fixed_y_all,
        default=fixed_y_all,
        help=T["y_help"],
    )
    st.markdown(T["y_selected"])
    for code in y_items:
        st.caption(f"**{code}** — {ADDICTION_LABELS[code]}")

if len(x_items) == 0 or len(y_items) == 0:
    st.warning(T["min_items_warning"])
    st.stop()

for col in x_items + y_items:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------------
# 4. COMPOSITE SCORES
# ------------------------------------------------------------------
st.subheader(T["section_3_title"])

comp_options = [T["comp_mean"], T["comp_sum"]]
comp_method = st.radio(
    T["comp_method_label"],
    comp_options,
    horizontal=True,
    index=comp_options.index(T["comp_mean"])
)

if comp_method.startswith(T["comp_mean"][:4]) or comp_method.startswith("Mean"):
    df["X_total"] = df[x_items].mean(axis=1)
    df["Y_total"] = df[y_items].mean(axis=1)
else:
    df["X_total"] = df[x_items].sum(axis=1)
    df["Y_total"] = df[y_items].sum(axis=1)

st.success(T["comp_success"])

valid_xy = df[["X_total", "Y_total"]].dropna()
n_valid = valid_xy.shape[0]
mean_x = valid_xy["X_total"].mean()
mean_y = valid_xy["Y_total"].mean()

# ------------------------------------------------------------------
# NORMALITY TEST (Shapiro–Wilk)
# ------------------------------------------------------------------

st.subheader(T["normality_title"])

shapiro_x = stats.shapiro(valid_xy["X_total"])
shapiro_y = stats.shapiro(valid_xy["Y_total"])

normal_x = "Normal" if shapiro_x.pvalue >= 0.05 else "Not Normal"
normal_y = "Normal" if shapiro_y.pvalue >= 0.05 else "Not Normal"

st.write(T["normality_result"])

result_norm = pd.DataFrame({
    "Variable": ["X_total", "Y_total"],
    "Shapiro-Wilk Statistic": [shapiro_x.statistic, shapiro_y.statistic],
    "p-value": [shapiro_x.pvalue, shapiro_y.pvalue],
    "Normality": [normal_x, normal_y]
})

st.dataframe(result_norm.round(4))

# Rekomendasi metode berdasarkan normality
if normal_x == "Normal" and normal_y == "Normal":
    recommended_method = T["pearson_corr"]
else:
    recommended_method = T["spearman_corr"]

st.info(T["normality_recommendation"].format(recommended_method))

m1, m2, m3 = st.columns(3)
m1.metric(T["valid_resp_metric"], n_valid)
m2.metric(T["avg_fomo_metric"], f"{mean_x:.2f}")
m3.metric(T["avg_addiction_metric"], f"{mean_y:.2f}")

# ------------------------------------------------------------------
# 5. HELPER – DESCRIPTIVE TABLE & BAR CHART ITEM
# ------------------------------------------------------------------
def descriptive_table(data: pd.DataFrame, cols):
    rows = []
    # Menggunakan nama kolom yang sesuai dengan bahasa
    col_names = {
        "Variable": "Variable",
        "N": "N",
        "Mean": "Mean" if lang_code == "en" else "Rata-rata",
        "Median": "Median",
        "Mode": "Mode",
        "Min": "Min",
        "Max": "Max",
        "Std Dev": "Std Dev" if lang_code == "en" else "Std Deviasi",
    }
    
    for col in cols:
        s = data[col].dropna()
        if s.empty:
            continue
        mode_vals = s.mode()
        mode_val = mode_vals.iloc[0] if not mode_vals.empty else np.nan
        rows.append(
            {
                col_names["Variable"]: col,
                col_names["N"]: len(s),
                col_names["Mean"]: s.mean(),
                col_names["Median"]: s.median(),
                col_names["Mode"]: mode_val,
                col_names["Min"]: s.min(),
                col_names["Max"]: s.max(),
                col_names["Std Dev"]: s.std(ddof=1),
            }
        )
    return pd.DataFrame(rows).set_index(col_names["Variable"]).round(3)


# NEW HELPER FUNCTION: To create and display individual bar charts
def create_item_bar_chart(df, col_name):
    # Dapatkan data frekuensi
    s_freq = df[col_name].dropna()
    freq = s_freq.value_counts().sort_index()

    if freq.empty:
        st.warning(f"No valid data found for {col_name}.")
        return
        
    # Buat figure
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(freq.index.astype(str), freq.values, color='lightgray', edgecolor='black')
    ax_bar.set_xlabel(col_name)
    ax_bar.set_ylabel(T["plot_bar_y"])
    ax_bar.set_title(T["plot_bar_title"].format(col_name))
    plt.tight_layout()
    
    # Tampilkan figure di Streamlit
    st.pyplot(fig_bar)

    # Simpan ke buffer untuk download
    buf_bar = io.BytesIO()
    fig_bar.savefig(buf_bar, format="png", bbox_inches="tight")
    buf_bar.seek(0)
    
    # Tampilkan tombol download
    st.download_button(
        T["plot_download"].format(col_name),
        data=buf_bar,
        file_name=f"{col_name}_bar_chart.png",
        mime="image/png",
    )
    plt.close(fig_bar) # Tutup figure untuk membebaskan memori

# ------------------------------------------------------------------
# 6. ASSOCIATION METHOD – CHOOSE ONE
# ------------------------------------------------------------------
st.subheader(T["section_4_title"])

assoc_options = [T["pearson_corr"], T["spearman_corr"], T["chi_square_test"]]
assoc_method = st.radio(
    T["assoc_method_label"],
    assoc_options,
    index=0,
)

assoc_stats = {}
assoc_summary_text = ""

if assoc_method == T["pearson_corr"] or assoc_method == T["spearman_corr"]:
    x_corr = valid_xy["X_total"]
    y_corr = valid_xy["Y_total"]

    if assoc_method == T["pearson_corr"]:
        r_value, p_value = stats.pearsonr(x_corr, y_corr)
        method_short = "Pearson"
    else:
        r_value, p_value = stats.spearmanr(x_corr, y_corr)
        method_short = "Spearman"

    def interpret_strength(r):
        a = abs(r)
        if a < 0.2:
            return T["corr_table_strength_vweak"]
        elif a < 0.4:
            return T["corr_table_strength_weak"]
        elif a < 0.6:
            return T["corr_table_strength_mod"]
        elif a < 0.8:
            return T["corr_table_strength_strong"]
        else:
            return T["corr_table_strength_vstrong"]

    direction = T["corr_table_direction_pos"] if r_value > 0 else T["corr_table_direction_neg"]
    strength = interpret_strength(r_value)
    signif_text = T["corr_table_signif_sig"] if p_value < 0.05 else T["corr_table_signif_ns"]
    
    # Ambil hanya teks Signifikan/Tidak Signifikan untuk summary ID
    signif_short_id = "signifikan" if p_value < 0.05 else "tidak signifikan"

    assoc_stats = {
        "type": "correlation",
        "method": method_short,
        "r": r_value,
        "p": p_value,
        "direction": direction,
        "strength": strength,
        "signif_text": signif_text,
    }

    if lang_code == "en":
        assoc_summary_text = (
            T["corr_summary"].format(method_short, direction.lower(), strength.lower(), 
                                     r_value, p_value, signif_text.lower())
        )
    else: # Bahasa Indonesia
        assoc_summary_text = (
            T["corr_summary"].format(method_short, direction.lower(), strength.lower(), 
                                     r_value, p_value, signif_short_id, signif_text)
        )


else: # Chi-Square
    st.markdown(T["chi_square_note"])
    cat_options = x_items + y_items
    chi_x_col = st.selectbox(T["chi_x_label"], cat_options, key="chi_x")
    chi_y_col = st.selectbox(T["chi_y_label"], cat_options, key="chi_y")

    contingency = pd.crosstab(df[chi_x_col], df[chi_y_col])
    chi2_value, p_chi, dof, expected = stats.chi2_contingency(contingency)
    signif_text = T["corr_table_signif_sig"] if p_chi < 0.05 else T["corr_table_signif_ns"]

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

    assoc_summary_text = (
        T["chi_summary"].format(chi_x_col, chi_y_col, chi2_value, dof, p_chi, signif_text.lower())
    )

# ------------------------------------------------------------------
# 7. TABS
# ------------------------------------------------------------------
# Pastikan age_counts sudah dihitung di bagian DEMOGRAPHIC SUMMARY

# Prepare Age Group Bar Chart (for tab_vis & pdf)
fig_age_bar, ax_age_bar = plt.subplots(figsize=(8, 5))
age_counts.plot(kind='bar', ax=ax_age_bar, color='skyblue', edgecolor='black')
ax_age_bar.set_title(T["plot_age_title"])
ax_age_bar.set_xlabel(T["plot_age_x"])
ax_age_bar.set_ylabel(T["plot_age_y"])
ax_age_bar.tick_params(axis='x', rotation=45)
plt.tight_layout()
buf_age_bar = io.BytesIO()
fig_age_bar.savefig(buf_age_bar, format="png", bbox_inches="tight")
buf_age_bar.seek(0)
# NOTE: fig_age_bar remains open until tab_vis/pdf needs it. (Don't close yet)

# Prepare X_total Histogram (for tab_vis & pdf)
fig_hist_x, ax_hist_x = plt.subplots()
ax_hist_x.hist(valid_xy["X_total"].dropna(), bins=5, edgecolor="black", color='lightcoral')
ax_hist_x.set_title(T["plot_hist_x_title"])
ax_hist_x.set_xlabel(T["plot_hist_x_x"])
ax_hist_x.set_ylabel(T["plot_age_y"]) # Frequency
# NOTE: fig_hist_x remains open

# Prepare Y_total Histogram (for tab_vis & pdf)
fig_hist_y, ax_hist_y = plt.subplots()
ax_hist_y.hist(valid_xy["Y_total"].dropna(), bins=5, edgecolor="black", color='lightgreen')
ax_hist_y.set_title(T["plot_hist_y_title"])
ax_hist_y.set_xlabel(T["plot_hist_y_y"])
ax_hist_y.set_ylabel(T["plot_age_y"]) # Frequency
# NOTE: fig_hist_y remains open

tab_desc, tab_vis, tab_assoc, tab_pdf = st.tabs(
    [T["tab_desc_title"], T["tab_vis_title"], T["tab_assoc_title"], T["tab_pdf_title"]]
)

# ------------------ TAB DESCRIPTIVES ------------------
with tab_desc:
    st.markdown(T["desc_50_title"])

    st.markdown(T["desc_age_dist"])
    st.dataframe(age_demo_df)

    if gender_demo_df is not None:
        st.markdown(T["desc_gender_dist"])
        st.dataframe(gender_demo_df)
    else:
        st.info(T["desc_gender_info"])

    st.markdown(T["desc_51_title"])
    desc_items = descriptive_table(df, x_items + y_items)
    st.dataframe(desc_items)

    st.markdown(T["desc_52_title"])
    desc_comp = descriptive_table(df, ["X_total", "Y_total"])
    st.dataframe(desc_comp)

#--------------- Frequency ---------------

    st.markdown(T["desc_53_title"])
    st.caption(T["desc_freq_caption"])

    all_items = x_items + y_items

    # Loop melalui semua item (X1 hingga Y5) untuk menampilkan TABEL saja
    for var_freq in all_items:
        st.markdown(T["freq_item_header"].format(var_freq))

        # 1. Hitung Frekuensi dan Persentase
        s_freq = df[var_freq].dropna()
        freq = s_freq.value_counts().sort_index()
        perc = (freq / freq.sum() * 100).round(2)
        # Ganti nama kolom 'Frequency' berdasarkan bahasa
        freq_table = pd.DataFrame({
            T["corr_table_metric"][0] if lang_code == "id" else "Frequency": freq, 
            "Percentage (%)": perc
        })

        # 2. Terapkan Mapping Label Likert
        if var_freq in (x_items + y_items):
            if freq_table.index.dtype in [int, float] and freq_table.index.max() <= 5: 
                labeled_index = freq_table.index.map(lambda x: RESPONSE_LABELS.get(x, x))
                freq_table.index = labeled_index
                st.caption(T["likert_note"])

        st.dataframe(freq_table)
        st.markdown("---") # Garis pemisah antar item (opsional)

# ------------------ TAB VISUALIZATION ------------------
with tab_vis:
    st.markdown("### Visualizations")
    
    # 1. Age Group Bar Chart
    st.markdown("#### Distribution of Respondents by Age Group")
    st.pyplot(fig_age_bar)
    plt.close(fig_age_bar)

    # 2. Histogram X_total
    st.markdown("#### Histogram of X_total (FOMO)")
    st.pyplot(fig_hist_x)
    plt.close(fig_hist_x)

    # 3. Histogram Y_total
    st.markdown("#### Histogram of Y_total (Social Media Addiction)")
    st.pyplot(fig_hist_y)
    plt.close(fig_hist_y)

    # 4. Scatterplot X vs Y
    if assoc_stats["type"] == "correlation":
        st.markdown("#### Scatterplot X_total vs Y_total")
        fig_vis_scatter, ax_vis_scatter = plt.subplots()
        ax_vis_scatter.scatter(valid_xy["X_total"], valid_xy["Y_total"], color='purple', alpha=0.6)
        m, b = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
        ax_vis_scatter.plot(valid_xy["X_total"], m*valid_xy["X_total"] + b, color='red', linestyle='--')
        ax_vis_scatter.set_xlabel(T["plot_scatter_x"])
        ax_vis_scatter.set_ylabel(T["plot_scatter_y"])
        ax_vis_scatter.set_title(T["plot_scatter_title"])
        st.pyplot(fig_vis_scatter)
        plt.close(fig_vis_scatter)

    # 5. Frequency Bar Charts for each item
    st.markdown("#### Frequency Bar Charts for Each Item (X1–Y5)")
    for var in all_items:
        create_item_bar_chart(df, var)


# --- Test Result/analysis ------

with tab_assoc:
    st.markdown(T["desc_assoc_title"].format(assoc_method))

    if assoc_stats["type"] == "correlation":
        st.markdown(T["desc_corr_result"].format(assoc_stats['method']))
        
        # Tampilkan tabel ringkasan
        corr_data = pd.DataFrame({
            "Metric": T["corr_table_metric"],
            "Value": [
                f"{assoc_stats['r']:.3f}", 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['direction'], 
                assoc_stats['strength'], 
                assoc_stats['signif_text']
            ]
        }).set_index("Metric")
        
        st.dataframe(corr_data)

        # Tampilkan interpretasi teks
        st.markdown(T["corr_interpretation"])
        st.success(assoc_summary_text)

        # Tambahkan visualisasi scatterplot 
        st.markdown("---")
        st.markdown(T["scatter_title"])
        
        # Buat ulang scatterplot untuk ditampilkan di tab analisis ini
        fig_assoc_scatter, ax_assoc_scatter = plt.subplots()
        ax_assoc_scatter.scatter(valid_xy["X_total"], valid_xy["Y_total"], color='purple', alpha=0.6)
        
        # Tambahkan garis regresi
        m, b = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
        ax_assoc_scatter.plot(valid_xy["X_total"], m*valid_xy["X_total"] + b, color='red', linestyle='--')
        
        ax_assoc_scatter.set_xlabel(T["plot_scatter_x"])
        ax_assoc_scatter.set_ylabel(T["plot_scatter_y"])
        ax_assoc_scatter.set_title(f"Scatterplot (r={assoc_stats['r']:.3f})")
        st.pyplot(fig_assoc_scatter)
        plt.close(fig_assoc_scatter)

    elif assoc_stats["type"] == "chi-square":
        st.markdown(T["desc_chi_result"].format(assoc_stats['x'], assoc_stats['y']))
        
        chi_data = pd.DataFrame({
            "Metric": T["chi_table_metric"],
            "Value": [
                f"{assoc_stats['chi2']:.3f}", 
                assoc_stats['dof'], 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['signif_text']
            ]
        }).set_index("Metric")
        
        st.dataframe(chi_data)
        st.markdown(T["corr_interpretation"])
        st.success(assoc_summary_text)
        
        st.markdown("---")
        st.markdown(T["contingency_table"])
        contingency = pd.crosstab(df[assoc_stats['x']], df[assoc_stats['y']])
        st.dataframe(contingency)

    else:
        st.warning(T["choose_assoc_warning"])

# ------------------ TAB PDF REPORT (FINAL MODIFIED VERSION) ------------------
with tab_pdf:
    st.markdown(T["section_8_title"])

    # 1. INPUT NAMA FILE
    pdf_filename = st.text_input(
        T["pdf_filename_label"],
        value="Laporan_Analisis" if lang_code == "id" else "Analysis_Report"
    )
    
    # 2. PILIHAN JUMLAH GRAFIK HORIZONTAL
    st.markdown("---")
    st.write(T["pdf_vis_setting"])
    cols_per_row = st.radio(
        T["pdf_cols_per_row"],
        options=[1], 
        index=0, 
        horizontal=True
    )
    
    st.markdown("---")
    st.write(T["pdf_content_select"])

    include_items = st.checkbox(T["pdf_include_items"], value=True)
    include_comp = st.checkbox(T["pdf_include_comp"], value=True)
    include_corr = st.checkbox(T["pdf_include_corr"], value=True)
    include_demo = st.checkbox(T["pdf_include_demo"], value=True)
    include_normality = st.checkbox(T["pdf_include_normality"], value=True)
    
    st.markdown("---")
    st.markdown(T["pdf_visualizations"])
    
    include_freq_plot = st.checkbox(T["pdf_include_freq_plot"], value=True) 
    include_stacked_plot = st.checkbox(T["pdf_include_stacked_plot"], value=True)
    
    include_hist_x_plot = st.checkbox(T["pdf_include_hist_x_plot"], value=True)
    include_hist_y_plot = st.checkbox(T["pdf_include_hist_y_plot"], value=True)
    include_scatter_plot = st.checkbox(T["pdf_include_scatter_plot"], value=True)
    include_age_plot = st.checkbox(T["pdf_include_age_plot"], value=True)


    if st.button(T["pdf_button"]):
        styles = getSampleStyleSheet()
        story = []
        temp_imgs = []

        # Helper untuk membuat tabel (Menggunakan T[] untuk judul tabel)
        def add_table(title, df_table):
            story.append(Paragraph(title, styles["Heading3"]))
            df_reset = df_table.reset_index()
            
            # Ganti nama kolom 'Frequency' jika bahasa ID
            if lang_code == "id" and "Frequency" in df_reset.columns:
                 df_reset = df_reset.rename(columns={"Frequency": T["corr_table_metric"][0]})

            table_data = [df_reset.columns.tolist()] + df_reset.values.tolist()
            tbl = Table(table_data)
            # ... (TableStyle tidak berubah) ...
            tbl.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ]
                )
            )
            story.append(tbl)
            story.append(Spacer(1, 10))
            
        # Helper untuk menambahkan plot ke list
        def add_plot_to_list(fig, title_text, temp_list, width, height):
            """Saves plot to temp file and returns filename and title."""
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_file.name, bbox_inches="tight")
            plt.close(fig)
            temp_list.append(tmp_file.name)
            return {'title': title_text, 'file': tmp_file.name, 'width': width, 'height': height}

        
        # 1. KONFIGURASI AWAL PDF
        safe_filename = "".join(c for c in pdf_filename if c.isalnum() or c in (' ', '_')).rstrip()
        final_filename = (safe_filename if safe_filename else ("Laporan_Analisis" if lang_code == "id" else "Analysis_Report")) + ".pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        
        # 2. BANGUN KONTEN TEKS DAN TABEL
        
        story.append(Paragraph(T["pdf_title_report"], styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(T["pdf_title_group"], styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(T["pdf_member_title"], styles["Heading3"]))
        story.append(Paragraph("- Delon Raphael Andianto (004202200050)<br/>- Kallista Viasta (004202200039)<br/>- Nabila Putri Amalia (004202200049)<br/>- Pingkan R G Lumingkewas (004202200035)", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Data Cleaning Summary
        story.append(Paragraph(T["pdf_clean_title"], styles["Heading3"]))
        story.append(Paragraph(T["pdf_clean_desc"], styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(T["pdf_clean_summary"].format(before_clean, after_clean, before_clean - after_clean), styles["Normal"]))
        story.append(Spacer(1, 12))

        # Tables (Conditional)
        if include_normality: 
            add_table(T["pdf_table_normality"], result_norm)
        if include_demo: 
            add_table(T["pdf_table_demo_age"], age_demo_df)
            if gender_demo_df is not None: 
                add_table(T["pdf_table_demo_gender"], gender_demo_df)
        if include_items: 
            add_table(T["pdf_table_desc_items"], descriptive_table(df, x_items + y_items))
        if include_comp: 
            add_table(T["pdf_table_desc_comp"], descriptive_table(df, ["X_total", "Y_total"]))
        if include_corr:
            story.append(Paragraph(T["pdf_table_assoc"], styles["Heading3"]))
            story.append(Paragraph(assoc_summary_text, styles["Normal"]))
            story.append(Spacer(1, 10))

        
        # 3. KUMPULKAN DAN RENDERING GRAFIK
        
        # Hitung lebar dan tinggi grafik berdasarkan jumlah kolom
        if cols_per_row == 1:
            plot_width = 450
            plot_height = 300
        # else: (Logika untuk 2 atau 3 kolom jika diaktifkan)
        #     plot_width = ...

        # Hitung lebar ReportLab per kolom
        effective_page_width = 500.0
        col_unit_width = effective_page_width / cols_per_row
        image_render_width = col_unit_width * 0.95 # 95% untuk margin
        
        plots_to_render = []
        
        # 1. Age Group Bar Chart
        if include_age_plot:
            fig_pdf_age, ax_pdf_age = plt.subplots(figsize=(8, 5))
            age_counts.plot(kind='bar', ax=ax_pdf_age, color='skyblue', edgecolor='black')
            ax_pdf_age.set_title(T["plot_age_title"])
            ax_pdf_age.set_xlabel(T["plot_age_x"])
            ax_pdf_age.set_ylabel(T["plot_age_y"])
            ax_pdf_age.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plots_to_render.append(add_plot_to_list(fig_pdf_age, T["pdf_age_plot_title"], temp_imgs, 400, 300))

        # 2. FREQUENCY BAR CHARTS - SEMUA ITEM (X1-Y5)
        if include_freq_plot:
            all_items = x_items + y_items
            for var in all_items:
                fig_pdf_bar, ax_pdf_bar = plt.subplots(figsize=(6, 4))
                s_freq = df[var].dropna()
                freq = s_freq.value_counts().sort_index()
                ax_pdf_bar.bar(freq.index.astype(str), freq.values)
                ax_pdf_bar.set_xlabel(var)
                ax_pdf_bar.set_ylabel(T["plot_bar_y"])
                ax_pdf_bar.set_title(T["plot_bar_title"].format(var))
                plots_to_render.append(add_plot_to_list(fig_pdf_bar, T["pdf_freq_plot_title"].format(var), temp_imgs, plot_width, plot_height))
                
        # 3. STACKED BAR CHART 
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
            
            ax_stacked.set_title(T["plot_stack_title"])
            ax_stacked.set_xlabel(T["plot_stack_x"])
            ax_stacked.set_ylabel(T["plot_stack_y"])
            ax_stacked.legend(title=T["plot_stack_legend"], bbox_to_anchor=(1.05, 1), loc='upper left')
            ax_stacked.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            plots_to_render.append(add_plot_to_list(fig_stacked, T["pdf_stack_plot_title"], temp_imgs, 400, 300))

        # 4. Histogram X_total
        if include_hist_x_plot:
            fig_pdf_hist_x, ax_pdf_hist_x = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["X_total"].dropna()
            ax_pdf_hist_x.hist(d_hist, bins=5, edgecolor="black", color='lightcoral')
            ax_pdf_hist_x.set_title(T["plot_hist_x_title"])
            ax_pdf_hist_x.set_xlabel(T["plot_hist_x_x"])
            ax_pdf_hist_x.set_ylabel(T["plot_age_y"])
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_x, T["pdf_hist_x_plot_title"], temp_imgs, plot_width, plot_height))
            
        # 5. Histogram Y_total
        if include_hist_y_plot:
            fig_pdf_hist_y, ax_pdf_hist_y = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["Y_total"].dropna()
            ax_pdf_hist_y.hist(d_hist, bins=5, edgecolor="black", color='lightgreen')
            ax_pdf_hist_y.set_title(T["plot_hist_y_title"])
            ax_pdf_hist_y.set_xlabel(T["plot_hist_y_y"])
            ax_pdf_hist_y.set_ylabel(T["plot_age_y"])
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_y, T["pdf_hist_y_plot_title"], temp_imgs, plot_width, plot_height))

        # 6. Scatterplot X_total vs Y_total
        if include_scatter_plot:
            fig_pdf_sc, ax_pdf_sc = plt.subplots(figsize=(6, 4))
            ax_pdf_sc.scatter(valid_xy["X_total"], valid_xy["Y_total"])
            ax_pdf_sc.set_xlabel(T["plot_scatter_x"])
            ax_pdf_sc.set_ylabel(T["plot_scatter_y"])
            ax_pdf_sc.set_title(T["plot_scatter_title"])
            plots_to_render.append(add_plot_to_list(fig_pdf_sc, T["pdf_scatter_plot_title"], temp_imgs, plot_width, plot_height))


        # --- RENDERING GRAFIK SECARA HORIZONTAL (DALAM TABEL REPORTLAB) ---
        if plots_to_render:
            story.append(Paragraph(T["pdf_vis_title"], styles["Heading2"]))
            
            rows = []
            
            for i in range(0, len(plots_to_render), cols_per_row):
                row_plots = plots_to_render[i:i + cols_per_row]
                
                # Baris 1: Judul Grafik 
                title_row = [Paragraph(p['title'], styles['Normal']) for p in row_plots]
                
                # Baris 2: Gambar Grafik
                image_row = []
                for p in row_plots:
                    img = RLImage(p['file'], width=image_render_width)
                    image_row.append(img)
                
                # Jika ada kolom kosong di baris terakhir, tambahkan placeholder
                if len(row_plots) < cols_per_row:
                    diff = cols_per_row - len(row_plots)
                    for _ in range(diff):
                        title_row.append(Paragraph("", styles['Normal']))
                        image_row.append(Spacer(1, 1))
                
                rows.append(title_row)
                rows.append(image_row)
                
                # Buat tabel ReportLab setelah semua baris terkumpul
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


        # 4. MEMBANGUN PDF (TRY/EXCEPT BLOCK)

        try:
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            
            # DOWNLOAD PDF
            st.download_button(
                T["pdf_download_button"],
                data=pdf_bytes,
                file_name=final_filename, 
                mime="application/pdf",
            )
            st.success(T["pdf_success"].format(final_filename))
            
        except Exception as e:
            st.error(T["pdf_error"].format(e))
            
        finally:
            # Hapus file sementara gambar (temp_imgs)
            for path in temp_imgs:
                try:
                    os.remove(path)
                except OSError:
                    pass