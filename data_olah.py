import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import io
import os
import tempfile
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

# ------------------------------------------------------------------
# CONFIGURATIONS
# ------------------------------------------------------------------

# 1. RESPONSE LABELS (Hanya English untuk internal konsisten)
RESPONSE_LABELS_EN = {
    1: "1 (SD: Strongly Disagree)",
    2: "2 (D: Disagree)",
    3: "3 (N: Neutral)",
    4: "4 (A: Agree)",
    5: "5 (SA: Strongly Agree)",
}

# 2. LANGUAGE CONFIGURATION
LANGUAGES = {
    "English": {
        "title": "📊 The Relationship between Fear of Missing Out (FOMO) and Social Media Addiction among Generation Z",
        "caption": "Statistics 1 • Class 1",
        "sidebar_header": "👥 Group Members",
        "upload_header": "1. Upload Dataset",
        "upload_info": "Please upload the dataset first.",
        "preview_data": "Data Preview (The first 5 rows, before age cleaning):",
        "all_columns": "See all column names (headers):",
        "age_col_error": "Age column not found. Ensure a column name contains 'Age' or 'Umur'.",
        "age_col_detected": "Age column detected as:",
        "clean_success": "✅ Data cleaning & age grouping completed.",
        "clean_summary": "**Data Cleaning Summary:**",
        "resp_before": "- Respondents before cleaning:",
        "resp_after": "- Respondents after cleaning (13–28 years group only):",
        "resp_removed": "- Removed respondents:",
        "age_dist": "**Age Group Distribution:**",
        "preview_after": "Data Preview after cleaning & age grouping:",
        "select_header": "2. Select Variables X and Y (fixed item set)",
        "fomo_multiselect": "FOMO (X) – Choose Items:",
        "fomo_caption": "Selected FOMO items:",
        "addict_multiselect": "Social Media Addiction (Y) – Choose Items:",
        "addict_caption": "Selected Addiction items:",
        "min_select_warn": "Minimum Choose 1 item X and 1 item Y.",
        "col_missing_error": "Some question columns are missing.",
        "safest_way": "Safest way: change the headers in Excel/Sheets to X1..X5 and Y1..Y5, then re-upload.",
        "current_headers": "Current Headers:",
        "comp_header": "3. Composite Scores (X_total & Y_total)",
        "comp_method": "Composite score method:",
        "comp_success": "✅ Composite scores X_total and Y_total have been successfully created.",
        "normality_header": "Normality Test (Shapiro–Wilk)",
        "normality_result": "### Result:",
        "normality_normal": "Normal",
        "normality_not_normal": "Not Normal",
        "normality_reco": "✅ Recommended association method based on normality test:",
        "valid_resp_metric": "Valid respondents (after age filter)",
        "avg_fomo_metric": "Average FOMO ($X_{total}$)",
        "avg_addict_metric": "Average Addiction ($Y_{total}$)",
        "assoc_header": "4. Association Analysis – Choose One Method",
        "assoc_method_radio": "Association method for X and Y (based on normality recommendation):",
        "chi_header": "**Chi-square Test – select categorical X and Y (Likert).**",
        "chi_x_select": "Categorical X variable:",
        "chi_y_select": "Categorical Y variable:",
        "corr_result_header": "#### Result of {method} Correlation",
        "corr_metric_r": "Correlation Coefficient ($r$)",
        "corr_metric_p": "$p$-value",
        "corr_metric_dir": "Direction",
        "corr_metric_strength": "Strength",
        "corr_metric_signif": "Significance",
        "corr_interpretation": "#### Interpretation:",
        "corr_summary_template": "Using the {method} correlation, there is a {direction} and {strength} relationship between FOMO ($X_{total}$) and social media addiction ($Y_{total}$), with $r = {r_value:.3f}$ and $p = {p_value:.4f}$, indicating that the association is {signif_text}.",
        "corr_signif": "significant ($p < 0.05$)",
        "corr_not_signif": "not significant ($p \\ge 0.05$)",
        "corr_visual_check": "#### Visual Check: Scatterplot",
        "chi_result_header": "#### Result of Chi-square Test between {x} and {y}",
        "chi_metric_chi2": "Chi-square Value ($\\chi^2$)",
        "chi_metric_dof": "Degrees of Freedom (dof)",
        "chi_contingency": "#### Contingency Table",
        "chi_summary_template": "Using the Chi-square test between {x} and {y}, the chi-square statistic is $\\chi^2 = {chi2_value:.3f}$ with {dof} degrees of freedom and $p = {p_chi:.4f}$, indicating that the association is {signif_text}.",
        "no_assoc_method": "Please select an association method in section **4. Association Analysis** above.",
        "tab_desc": "📋 Descriptive Statistics",
        "tab_vis": "📈 Visualizations",
        "tab_assoc": "🔗 Analysis Result",
        "tab_pdf": "📄 PDF Report",
        "demo_header": "### 5.0 Demographic Summary",
        "age_dist_header": "**Age Group Distribution**",
        "gender_dist_header": "**Gender Distribution**",
        "gender_not_found": "Gender column was not detected, so gender distribution is not shown.",
        "desc_item_header": "### 5.1 Descriptive Statistics – Each Survey Item",
        "desc_comp_header": "### 5.2 Descriptive Statistics – Composite Scores ($X_{total}$ & $Y_{total}$)",
        "freq_header": "### 5.3 Frequency & Percentage Table (All X and Y Items)",
        "freq_caption": "The table shows the frequency distribution for each questionnaire item from X1 to Y5. The chart is available in the '📈 Visualizations' tab.",
        "freq_item_header": "#### Results for Item: **{var_freq}**",
        "likert_caption": "Description: SD = Strongly Disagree, SA = Strongly Agree.",
        "pdf_header": "8. Export PDF Report",
        "pdf_filename_input": "The name of the PDF file to be downloaded (without .pdf):",
        "pdf_vis_settings": "**Visualization Layout Settings in PDF:**",
        "pdf_cols_per_row": "Number of Plots per Row:",
        "pdf_select_content": "Select content to include in the PDF:",
        "pdf_include_items": "Descriptive statistics – items (X & Y)",
        "pdf_include_comp": "Descriptive statistics – composite scores ($X_{total}$ & $Y_{total}$)",
        "pdf_include_corr": "Association analysis summary",
        "pdf_include_demo": "Demographic summary (Age & Gender)",
        "pdf_include_normality": "Normality test result (Shapiro–Wilk)",
        "pdf_vis_header": "**Visualizations**",
        "pdf_include_freq_plot": "Frequency bar charts (All X and Y items)",
        "pdf_include_stacked_plot": "Stacked Bar Chart (All Item Response Percentage)",
        "pdf_include_hist_x_plot": "Histogram $X_{total}$",
        "pdf_include_hist_y_plot": "Histogram $Y_{total}$",
        "pdf_include_scatter_plot": "Scatterplot $X_{total}$ vs $Y_{total}$",
        "pdf_include_age_plot": "Demographic bar chart (Age Group)",
        "pdf_button": "Generate PDF Report",
        "pdf_success": "✅ PDF Report '{final_filename}' successfully created and ready for download.",
        "pdf_fail": "Failed to build PDF. Ensure all plots fit on the page (Try changing 'Number of Plots per Row' to 1 or 2). Error Detail: {e}",
        "plot_age_title": "Distribution of Respondents by Age Group",
        "plot_freq_title": "Frequency of {var}",
        "plot_stacked_title": "Response Percentage Across All Items (X & Y)",
        "plot_hist_x_title": "Histogram $X_{total}$ (FOMO)",
        "plot_hist_y_title": "Histogram $Y_{total}$ (Social Media Addiction)",
        "plot_scatter_title": "Scatterplot $X_{total}$ vs $Y_{total}$",
        "pdf_download_button": "Download PDF Report",
        "desc_freq": "Frequency",
        "desc_perc": "Percentage (%)",
        "desc_var": "Variable",
        "desc_mean": "Mean",
        "desc_median": "Median",
        "desc_mode": "Mode",
        "desc_min": "Min",
        "desc_max": "Max",
        "desc_std": "Std Dev",
        "vis_header": "### 6. Visualizations",
        "vis_age": "#### 6.1 Demographic Visualization",
        "vis_dist_x": "#### 6.2 Distribution of FOMO ($X_{total}$)",
        "vis_dist_y": "#### 6.3 Distribution of Social Media Addiction ($Y_{total}$)",
        "vis_assoc": "#### 6.4 Association Scatterplot ($X_{total}$ vs $Y_{total}$)",
        "vis_item_freq": "#### 6.5 Item Frequency Bar Charts",
        "download_chart_button": "Download {col_name} Bar Chart as PNG",
        "no_data_chart": "No valid data found for {col_name}.",
        "vis_stacked": "#### 6.6 Stacked Bar Chart of Item Response Percentages",
        "corr_strength_header": "**Visual Interpretation of Correlation Strength**",
        "corr_strength_diagram": "",
    },
    "Indonesia": {
        "title": "📊 Hubungan antara Fear of Missing Out (FOMO) dan Kecanduan Media Sosial pada Generasi Z",
        "caption": "Statistika 1 • Kelas 1",
        "sidebar_header": "👥 Anggota Kelompok",
        "upload_header": "1. Unggah Dataset",
        "upload_info": "Silakan unggah dataset terlebih dahulu.",
        "preview_data": "Pratinjau Data (5 baris pertama, sebelum pembersihan usia):",
        "all_columns": "Lihat semua nama kolom (header):",
        "age_col_error": "Kolom usia tidak ditemukan. Pastikan ada kolom dengan nama mengandung 'Age' atau 'Umur'.",
        "age_col_detected": "Kolom usia terdeteksi sebagai:",
        "clean_success": "✅ Pembersihan data & pengelompokan usia selesai.",
        "clean_summary": "**Ringkasan Pembersihan Data:**",
        "resp_before": "- Responden sebelum pembersihan:",
        "resp_after": "- Responden setelah pembersihan (hanya kelompok usia 13–28 tahun):",
        "resp_removed": "- Responden yang dihapus:",
        "age_dist": "**Distribusi Kelompok Usia:**",
        "preview_after": "Pratinjau data setelah pembersihan & pengelompokan usia:",
        "select_header": "2. Pilih Variabel X dan Y (set item tetap)",
        "fomo_multiselect": "FOMO (X) – Pilih Item:",
        "fomo_caption": "Item FOMO yang dipilih:",
        "addict_multiselect": "Kecanduan Media Sosial (Y) – Pilih Item:",
        "addict_caption": "Item Kecanduan yang dipilih:",
        "min_select_warn": "Minimum Pilih 1 item X dan 1 item Y.",
        "col_missing_error": "Beberapa kolom pertanyaan tidak ditemukan.",
        "safest_way": "Cara paling aman: ubah header di Excel/Sheets menjadi X1..X5 dan Y1..Y5, lalu unggah ulang.",
        "current_headers": "Header Saat Ini:",
        "comp_header": "3. Skor Komposit ($X_{total}$ & $Y_{total}$)",
        "comp_method": "Metode skor komposit:",
        "comp_success": "✅ Skor komposit $X_{total}$ dan $Y_{total}$ telah berhasil dibuat.",
        "normality_header": "Uji Normalitas (Shapiro–Wilk)",
        "normality_result": "### Hasil:",
        "normality_normal": "Normal",
        "normality_not_normal": "Tidak Normal",
        "normality_reco": "✅ Metode asosiasi yang direkomendasikan berdasarkan uji normalitas:",
        "valid_resp_metric": "Responden valid (setelah filter usia)",
        "avg_fomo_metric": "Rata-rata FOMO ($X_{total}$)",
        "avg_addict_metric": "Rata-rata Kecanduan ($Y_{total}$)",
        "assoc_header": "4. Analisis Asosiasi – Pilih Satu Metode",
        "assoc_method_radio": "Metode asosiasi untuk X dan Y (berdasarkan rekomendasi normalitas):",
        "chi_header": "**Uji Chi-square – pilih X dan Y kategorik (Likert).**",
        "chi_x_select": "Variabel X Kategorikal:",
        "chi_y_select": "Variabel Y Kategorikal:",
        "corr_result_header": "#### Hasil Korelasi {method}",
        "corr_metric_r": "Koefisien Korelasi ($r$)",
        "corr_metric_p": "Nilai $p$",
        "corr_metric_dir": "Arah",
        "corr_metric_strength": "Kekuatan",
        "corr_metric_signif": "Signifikansi",
        "corr_interpretation": "#### Interpretasi:",
        "corr_summary_template": "Menggunakan korelasi {method}, terdapat hubungan {direction} dan {strength} antara FOMO ($X_{total}$) dan kecanduan media sosial ($Y_{total}$), dengan $r = {r_value:.3f}$ dan $p = {p_value:.4f}$, menunjukkan bahwa asosiasi tersebut {signif_text}.",
        "corr_signif": "signifikan ($p < 0.05$)",
        "corr_not_signif": "tidak signifikan ($p \\ge 0.05$)",
        "corr_visual_check": "#### Pemeriksaan Visual: Scatterplot",
        "chi_result_header": "#### Hasil Uji Chi-square antara {x} dan {y}",
        "chi_metric_chi2": "Nilai Chi-square ($\\chi^2$)",
        "chi_metric_dof": "Derajat Kebebasan (dof)",
        "chi_contingency": "#### Tabel Kontingensi",
        "chi_summary_template": "Menggunakan uji Chi-square antara {x} dan {y}, statistik chi-square adalah $\\chi^2 = {chi2_value:.3f}$ dengan {dof} derajat kebebasan dan $p = {p_chi:.4f}$, menunjukkan bahwa asosiasi tersebut {signif_text}.",
        "no_assoc_method": "Silakan pilih metode asosiasi di bagian **4. Analisis Asosiasi** di atas.",
        "tab_desc": "📋 Statistik Deskriptif",
        "tab_vis": "📈 Visualisasi",
        "tab_assoc": "🔗 Hasil Analisis",
        "tab_pdf": "📄 Laporan PDF",
        "demo_header": "### 5.0 Ringkasan Demografi",
        "age_dist_header": "**Distribusi Kelompok Usia**",
        "gender_dist_header": "**Distribusi Jenis Kelamin**",
        "gender_not_found": "Kolom Jenis Kelamin tidak terdeteksi, sehingga distribusi jenis kelamin tidak ditampilkan.",
        "desc_item_header": "### 5.1 Statistik Deskriptif – Setiap Item Kuesioner",
        "desc_comp_header": "### 5.2 Statistik Deskriptif – Skor Komposit ($X_{total}$ & $Y_{total}$)",
        "freq_header": "### 5.3 Tabel Frekuensi & Persentase (Semua Item X dan Y)",
        "freq_caption": "Tabel menunjukkan distribusi frekuensi untuk setiap item kuesioner dari X1 hingga Y5. Grafik tersedia di tab '📈 Visualisasi'.",
        "freq_item_header": "#### Hasil untuk Item: **{var_freq}**",
        "likert_caption": "Keterangan: SD = Sangat Tidak Setuju, SA = Sangat Setuju.",
        "pdf_header": "8. Ekspor Laporan PDF",
        "pdf_filename_input": "Nama file PDF yang akan diunduh (tanpa .pdf):",
        "pdf_vis_settings": "**Pengaturan Tata Letak Visualisasi dalam PDF:**",
        "pdf_cols_per_row": "Jumlah Grafik per Baris:",
        "pdf_select_content": "Pilih konten yang ingin dimasukkan ke PDF:",
        "pdf_include_items": "Statistik deskriptif – item (X & Y)",
        "pdf_include_comp": "Statistik deskriptif – skor komposit ($X_{total}$ & $Y_{total}$)",
        "pdf_include_corr": "Ringkasan analisis asosiasi",
        "pdf_include_demo": "Ringkasan demografi (Usia & Jenis Kelamin)",
        "pdf_include_normality": "Hasil uji normalitas (Shapiro–Wilk)",
        "pdf_vis_header": "**Visualisasi**",
        "pdf_include_freq_plot": "Diagram batang frekuensi (Semua item X dan Y)",
        "pdf_include_stacked_plot": "Diagram Batang Bertumpuk (Persentase Respon Semua Item)",
        "pdf_include_hist_x_plot": "Histogram $X_{total}$",
        "pdf_include_hist_y_plot": "Histogram $Y_{total}$",
        "pdf_include_scatter_plot": "Scatterplot $X_{total}$ vs $Y_{total}$",
        "pdf_include_age_plot": "Diagram batang demografi (Kelompok Usia)",
        "pdf_button": "Buat Laporan PDF",
        "pdf_success": "✅ Laporan PDF '{final_filename}' berhasil dibuat dan siap diunduh.",
        "pdf_fail": "Gagal membangun PDF. Pastikan semua grafik muat di halaman (Coba ubah 'Jumlah Grafik per Baris' menjadi 1 atau 2). Detail Error: {e}",
        "plot_age_title": "Distribusi Responden berdasarkan Kelompok Usia",
        "plot_freq_title": "Frekuensi {var}",
        "plot_stacked_title": "Persentase Respon Semua Item (X & Y)",
        "plot_hist_x_title": "Histogram $X_{total}$ (FOMO)",
        "plot_hist_y_title": "Histogram $Y_{total}$ (Kecanduan Media Sosial)",
        "plot_scatter_title": "Scatterplot $X_{total}$ vs $Y_{total}$",
        "pdf_download_button": "Unduh Laporan PDF",
        "desc_freq": "Frekuensi",
        "desc_perc": "Persentase (%)",
        "desc_var": "Variabel",
        "desc_mean": "Rata-rata",
        "desc_median": "Median",
        "desc_mode": "Modus",
        "desc_min": "Min",
        "desc_max": "Max",
        "desc_std": "Std Deviasi",
        "vis_header": "### 6. Visualisasi",
        "vis_age": "#### 6.1 Visualisasi Demografi",
        "vis_dist_x": "#### 6.2 Distribusi FOMO ($X_{total}$)",
        "vis_dist_y": "#### 6.3 Distribusi Kecanduan Media Sosial ($Y_{total}$)",
        "vis_assoc": "#### 6.4 Scatterplot Asosiasi ($X_{total}$ vs $Y_{total}$)",
        "vis_item_freq": "#### 6.5 Diagram Batang Frekuensi Item",
        "download_chart_button": "Unduh Diagram Batang {col_name} sebagai PNG",
        "no_data_chart": "Tidak ada data valid ditemukan untuk {col_name}.",
        "vis_stacked": "#### 6.6 Diagram Batang Bertumpuk Persentase Respon Item",
        "corr_strength_header": "**Interpretasi Kekuatan Korelasi Visual**",
        "corr_strength_diagram": "",
    }
}

# 3. SELECT LANGUAGE (Default ke Indonesia)
st.sidebar.header("🌍 Language / Bahasa")
selected_lang = st.sidebar.radio("Choose language / Pilih bahasa:", options=["English", "Indonesia"], index=1)
lang = LANGUAGES[selected_lang]

# Sesuaikan RESPONSE_LABELS dengan bahasa terpilih (untuk tampilan)
RESPONSE_LABELS = {
    1: f"1 (SD: Strongly Disagree / Sangat Tidak Setuju)",
    2: f"2 (D: Disagree / Tidak Setuju)",
    3: f"3 (N: Neutral / Netral)",
    4: f"4 (A: Agree / Setuju)",
    5: f"5 (SA: Strongly Agree / Sangat Setuju)",
} if selected_lang == "Indonesia" else RESPONSE_LABELS_EN

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="FOMO & Social Media Addiction – Group 3",
    layout="wide"
)

st.title(lang["title"])
st.caption(lang["caption"])

# ------------------------------------------------------------------
# SIDEBAR – GROUP MEMBERS
# ------------------------------------------------------------------
st.sidebar.header(lang["sidebar_header"])
st.sidebar.write("- Delon Raphael Andianto (004202200050)")
st.sidebar.write("- Kallista Viasta (004202200039)")
st.sidebar.write("- Nabila Putri Amalia (004202200049)")
st.sidebar.write("- Pingkan R G Lumingkewas (004202200035)")

# ------------------------------------------------------------------
# 1. UPLOAD DATASET
# ------------------------------------------------------------------
st.subheader(lang["upload_header"])

uploaded = st.file_uploader(
    "Upload a CSV or Excel file / Unggah file CSV atau Excel:",
    type=["csv", "xlsx"]
)

if uploaded is None:
    st.info(lang["upload_info"])
    st.stop()

if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

st.write(lang["preview_data"])
st.dataframe(df.head())

with st.expander(lang["all_columns"]):
    st.write(list(df.columns))

# ------------------------------------------------------------------
# 1A. DATA CLEANING – AGE CATEGORIES
# ------------------------------------------------------------------

# Auto-detect age column
AGE_COLUMN = None
for col in df.columns:
    col_lower = str(col).lower()
    if "age" in col_lower or "umur" in col_lower:
        AGE_COLUMN = col
        break

if AGE_COLUMN is None:
    st.error(lang["age_col_error"])
    st.stop()

st.write(f"{lang['age_col_detected']} **{AGE_COLUMN}**")

allowed_age_categories = [
    "13–18 years / tahun",
    "19–23 years / tahun",
    "24–28 years / tahun",
    "13-18 years / tahun",
    "19-23 years / tahun",
    "24-28 years / tahun",
]

before_clean = len(df)

# Filter for allowed age categories
df = df[df[AGE_COLUMN].astype(str).isin(allowed_age_categories)]

after_clean = len(df)

# Create Age_Group column
df["Age_Group"] = df[AGE_COLUMN].astype("category")

st.success(lang["clean_success"])
st.write(lang["clean_summary"])
st.write(f"{lang['resp_before']} {before_clean}")
st.write(f"{lang['resp_after']} {after_clean}")
st.write(f"{lang['resp_removed']} {before_clean - after_clean}")

st.write(lang["age_dist"])
st.dataframe(df["Age_Group"].value_counts().rename(lang["desc_freq"]))

st.write(lang["preview_after"])
st.dataframe(df.head())

# ------------------------------------------------------------------
# DEMOGRAPHIC SUMMARY (Age_Group + optional Gender)
# ------------------------------------------------------------------

# Summary Age_Group (frequency + percentage)
age_counts = df["Age_Group"].value_counts().sort_index()
age_demo_df = pd.DataFrame({
    f"Age Group / {LANGUAGES['Indonesia']['age_dist_header'].strip('*')}": age_counts.index,
    lang["desc_freq"]: age_counts.values,
})
age_demo_df[lang["desc_perc"]] = (age_demo_df[lang["desc_freq"]] / age_demo_df[lang["desc_freq"]].sum() * 100).round(2)

# Auto-detect gender column (optional)
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
        f"Gender / {LANGUAGES['Indonesia']['gender_dist_header'].strip('*')}": gender_counts.index,
        lang["desc_freq"]: gender_counts.values,
    })
    gender_demo_df[lang["desc_perc"]] = (gender_demo_df[lang["desc_freq"]] / gender_demo_df[lang["desc_freq"]].sum() * 100).round(2)

# ------------------------------------------------------------------
# 2. FIXED DEFINITIONS FOR X & Y (ACCORDING TO QUESTIONNAIRE)
# ------------------------------------------------------------------
# Use English for internal labels
FOMO_LABELS = {
    "X1": "I feel anxious if I don't know the latest updates on social media. / Saya merasa cemas jika tidak tahu kabar terbaru di media sosial.",
    "X2": "I feel the urge to constantly check social media to stay connected. / Saya merasa terdorong untuk terus memeriksa media sosial agar tetap terhubung.",
    "X3": "I'm afraid of being left behind when others talk about trending topics. / Saya takut tertinggal ketika orang lain membicarakan topik yang sedang tren.",
    "X4": "I feel the need to follow viral trends to stay “included”. / Saya merasa perlu mengikuti tren viral agar tetap “termasuk”.",
    "X5": "I feel uncomfortable when I see others participating in activities that I am not part of. / Saya merasa tidak nyaman ketika melihat orang lain berpartisipasi dalam kegiatan yang tidak saya ikuti.",
}

ADDICTION_LABELS = {
    "Y1": "I find it difficult to reduce the amount of time I spend on social media. / Saya merasa sulit untuk mengurangi waktu yang saya habiskan di media sosial.",
    "Y2": "I prefer using social media over doing offline activities. / Saya lebih memilih menggunakan media sosial daripada melakukan kegiatan offline.",
    "Y3": "Social media usage disrupts my sleep, study time, or other important activities. / Penggunaan media sosial mengganggu tidur, waktu belajar, atau kegiatan penting lainnya.",
    "Y4": "I often spend more time on social media than I originally planned. / Saya sering menghabiskan lebih banyak waktu di media sosial dari yang saya rencanakan semula.",
    "Y5": "I often open social media automatically without any clear purpose. / Saya sering membuka media sosial secara otomatis tanpa tujuan yang jelas.",
}

fixed_x_all = list(FOMO_LABELS.keys())
fixed_y_all = list(ADDICTION_LABELS.keys())

# ------------------------------------------------------------------
# 2A. FLEXIBLE MAPPING HEADER → X1..Y5 (FROM QUESTION TEXT)
# ------------------------------------------------------------------
if not all(c in df.columns for c in fixed_x_all + fixed_y_all):
    PHRASES = {
        # Check for English phrases
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
        # Add Indonesian phrases for robustness
        "X1_ID": "cemas jika tidak tahu kabar terbaru",
        "X2_ID": "terdorong untuk terus memeriksa media sosial",
        "X3_ID": "takut tertinggal ketika orang lain membicarakan topik yang sedang tren",
        "X4_ID": "perlu mengikuti tren viral agar tetap termasuk",
        "X5_ID": "tidak nyaman ketika melihat orang lain berpartisipasi",
        "Y1_ID": "sulit untuk mengurangi waktu yang saya habiskan di media sosial",
        "Y2_ID": "lebih memilih menggunakan media sosial daripada melakukan kegiatan offline",
        "Y3_ID": "mengganggu tidur, waktu belajar, atau kegiatan penting lainnya",
        "Y4_ID": "menghabiskan lebih banyak waktu di media sosial dari yang saya rencanakan semula",
        "Y5_ID": "membuka media sosial secara otomatis tanpa tujuan yang jelas",
    }

    lower_cols = {c: str(c).lower() for c in df.columns}
    renamed = {}

    for code, phrase in PHRASES.items():
        base_code = code.split('_')[0] 
        phrase_low = phrase.lower()
        for col, col_low in lower_cols.items():
            if phrase_low in col_low and base_code not in renamed.values():
                renamed[col] = base_code

    df = df.rename(columns=renamed)

missing_x = [c for c in fixed_x_all if c not in df.columns]
missing_y = [c for c in fixed_y_all if c not in df.columns]

if missing_x or missing_y:
    st.error(
        f"{lang['col_missing_error']}\n\n"
        f"Missing FOMO (X): {missing_x}\n"
        f"Missing Addiction (Y): {missing_y}\n\n"
        f"{lang['safest_way']}"
    )
    st.write(f"{lang['current_headers']} {list(df.columns)}")
    st.stop()

# ------------------------------------------------------------------
# 3. SELECT SUBSET X & Y
# ------------------------------------------------------------------
st.subheader(lang["select_header"])

cA, cB = st.columns(2)

with cA:
    x_items = st.multiselect(
        lang["fomo_multiselect"],
        options=fixed_x_all,
        default=fixed_x_all,
        help="Just X1–X5 (Like Questionnaire)." if selected_lang == "English" else "Hanya X1–X5 (Sesuai Kuesioner).",
    )
    st.markdown(f"**{lang['fomo_caption']}**")
    for code in x_items:
        st.caption(f"**{code}** — {FOMO_LABELS[code]}")

with cB:
    y_items = st.multiselect(
        lang["addict_multiselect"],
        options=fixed_y_all,
        default=fixed_y_all,
        help="Just Y1–Y5 (Like Questionnaire)." if selected_lang == "English" else "Hanya Y1–Y5 (Sesuai Kuesioner).",
    )
    st.markdown(f"**{lang['addict_caption']}**")
    for code in y_items:
        st.caption(f"**{code}** — {ADDICTION_LABELS[code]}")

if len(x_items) == 0 or len(y_items) == 0:
    st.warning(lang["min_select_warn"])
    st.stop()

for col in x_items + y_items:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------------
# 4. COMPOSITE SCORES
# ------------------------------------------------------------------
st.subheader(lang["comp_header"])

comp_method_options = [
    "Mean of items (recommended)" if selected_lang == "English" else "Rata-rata item (direkomendasikan)", 
    "Sum of items" if selected_lang == "English" else "Jumlah item"
]
comp_method = st.radio(
    lang["comp_method"],
    comp_method_options,
    horizontal=True,
)

if comp_method.startswith("Mean") or comp_method.startswith("Rata-rata"):
    df["X_total"] = df[x_items].mean(axis=1)
    df["Y_total"] = df[y_items].mean(axis=1)
else:
    df["X_total"] = df[x_items].sum(axis=1)
    df["Y_total"] = df[y_items].sum(axis=1)

st.success(lang["comp_success"])
valid_xy = df[["X_total", "Y_total"]].dropna()
n_valid = valid_xy.shape[0]
mean_x = valid_xy["X_total"].mean()
mean_y = valid_xy["Y_total"].mean()

# ------------------------------------------------------------------
# NORMALITY TEST (Shapiro–Wilk)
# ------------------------------------------------------------------

st.subheader(lang["normality_header"])

if n_valid < 3:
    st.warning("Not enough data for Shapiro-Wilk test (N < 3). Skipping.")
    normal_x = "Not Applicable"
    normal_y = "Not Applicable"
    shapiro_x = type('ShapiroResult', (object,), {'statistic': np.nan, 'pvalue': np.nan})()
    shapiro_y = type('ShapiroResult', (object,), {'statistic': np.nan, 'pvalue': np.nan})()
else:
    shapiro_x = stats.shapiro(valid_xy["X_total"])
    shapiro_y = stats.shapiro(valid_xy["Y_total"])
    normal_x = lang["normality_normal"] if shapiro_x.pvalue >= 0.05 else lang["normality_not_normal"]
    normal_y = lang["normality_normal"] if shapiro_y.pvalue >= 0.05 else lang["normality_not_normal"]

st.write(lang["normality_result"])

result_norm = pd.DataFrame({
    lang["desc_var"]: ["X_total", "Y_total"],
    "Shapiro-Wilk Statistic": [shapiro_x.statistic, shapiro_y.statistic],
    "p-value": [shapiro_x.pvalue, shapiro_y.pvalue],
    "Normality": [normal_x, normal_y]
})

st.dataframe(result_norm.round(4))

# Rekomendasi metode berdasarkan normality
if normal_x == lang["normality_normal"] and normal_y == lang["normality_normal"]:
    recommended_method = "Pearson Correlation"
else:
    recommended_method = "Spearman Rank Correlation"

st.info(f"{lang['normality_reco']} **{recommended_method}**")


m1, m2, m3 = st.columns(3)
m1.metric(lang["valid_resp_metric"], n_valid)
m2.metric(lang["avg_fomo_metric"], f"{mean_x:.2f}")
m3.metric(lang["avg_addict_metric"], f"{mean_y:.2f}")

# ------------------------------------------------------------------
# 5. HELPER – DESCRIPTIVE TABLE & BAR CHART ITEM
# ------------------------------------------------------------------
def descriptive_table(data: pd.DataFrame, cols):
    rows = []
    for col in cols:
        s = data[col].dropna()
        if s.empty:
            continue
        mode_vals = s.mode()
        mode_val = mode_vals.iloc[0] if not mode_vals.empty else np.nan
        rows.append(
            {
                lang["desc_var"]: col,
                "N": len(s),
                lang["desc_mean"]: s.mean(),
                lang["desc_median"]: s.median(),
                lang["desc_mode"]: mode_val,
                lang["desc_min"]: s.min(),
                lang["desc_max"]: s.max(),
                lang["desc_std"]: s.std(ddof=1),
            }
        )
    return pd.DataFrame(rows).set_index(lang["desc_var"]).round(3)


# HELPER: To create and display individual bar charts
def create_item_bar_chart(df, col_name, lang):
    s_freq = df[col_name].dropna()
    freq = s_freq.value_counts().sort_index()

    if freq.empty:
        st.warning(lang["no_data_chart"].format(col_name=col_name))
        return
        
    fig_bar, ax_bar = plt.subplots()
    
    # Map numerical score to label for better visualization
    labels = [RESPONSE_LABELS.get(int(i), str(int(i))) for i in freq.index.astype(int)]
    
    ax_bar.bar(labels, freq.values, color='skyblue', edgecolor='black')
    ax_bar.set_xlabel(col_name)
    ax_bar.set_ylabel(lang["desc_freq"])
    ax_bar.set_title(lang["plot_freq_title"].format(var=col_name))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    st.pyplot(fig_bar)

    buf_bar = io.BytesIO()
    fig_bar.savefig(buf_bar, format="png", bbox_inches="tight")
    buf_bar.seek(0)
    
    st.download_button(
        lang["download_chart_button"].format(col_name=col_name),
        data=buf_bar,
        file_name=f"{col_name}_bar_chart.png",
        mime="image/png",
    )
    plt.close(fig_bar) 

# ------------------------------------------------------------------
# 6. ASSOCIATION METHOD – CHOOSE ONE
# ------------------------------------------------------------------
st.subheader(lang["assoc_header"])

assoc_method = st.radio(
    lang["assoc_method_radio"],
    ["Pearson Correlation", "Spearman Rank Correlation", "Chi-square Test (categorical X & Y)"],
    index=0,
)

assoc_stats = {"type": "none"}
assoc_summary_text = lang["no_assoc_method"]

if assoc_method in ["Pearson Correlation", "Spearman Rank Correlation"]:
    
    try:
        x_corr = valid_xy["X_total"]
        y_corr = valid_xy["Y_total"]

        # ********** PENGAMAN TAMBAHAN BARU **********
        if x_corr.empty or y_corr.empty or len(x_corr) < 2:
            assoc_summary_text = "ERROR: Not enough valid data for correlation calculation (N < 2). Check if all item scores (X1-Y5) are numeric and not missing after age filtering."
            st.error(assoc_summary_text)
            # Use st.stop() to halt execution cleanly after an error in Streamlit.
            st.stop()
        # **********************************************

        if assoc_method.startswith("Pearson"):
            r_value, p_value = stats.pearsonr(x_corr, y_corr)
            method_short = "Pearson"
        else:
            r_value, p_value = stats.spearmanr(x_corr, y_corr)
            method_short = "Spearman"

        # Fungsi interpretasi kekuatan
        def interpret_strength(r):
            a = abs(r)
            if selected_lang == "English":
                if a < 0.2: return "very weak"
                elif a < 0.4: return "weak"
                elif a < 0.6: return "moderate"
                elif a < 0.8: return "strong"
                else: return "very strong"
            else: 
                if a < 0.2: return "sangat lemah"
                elif a < 0.4: return "lemah"
                elif a < 0.6: return "sedang"
                elif a < 0.8: return "kuat"
                else: return "sangat kuat"
        
        # Penafsiran hasil
        direction = "positive" if r_value > 0 else "negative"
        if selected_lang == "Indonesia":
            direction = "positif" if r_value > 0 else "negatif"
            
        strength = interpret_strength(r_value)
        
        signif_text = lang["corr_signif"] if p_value < 0.05 else lang["corr_not_signif"]
        
        # Simpan statistik
        assoc_stats = {
            "type": "correlation",
            "method": method_short,
            "r": r_value,
            "p": p_value,
            "direction": direction,
            "strength": strength,
            "signif_text": signif_text,
        }
        
        # Buat ringkasan teks
        assoc_summary_text = lang["corr_summary_template"].format(
            method=method_short,
            direction=direction, 
            strength=strength,
            r_value=r_value,
            p_value=p_value,
            signif_text=signif_text,
        )
        
    except Exception as e:
        # Jika error lain terjadi (misalnya, data non-numeric yang lolos filter)
        assoc_summary_text = f"Failed to calculate correlation. Error: {e}"
        st.error(assoc_summary_text)
        assoc_stats = {"type": "error"} # Set to error state


elif assoc_method.startswith("Chi-square"):
    st.markdown(lang["chi_header"])
    
    # Select only the original Likert columns (X1-X5, Y1-Y5) for Chi-Square
    cat_options = [c for c in (x_items + y_items) if c in df.columns]

    if not cat_options:
        st.error("No valid categorical items (X1-X5 or Y1-Y5) available for Chi-square test.")
        st.stop()
        
    chi_x_col = st.selectbox(lang["chi_x_select"], cat_options, key="chi_x")
    chi_y_col = st.selectbox(lang["chi_y_select"], cat_options, key="chi_y")

    contingency = pd.crosstab(df[chi_x_col], df[chi_y_col])
    
    if contingency.empty or contingency.shape[0] <= 1 or contingency.shape[1] <= 1:
        st.error("Contingency table is too small (e.g., only one row/column) to perform Chi-square test.")
        assoc_stats = {"type": "none"}
        st.stop()
        
    try:
        chi2_value, p_chi, dof, expected = stats.chi2_contingency(contingency)
        signif_text = lang["corr_signif"] if p_chi < 0.05 else lang["corr_not_signif"]

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

        assoc_summary_text = lang["chi_summary_template"].format(
            x=chi_x_col, 
            y=chi_y_col, 
            chi2_value=chi2_value, 
            dof=dof, 
            p_chi=p_chi, 
            signif_text=signif_text
        )
    except Exception as e:
        st.error(f"Failed to calculate Chi-square. Error: {e}")
        assoc_stats = {"type": "error"} # Set to error state


# ------------------------------------------------------------------
# 7. TABS
# ------------------------------------------------------------------

# Prepare Age Group Bar Chart (for tab_vis & pdf)
fig_age_bar, ax_age_bar = plt.subplots(figsize=(8, 5))
age_counts.plot(kind='bar', ax=ax_age_bar, color='skyblue', edgecolor='black')
ax_age_bar.set_title(lang["plot_age_title"])
ax_age_bar.set_xlabel(f"Age Group / {LANGUAGES['Indonesia']['age_dist_header'].strip('*')}")
ax_age_bar.set_ylabel(lang["desc_freq"])
ax_age_bar.tick_params(axis='x', rotation=45)
plt.tight_layout()
buf_age_bar = io.BytesIO()
fig_age_bar.savefig(buf_age_bar, format="png", bbox_inches="tight")
buf_age_bar.seek(0)
plt.close(fig_age_bar)

tab_desc, tab_vis, tab_assoc, tab_pdf = st.tabs(
    [lang["tab_desc"], lang["tab_vis"], lang["tab_assoc"], lang["tab_pdf"]]
)

# ------------------ TAB DESCRIPTIVES ------------------
with tab_desc:
    st.markdown(lang["demo_header"])

    st.markdown(lang["age_dist_header"])
    st.dataframe(age_demo_df)

    if gender_demo_df is not None:
        st.markdown(lang["gender_dist_header"])
        st.dataframe(gender_demo_df)
    else:
        st.info(lang["gender_not_found"])

    st.markdown(lang["desc_item_header"])
    desc_items = descriptive_table(df, x_items + y_items)
    st.dataframe(desc_items)

    st.markdown(lang["desc_comp_header"])
    desc_comp = descriptive_table(df, ["X_total", "Y_total"])
    st.dataframe(desc_comp)

#--------------- Frequency ---------------
    st.markdown(lang["freq_header"])
    st.caption(lang["freq_caption"])

    all_items = x_items + y_items

    # Loop through all items (X1 to Y5) to display TABLES only
    for var_freq in all_items:
        st.markdown(lang["freq_item_header"].format(var_freq=var_freq))

        # 1. Calculate Frequency and Percentage
        s_freq = df[var_freq].dropna()
        freq = s_freq.value_counts().sort_index()
        perc = (freq / freq.sum() * 100).round(2)
        freq_table = pd.DataFrame({lang["desc_freq"]: freq, lang["desc_perc"]: perc})

        # 2. Apply Likert Label Mapping
        if var_freq in (x_items + y_items):
            try:
                if freq_table.index.dtype in [int, float] and freq_table.index.max() <= 5: 
                    # Map to the full bilingual label
                    labeled_index = freq_table.index.map(lambda x: RESPONSE_LABELS.get(x, x))
                    freq_table.index = labeled_index
                    st.caption(lang["likert_caption"])
            except:
                pass 

        st.dataframe(freq_table)
        st.markdown("---") 
        
# ------------------ TAB VISUALIZATIONS ------------------
with tab_vis:
    st.markdown(lang["vis_header"])

    # 6.1 Age Group Bar Chart
    st.markdown(lang["vis_age"])
    st.image(buf_age_bar)
    
    # 6.2 Distribution of X_total
    st.markdown(lang["vis_dist_x"])
    fig_hist_x, ax_hist_x = plt.subplots()
    ax_hist_x.hist(valid_xy["X_total"].dropna(), bins=5, edgecolor="black", color='lightcoral')
    ax_hist_x.set_title(lang["plot_hist_x_title"])
    ax_hist_x.set_xlabel("$X_{total}$ Score (FOMO)")
    ax_hist_x.set_ylabel(lang["desc_freq"])
    st.pyplot(fig_hist_x)
    plt.close(fig_hist_x)
    
    # 6.3 Distribution of Y_total
    st.markdown(lang["vis_dist_y"])
    fig_hist_y, ax_hist_y = plt.subplots()
    ax_hist_y.hist(valid_xy["Y_total"].dropna(), bins=5, edgecolor="black", color='lightgreen')
    ax_hist_y.set_title(lang["plot_hist_y_title"])
    ax_hist_y.set_xlabel("$Y_{total}$ Score (Addiction)")
    ax_hist_y.set_ylabel(lang["desc_freq"])
    st.pyplot(fig_hist_y)
    plt.close(fig_hist_y)
    
    # 6.4 Association Scatterplot
    st.markdown(lang["vis_assoc"])
    fig_assoc_scatter, ax_assoc_scatter = plt.subplots()
    ax_assoc_scatter.scatter(valid_xy["X_total"], valid_xy["Y_total"], color='purple', alpha=0.6)
    m, b = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
    ax_assoc_scatter.plot(valid_xy["X_total"], m*valid_xy["X_total"] + b, color='red', linestyle='--')
    ax_assoc_scatter.set_xlabel("$X_{total}$ (FOMO)")
    ax_assoc_scatter.set_ylabel("$Y_{total}$ (Social media addiction)")
    ax_assoc_scatter.set_title(lang["plot_scatter_title"])
    st.pyplot(fig_assoc_scatter)
    plt.close(fig_assoc_scatter)
    
    # 6.5 Item Frequency Bar Charts
    st.markdown(lang["vis_item_freq"])
    for var in x_items + y_items:
        create_item_bar_chart(df, var, lang)

    # 6.6 Stacked Bar Chart
    st.markdown(lang["vis_stacked"])
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
    
    ax_stacked.set_title(lang["plot_stacked_title"])
    ax_stacked.set_xlabel("Survey Item / Item Kuesioner")
    ax_stacked.set_ylabel(lang["desc_perc"])
    legend_labels_short = {i: RESPONSE_LABELS[i].split(' ')[0] for i in range(1, 6)}
    ax_stacked.legend(title="Response Score / Skor Respon", labels=[legend_labels_short[col] for col in freq_data.columns], bbox_to_anchor=(1.05, 1), loc='upper left')
    ax_stacked.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig_stacked)
    plt.close(fig_stacked)


# --- Test Result/analysis ------

with tab_assoc:
    st.markdown(f"### 7. {lang['tab_assoc']} ({assoc_method})")

    if assoc_stats["type"] == "correlation":
        st.markdown(lang["corr_result_header"].format(method=assoc_stats['method']))
        
        corr_data = pd.DataFrame({
            "Metric / Metrik": [
                lang["corr_metric_r"], 
                lang["corr_metric_p"], 
                lang["corr_metric_dir"], 
                lang["corr_metric_strength"], 
                lang["corr_metric_signif"]
            ],
            "Value / Nilai": [
                f"{assoc_stats['r']:.3f}", 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['direction'].capitalize(), 
                assoc_stats['strength'].capitalize(), 
                assoc_stats['signif_text'].capitalize()
            ]
        }).set_index("Metric / Metrik")
        
        st.dataframe(corr_data)

        st.markdown(lang["corr_interpretation"])
        st.success(assoc_summary_text)
        
        # Tambahkan diagram instruktif interpretasi korelasi di sini
        st.markdown("---")
        st.markdown(lang["corr_strength_header"])
        st.markdown(lang["corr_strength_diagram"])
        
        st.markdown("---")
        st.markdown(lang["corr_visual_check"])
        
        # Recreate scatterplot for this analysis tab
        fig_assoc_scatter, ax_assoc_scatter = plt.subplots()
        ax_assoc_scatter.scatter(valid_xy["X_total"], valid_xy["Y_total"], color='purple', alpha=0.6)
        
        # Add regression line
        m, b = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
        ax_assoc_scatter.plot(valid_xy["X_total"], m*valid_xy["X_total"] + b, color='red', linestyle='--')
        
        ax_assoc_scatter.set_xlabel("$X_{total}$ (FOMO)")
        ax_assoc_scatter.set_ylabel("$Y_{total}$ (Social media addiction)")
        ax_assoc_scatter.set_title(lang["plot_scatter_title"] + f" ($r={assoc_stats['r']:.3f}$)")
        st.pyplot(fig_assoc_scatter)
        plt.close(fig_assoc_scatter)

    elif assoc_stats["type"] == "chi-square":
        st.markdown(lang["chi_result_header"].format(x=assoc_stats['x'], y=assoc_stats['y']))
        
        chi_data = pd.DataFrame({
            "Metric / Metrik": [
                lang["chi_metric_chi2"], 
                lang["chi_metric_dof"], 
                lang["corr_metric_p"], 
                lang["corr_metric_signif"]
            ],
            "Value / Nilai": [
                f"{assoc_stats['chi2']:.3f}", 
                assoc_stats['dof'], 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['signif_text'].capitalize()
            ]
        }).set_index("Metric / Metrik")
        
        st.dataframe(chi_data)
        st.markdown(lang["corr_interpretation"])
        st.success(assoc_summary_text)
        
        st.markdown("---")
        st.markdown(lang["chi_contingency"])
        contingency = pd.crosstab(df[assoc_stats['x']], df[assoc_stats['y']])
        st.dataframe(contingency)
        
    elif assoc_stats["type"] == "error":
         st.error(assoc_summary_text)
        
    else:
        st.warning(lang["no_assoc_method"])

# ------------------ TAB PDF REPORT ------------------
with tab_pdf:
    st.markdown(f"### {lang['pdf_header']}")

    # 1. INPUT NAMA FILE
    pdf_filename = st.text_input(
        lang["pdf_filename_input"],
        value="Laporan_Analisis" if selected_lang == "Indonesia" else "Analysis_Report"
    )
    
    # 2. PILIHAN JUMLAH GRAFIK HORIZONTAL
    st.markdown("---")
    st.write(lang["pdf_vis_settings"])
    
    cols_per_row = st.radio(
        lang["pdf_cols_per_row"],
        options=[1], 
        index=0, 
        horizontal=True,
        format_func=lambda x: f"{x}"
    )
    
    st.markdown("---")
    st.write(lang["pdf_select_content"])

    include_items = st.checkbox(lang["pdf_include_items"], value=True)
    include_comp = st.checkbox(lang["pdf_include_comp"], value=True)
    include_corr = st.checkbox(lang["pdf_include_corr"], value=True)
    include_demo = st.checkbox(lang["pdf_include_demo"], value=True)
    include_normality = st.checkbox(lang["pdf_include_normality"], value=True)
    
    st.markdown("---")
    st.markdown(lang["pdf_vis_header"])
    
    include_freq_plot = st.checkbox(lang["pdf_include_freq_plot"], value=True) 
    include_stacked_plot = st.checkbox(lang["pdf_include_stacked_plot"], value=True)
    
    include_hist_x_plot = st.checkbox(lang["pdf_include_hist_x_plot"], value=True)
    include_hist_y_plot = st.checkbox(lang["pdf_include_hist_y_plot"], value=True)
    include_scatter_plot = st.checkbox(lang["pdf_include_scatter_plot"], value=True)
    include_age_plot = st.checkbox(lang["pdf_include_age_plot"], value=True)


    if st.button(lang["pdf_button"]):
        styles = getSampleStyleSheet()
        story = []
        temp_imgs = []
        
        # Helper function to create table for ReportLab
        def add_table(title, df_table, index_name=lang["desc_var"]):
            story.append(Paragraph(title, styles["Heading3"]))
            # Handle bilingual headers
            df_table_copy = df_table.copy()
            df_table_copy.index.name = index_name
            df_reset = df_table_copy.reset_index()
            
            table_data = [df_reset.columns.tolist()] + df_reset.values.tolist()
            tbl = Table(table_data)
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
            
        # Helper function to save plot to temp file
        def add_plot_to_list(fig, title_text, temp_list, width=400, height=300):
            """Saves plot to temp file and returns filename and title."""
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_file.name, bbox_inches="tight")
            plt.close(fig)
            temp_list.append(tmp_file.name)
            return {'title': title_text, 'file': tmp_file.name, 'width': width, 'height': height}

        
        # 1. PDF INITIAL CONFIGURATION
        safe_filename = "".join(c for c in pdf_filename if c.isalnum() or c in (' ', '_')).rstrip()
        final_filename = (safe_filename if safe_filename else "Analysis_Report") + ".pdf"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        
        # 2. BUILD TEXT AND TABLE CONTENT
        story.append(Paragraph(lang["title"], styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("FOMO & Social Media Addiction – Statistics 1 (Group 3)", styles["Heading2"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(lang["sidebar_header"], styles["Heading3"]))
        story.append(Paragraph("- Delon Raphael Andianto (004202200050)<br/>- Kallista Viasta (004202200039)<br/>- Nabila Putri Amalia (004202200049)<br/>- Pingkan R G Lumingkewas (004202200035)", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Data Cleaning Summary
        story.append(Paragraph(lang["clean_summary"].strip('*'), styles["Heading3"]))
        story.append(Paragraph(
            "Only respondents whose age category was 13–18 years, 19–23 years, or 24–28 years were included in the analysis to represent Generation Z. Other age categories such as below 13 or above 28 years were excluded.", 
            styles["Normal"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"{lang['resp_before']} {before_clean}<br/>{lang['resp_after']} {after_clean}<br/>{lang['resp_removed']} {before_clean - after_clean}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Tables (Conditional)
        if include_normality: add_table(lang["normality_header"], result_norm, lang["desc_var"])
        if include_demo: 
            add_table(lang["age_dist_header"].strip('*'), age_demo_df, age_demo_df.columns[0])
            if gender_demo_df is not None: add_table(lang["gender_dist_header"].strip('*'), gender_demo_df, gender_demo_df.columns[0])
        if include_items: add_table(lang["desc_item_header"].strip('#'), desc_items)
        if include_comp: add_table(lang["desc_comp_header"].strip('#'), desc_comp)
        if include_corr and assoc_stats["type"] == "correlation":
            story.append(Paragraph(lang["pdf_include_corr"], styles["Heading3"]))
            story.append(Paragraph(assoc_summary_text, styles["Normal"]))
            # Include correlation strength diagram instruction
            story.append(Paragraph(lang["corr_strength_header"].strip('*'), styles["Normal"]))
            story.append(Paragraph(lang["corr_strength_diagram"], styles["Normal"]))
            story.append(Spacer(1, 10))
        elif include_corr and assoc_stats["type"] == "chi-square":
             story.append(Paragraph(lang["pdf_include_corr"], styles["Heading3"]))
             story.append(Paragraph(assoc_summary_text, styles["Normal"]))
             story.append(Spacer(1, 10))

        
        # 3. COLLECT AND RENDER PLOTS
        
        plot_width = 450
        plot_height = 300
        effective_page_width = 500.0
        col_unit_width = effective_page_width / cols_per_row
        image_render_width = col_unit_width * 0.95 
        
        plots_to_render = []
        
        # 1. Age Group Bar Chart 
        if include_age_plot:
            fig_pdf_age, ax_pdf_age = plt.subplots(figsize=(8, 5))
            age_counts.plot(kind='bar', ax=ax_pdf_age, color='skyblue', edgecolor='black')
            ax_pdf_age.set_title(lang["plot_age_title"])
            ax_pdf_age.set_xlabel(f"Age Group / {LANGUAGES['Indonesia']['age_dist_header'].strip('*')}")
            ax_pdf_age.set_ylabel(lang["desc_freq"])
            ax_pdf_age.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plots_to_render.append(add_plot_to_list(fig_pdf_age, lang["plot_age_title"], temp_imgs, 400, 300))

        # 2. FREQUENCY BAR CHARTS - ALL ITEMS (X1-Y5)
        if include_freq_plot:
            all_items = x_items + y_items
            for var in all_items:
                fig_pdf_bar, ax_pdf_bar = plt.subplots(figsize=(6, 4))
                s_freq = df[var].dropna()
                freq = s_freq.value_counts().sort_index()
                
                labels = [RESPONSE_LABELS.get(int(i), str(int(i))) for i in freq.index.astype(int)]

                ax_pdf_bar.bar(labels, freq.values)
                ax_pdf_bar.set_xlabel(var)
                ax_pdf_bar.set_ylabel(lang["desc_freq"])
                ax_pdf_bar.set_title(lang["plot_freq_title"].format(var=var))
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plots_to_render.append(add_plot_to_list(fig_pdf_bar, lang["plot_freq_title"].format(var=var), temp_imgs, plot_width, plot_height))
                
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
            
            ax_stacked.set_title(lang["plot_stacked_title"])
            ax_stacked.set_xlabel("Survey Item / Item Kuesioner")
            ax_stacked.set_ylabel(lang["desc_perc"])
            legend_labels_short = {i: RESPONSE_LABELS[i].split(' ')[0] for i in range(1, 6)}
            ax_stacked.legend(title="Response Score / Skor Respon", labels=[legend_labels_short[col] for col in freq_data.columns], bbox_to_anchor=(1.05, 1), loc='upper left')
            ax_stacked.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            
            plots_to_render.append(add_plot_to_list(fig_stacked, lang["plot_stacked_title"], temp_imgs, 450, 350))

        # 4. Histogram X_total
        if include_hist_x_plot:
            fig_pdf_hist_x, ax_pdf_hist_x = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["X_total"].dropna()
            ax_pdf_hist_x.hist(d_hist, bins=5, edgecolor="black", color='lightcoral')
            ax_pdf_hist_x.set_title(lang["plot_hist_x_title"])
            ax_pdf_hist_x.set_xlabel("$X_{total}$ Score (FOMO)")
            ax_pdf_hist_x.set_ylabel(lang["desc_freq"])
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_x, lang["plot_hist_x_title"], temp_imgs, plot_width, plot_height))
            
        # 5. Histogram Y_total
        if include_hist_y_plot:
            fig_pdf_hist_y, ax_pdf_hist_y = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["Y_total"].dropna()
            ax_pdf_hist_y.hist(d_hist, bins=5, edgecolor="black", color='lightgreen')
            ax_pdf_hist_y.set_title(lang["plot_hist_y_title"])
            ax_pdf_hist_y.set_xlabel("$Y_{total}$ Score (Addiction)")
            ax_pdf_hist_y.set_ylabel(lang["desc_freq"])
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_y, lang["plot_hist_y_title"], temp_imgs, plot_width, plot_height))

        # 6. Scatterplot X_total vs Y_total
        if include_scatter_plot:
            fig_pdf_sc, ax_pdf_sc = plt.subplots(figsize=(6, 4))
            ax_pdf_sc.scatter(valid_xy["X_total"], valid_xy["Y_total"])
            ax_pdf_sc.set_xlabel("$X_{total}$ (FOMO)")
            ax_pdf_sc.set_ylabel("$Y_{total}$ (Social media addiction)")
            ax_pdf_sc.set_title(lang["plot_scatter_title"])
            plots_to_render.append(add_plot_to_list(fig_pdf_sc, lang["plot_scatter_title"], temp_imgs, plot_width, plot_height))


        # --- RENDERING PLOTS HORIZONTALLY (IN REPORTLAB TABLE) ---
        if plots_to_render:
            story.append(Paragraph(lang["pdf_vis_header"].strip('*'), styles["Heading2"]))
            
            rows = []
            
            for i in range(0, len(plots_to_render), cols_per_row):
                row_plots = plots_to_render[i:i + cols_per_row]
                
                # Row 1: Plot Titles
                title_row = [Paragraph(p['title'], styles['Normal']) for p in row_plots]
                
                # Row 2: Plot Images
                image_row = []
                for p in row_plots:
                    img = RLImage(p['file'], width=image_render_width)
                    image_row.append(img)
                
                # Pad empty columns in the last row
                if len(row_plots) < cols_per_row:
                    diff = cols_per_row - len(row_plots)
                    for _ in range(diff):
                        title_row.append(Paragraph("", styles['Normal']))
                        image_row.append(Spacer(1, 1))
                
                rows.append(title_row)
                rows.append(image_row)
            
            # Create ReportLab table after all rows are collected
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


        # 4. BUILD PDF (TRY/EXCEPT BLOCK)

        try:
            doc.build(story)
            pdf_bytes = buffer.getvalue()
            
            # DOWNLOAD PDF
            st.download_button(
                lang["pdf_download_button"],
                data=pdf_bytes,
                file_name=final_filename, 
                mime="application/pdf",
            )
            st.success(lang["pdf_success"].format(final_filename=final_filename))
            
        except Exception as e:
            st.error(lang["pdf_fail"].format(e=e))
            
        finally:
            # Delete temporary image files
            for path in temp_imgs:
                try:
                    os.remove(path)
                except OSError:
                    pass