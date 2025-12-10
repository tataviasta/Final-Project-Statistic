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

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="FOMO & Social Media Addiction – Group 3",
    layout="wide"
)

st.title("📊 The Relationship between Fear of Missing Out (FOMO) and Social Media Addiction among Generation Z ")
st.caption("Statistics 1 • Class 1")

# ------------------------------------------------------------------
# SIDEBAR – GROUP MEMBERS
# ------------------------------------------------------------------
st.sidebar.header("👥 Group Members")
st.sidebar.write("- Delon Raphael Andianto (004202200050)")
st.sidebar.write("- Kallista Viasta (004202200039)")
st.sidebar.write("- Nabila Putri Amalia (004202200049)")
st.sidebar.write("- Pingkan R G Lumingkewas (004202200035)")

# ------------------------------------------------------------------
# 1. UPLOAD DATASET
# ------------------------------------------------------------------
st.subheader("1. Upload Dataset")

uploaded = st.file_uploader(
    "Upload a CSV or Excel file:",
    type=["csv", "xlsx"]
)

if uploaded is None:
    st.info("Silakan upload dataset terlebih dahulu.")
    st.stop()

if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

st.write("Preview data (The first 5 lines, before age cleaning):")
st.dataframe(df.head())

with st.expander("See all column names (headers):"):
    st.write(list(df.columns))

# ------------------------------------------------------------------
# 1A. DATA CLEANING – PAKAI KATEGORI UMUR 13–18 / 19–23 / 24–28
# ------------------------------------------------------------------
st.subheader("Data Cleaning – Filter Usia & Pengelompokan")

# Deteksi kolom umur otomatis (mengandung 'age' atau 'umur')
AGE_COLUMN = None
for col in df.columns:
    col_lower = str(col).lower()
    if "age" in col_lower or "umur" in col_lower:
        AGE_COLUMN = col
        break

if AGE_COLUMN is None:
    st.error(
        "Kolom usia tidak ditemukan. Pastikan ada kolom dengan nama mengandung 'Age' atau 'Umur'."
    )
    st.stop()

st.write(f"Kolom usia terdeteksi sebagai: **{AGE_COLUMN}**")

# Nilai Age di file contoh: string kategori, misalnya:
# '13–18 years / tahun', '19–23 years / tahun', '24–28 years / tahun',
# juga bisa ada '< 13 years / tahun' atau '> 28 years / tahun'
allowed_age_categories = [
    "13–18 years / tahun",
    "19–23 years / tahun",
    "24–28 years / tahun",
    # versi dash biasa (jaga-jaga kalau beda di form)
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

st.success("✅ Data cleaning & age grouping completed.")
st.write("**Data Cleaning Summary:**")
st.write(f"- Respondents before cleaning: {before_clean}")
st.write(f"- Respondents after cleaning (13–28 years group only): {after_clean}")
st.write(f"- Removed respondents: {before_clean - after_clean}")

st.write("**Age Group Distribution:**")
st.dataframe(df["Age_Group"].value_counts().rename("Number of respondents"))

st.write("Preview data after cleaning & age grouping:")
st.dataframe(df.head())

# ------------------------------------------------------------------
# DEMOGRAPHIC SUMMARY (Age_Group + optional Gender)
# ------------------------------------------------------------------

# Summary Age_Group (frequency + percentage)
age_counts = df["Age_Group"].value_counts().sort_index()
age_demo_df = pd.DataFrame({
    "Age Group": age_counts.index,
    "Frequency": age_counts.values,
})
age_demo_df["Percentage (%)"] = (age_demo_df["Frequency"] / age_demo_df["Frequency"].sum() * 100).round(2)

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
        "Gender": gender_counts.index,
        "Frequency": gender_counts.values,
    })
    gender_demo_df["Percentage (%)"] = (gender_demo_df["Frequency"] / gender_demo_df["Frequency"].sum() * 100).round(2)

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
        "Beberapa kolom pertanyaan tidak ditemukan.\n\n"
        f"Missing FOMO (X): {missing_x}\n"
        f"Missing Addiction (Y): {missing_y}\n\n"
        "Cara paling aman: ubah header di Excel/Sheets jadi X1..X5 dan Y1..Y5, lalu upload ulang."
    )
    st.write("Header saat ini:", list(df.columns))
    st.stop()

# ------------------------------------------------------------------
# 3. PILIH SUBSET X & Y
# ------------------------------------------------------------------
st.subheader("2. Select Variables X and Y (fixed item set)")

cA, cB = st.columns(2)

with cA:
    x_items = st.multiselect(
        "FOMO (X) – Items Choose:",
        options=fixed_x_all,
        default=fixed_x_all,
        help="Just X1–X5 (Like Questionnaire).",
    )
    st.markdown("**Selected FOMO items:**")
    for code in x_items:
        st.caption(f"**{code}** — {FOMO_LABELS[code]}")

with cB:
    y_items = st.multiselect(
        "Social Media Addiction (Y) – Items Choose:",
        options=fixed_y_all,
        default=fixed_y_all,
        help="Just Y1–Y5 (Like Questionnaire).",
    )
    st.markdown("**Selected Addiction items:**")
    for code in y_items:
        st.caption(f"**{code}** — {ADDICTION_LABELS[code]}")

if len(x_items) == 0 or len(y_items) == 0:
    st.warning("Minimum Choose 1 item X and 1 item Y.")
    st.stop()

for col in x_items + y_items:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------------
# 4. COMPOSITE SCORES
# ------------------------------------------------------------------
st.subheader("3. Composite Scores (X_total & Y_total)")

comp_method = st.radio(
    "Metode composite score:",
    ["Mean of items (recommended)", "Sum of items"],
    horizontal=True,
)

if comp_method.startswith("Mean"):
    df["X_total"] = df[x_items].mean(axis=1)
    df["Y_total"] = df[y_items].mean(axis=1)
else:
    df["X_total"] = df[x_items].sum(axis=1)
    df["Y_total"] = df[y_items].sum(axis=1)

st.success("✅ Composite scores X_total dan Y_total berhasil dibuat.")

valid_xy = df[["X_total", "Y_total"]].dropna()
n_valid = valid_xy.shape[0]
mean_x = valid_xy["X_total"].mean()
mean_y = valid_xy["Y_total"].mean()

# ------------------------------------------------------------------
# NORMALITY TEST (Shapiro–Wilk)
# ------------------------------------------------------------------

st.subheader("Normality Test (Shapiro–Wilk)")

shapiro_x = stats.shapiro(valid_xy["X_total"])
shapiro_y = stats.shapiro(valid_xy["Y_total"])

normal_x = "Normal" if shapiro_x.pvalue >= 0.05 else "Not Normal"
normal_y = "Normal" if shapiro_y.pvalue >= 0.05 else "Not Normal"

st.write("### Result:")

result_norm = pd.DataFrame({
    "Variable": ["X_total", "Y_total"],
    "Shapiro-Wilk Statistic": [shapiro_x.statistic, shapiro_y.statistic],
    "p-value": [shapiro_x.pvalue, shapiro_y.pvalue],
    "Normality": [normal_x, normal_y]
})

st.dataframe(result_norm.round(4))

# Rekomendasi metode berdasarkan normality
if normal_x == "Normal" and normal_y == "Normal":
    recommended_method = "Pearson Correlation"
else:
    recommended_method = "Spearman Rank Correlation"

st.info(f"✅ Recommended association method based on normality test: **{recommended_method}**")

m1, m2, m3 = st.columns(3)
m1.metric("Valid respondents (after age filter)", n_valid)
m2.metric("Average FOMO (X_total)", f"{mean_x:.2f}")
m3.metric("Average Addiction (Y_total)", f"{mean_y:.2f}")

# ------------------------------------------------------------------
# 5. HELPER – DESCRIPTIVE TABLE & BAR CHART ITEM
# ------------------------------------------------------------------
def descriptive_table(data: pd.DataFrame, cols):
    # ... (Fungsi descriptive_table tetap sama) ...
    rows = []
    for col in cols:
        s = data[col].dropna()
        if s.empty:
            continue
        mode_vals = s.mode()
        mode_val = mode_vals.iloc[0] if not mode_vals.empty else np.nan
        rows.append(
            {
                "Variable": col,
                "N": len(s),
                "Mean": s.mean(),
                "Median": s.median(),
                "Mode": mode_val,
                "Min": s.min(),
                "Max": s.max(),
                "Std Dev": s.std(ddof=1),
            }
        )
    return pd.DataFrame(rows).set_index("Variable").round(3)


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
    ax_bar.set_ylabel("Frequency")
    ax_bar.set_title(f"Frequency of {col_name}")
    plt.tight_layout()
    
    # Tampilkan figure di Streamlit
    st.pyplot(fig_bar)

    # Simpan ke buffer untuk download
    buf_bar = io.BytesIO()
    fig_bar.savefig(buf_bar, format="png", bbox_inches="tight")
    buf_bar.seek(0)
    
    # Tampilkan tombol download
    st.download_button(
        f"Download {col_name} Bar Chart as PNG",
        data=buf_bar,
        file_name=f"{col_name}_bar_chart.png",
        mime="image/png",
    )
    plt.close(fig_bar) # Tutup figure untuk membebaskan memori

# ------------------------------------------------------------------
# 6. ASSOCIATION METHOD – CHOOSE ONE
# ------------------------------------------------------------------
st.subheader("4. Association Analysis – Choose One Method")

assoc_method = st.radio(
    "Association method for X and Y (based on normality recommendation):",
    ["Pearson Correlation", "Spearman Rank Correlation", "Chi-square Test (categorical X & Y)"],
    index=0,
)

st.caption(f"Normality-based recommendation: {recommended_method}")

assoc_stats = {}
assoc_summary_text = ""

if assoc_method in ["Pearson Correlation", "Spearman Rank Correlation"]:
    x_corr = valid_xy["X_total"]
    y_corr = valid_xy["Y_total"]

    if assoc_method.startswith("Pearson"):
        r_value, p_value = stats.pearsonr(x_corr, y_corr)
        method_short = "Pearson"
    else:
        r_value, p_value = stats.spearmanr(x_corr, y_corr)
        method_short = "Spearman"

    def interpret_strength(r):
        a = abs(r)
        if a < 0.2:
            return "very weak"
        elif a < 0.4:
            return "weak"
        elif a < 0.6:
            return "moderate"
        elif a < 0.8:
            return "strong"
        else:
            return "very strong"

    direction = "positive" if r_value > 0 else "negative"
    strength = interpret_strength(r_value)
    signif_text = "significant (p < 0.05)" if p_value < 0.05 else "not significant (p ≥ 0.05)"

    assoc_stats = {
        "type": "correlation",
        "method": method_short,
        "r": r_value,
        "p": p_value,
        "direction": direction,
        "strength": strength,
        "signif_text": signif_text,
    }

    assoc_summary_text = (
        f"Using the {method_short} correlation, there is a {direction} and {strength} "
        f"relationship between FOMO (X_total) and social media addiction (Y_total), "
        f"with r = {r_value:.3f} and p = {p_value:.4f}, indicating that the association is "
        f"{signif_text}."
    )

else:
    st.markdown("**Chi-square Test – pilih X dan Y kategorik (Likert).**")
    cat_options = x_items + y_items
    chi_x_col = st.selectbox("Categorical X variable:", cat_options, key="chi_x")
    chi_y_col = st.selectbox("Categorical Y variable:", cat_options, key="chi_y")

    contingency = pd.crosstab(df[chi_x_col], df[chi_y_col])
    chi2_value, p_chi, dof, expected = stats.chi2_contingency(contingency)
    signif_text = "significant (p < 0.05)" if p_chi < 0.05 else "not significant (p ≥ 0.05)"

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
        f"Using the Chi-square test between {chi_x_col} and {chi_y_col}, "
        f"the chi-square statistic is χ² = {chi2_value:.3f} with {dof} degrees of freedom "
        f"and p = {p_chi:.4f}, indicating that the association is {signif_text}."
    )

# ------------------------------------------------------------------
# 7. TABS
# ------------------------------------------------------------------
# Pastikan age_counts sudah dihitung di bagian DEMOGRAPHIC SUMMARY

# Prepare Age Group Bar Chart (for tab_vis & pdf)
fig_age_bar, ax_age_bar = plt.subplots(figsize=(8, 5))
age_counts.plot(kind='bar', ax=ax_age_bar, color='skyblue', edgecolor='black')
ax_age_bar.set_title("Distribution of Respondents by Age Group")
ax_age_bar.set_xlabel("Age Group")
ax_age_bar.set_ylabel("Frequency")
ax_age_bar.tick_params(axis='x', rotation=45)
plt.tight_layout()
buf_age_bar = io.BytesIO()
fig_age_bar.savefig(buf_age_bar, format="png", bbox_inches="tight")
buf_age_bar.seek(0)
# NOTE: fig_age_bar remains open until tab_vis/pdf needs it. (Don't close yet)

# Prepare X_total Histogram (for tab_vis & pdf)
fig_hist_x, ax_hist_x = plt.subplots()
ax_hist_x.hist(valid_xy["X_total"].dropna(), bins=5, edgecolor="black", color='lightcoral')
ax_hist_x.set_title("Histogram of X_total (FOMO)")
ax_hist_x.set_xlabel("X_total Score (FOMO)")
ax_hist_x.set_ylabel("Frequency")
# NOTE: fig_hist_x remains open

# Prepare Y_total Histogram (for tab_vis & pdf)
fig_hist_y, ax_hist_y = plt.subplots()
ax_hist_y.hist(valid_xy["Y_total"].dropna(), bins=5, edgecolor="black", color='lightgreen')
ax_hist_y.set_title("Histogram of Y_total (Social Media Addiction)")
ax_hist_y.set_xlabel("Y_total Score (Addiction)")
ax_hist_y.set_ylabel("Frequency")
# NOTE: fig_hist_y remains open
tab_desc, tab_vis, tab_assoc, tab_pdf = st.tabs(
    ["📋 Descriptive Statistics", "📈 Visualizations", "🔗 Analysis Result", "📄 PDF Report"]
)

# ------------------ TAB DESCRIPTIVES ------------------
with tab_desc:
    st.markdown("### 5.0 Demographic Summary")

    st.markdown("**Age Group Distribution**")
    st.dataframe(age_demo_df)

    if gender_demo_df is not None:
        st.markdown("**Gender Distribution**")
        st.dataframe(gender_demo_df)
    else:
        st.info("Gender column was not detected, so gender distribution is not shown.")
with tab_desc:
    st.markdown("### 5.1 Descriptive Statistics – Each Survey Item")
    desc_items = descriptive_table(df, x_items + y_items)
    st.dataframe(desc_items)

    st.markdown("### 5.2 Descriptive Statistics – Composite Scores (X_total & Y_total)")
    desc_comp = descriptive_table(df, ["X_total", "Y_total"])
    st.dataframe(desc_comp)

    st.markdown("### 5.3 Frequency & Percentage Table")
    var_freq = st.selectbox(
        "Choose variable for frequency table:",
        x_items + y_items + ["X_total", "Y_total"],
        key="freq_var",
    )
    s_freq = df[var_freq].dropna()
    freq = s_freq.value_counts().sort_index()
    perc = (freq / freq.sum() * 100).round(2)
    freq_table = pd.DataFrame({"Frequency": freq, "Percentage (%)": perc})
    st.dataframe(freq_table)

    st.markdown("#### Bar Chart (Frequency)")
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(freq.index.astype(str), freq.values)
    ax_bar.set_xlabel(var_freq)
    ax_bar.set_ylabel("Frequency")
    ax_bar.set_title(f"Frequency of {var_freq}")
    st.pyplot(fig_bar)

    buf_bar = io.BytesIO()
    fig_bar.savefig(buf_bar, format="png", bbox_inches="tight")
    buf_bar.seek(0)
    st.download_button(
        "Download bar chart as PNG",
        data=buf_bar,
        file_name=f"{var_freq}_bar_chart.png",
        mime="image/png",
    )
    plt.close(fig_bar)

# --- Test Result/analysis ------
    st.markdown(f"### 7 Association Analysis ({assoc_method})")

    if assoc_stats["type"] == "correlation":
        st.markdown(f"#### Hasil {assoc_stats['method']} Correlation")
        
        # Tampilkan tabel ringkasan
        corr_data = pd.DataFrame({
            "Metric": ["Correlation Coefficient (r)", "p-value", "Direction", "Strength", "Significance"],
            "Value": [
                f"{assoc_stats['r']:.3f}", 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['direction'].capitalize(), 
                assoc_stats['strength'].capitalize(), 
                assoc_stats['signif_text'].capitalize()
            ]
        }).set_index("Metric")
        
        st.dataframe(corr_data)

        # Tampilkan interpretasi teks
        st.markdown("#### Interpretation:")
        st.success(assoc_summary_text)

        # Tambahkan visualisasi scatterplot (sudah dibahas di visualisasi)
        st.markdown("---")
        st.markdown("#### Visual Check: Scatterplot")
        
        # Buat ulang scatterplot untuk ditampilkan di tab analisis ini
        fig_assoc_scatter, ax_assoc_scatter = plt.subplots()
        ax_assoc_scatter.scatter(valid_xy["X_total"], valid_xy["Y_total"], color='purple', alpha=0.6)
        
        # Tambahkan garis regresi
        m, b = np.polyfit(valid_xy["X_total"], valid_xy["Y_total"], 1)
        ax_assoc_scatter.plot(valid_xy["X_total"], m*valid_xy["X_total"] + b, color='red', linestyle='--')
        
        ax_assoc_scatter.set_xlabel("X_total (FOMO)")
        ax_assoc_scatter.set_ylabel("Y_total (Social media addiction)")
        ax_assoc_scatter.set_title(f"Scatterplot (r={assoc_stats['r']:.3f})")
        st.pyplot(fig_assoc_scatter)
        plt.close(fig_assoc_scatter)

    elif assoc_stats["type"] == "chi-square":
        st.markdown(f"#### Hasil Chi-square Test antara {assoc_stats['x']} dan {assoc_stats['y']}")
        
        chi_data = pd.DataFrame({
            "Metric": ["Chi-square Value ($\chi^2$)", "Degrees of Freedom (dof)", "p-value", "Significance"],
            "Value": [
                f"{assoc_stats['chi2']:.3f}", 
                assoc_stats['dof'], 
                f"{assoc_stats['p']:.4f}", 
                assoc_stats['signif_text'].capitalize()
            ]
        }).set_index("Metric")
        
        st.dataframe(chi_data)
        st.markdown("#### Interpretation:")
        st.success(assoc_summary_text)
        
        st.markdown("---")
        st.markdown("#### Contingency Table")
        contingency = pd.crosstab(df[assoc_stats['x']], df[assoc_stats['y']])
        st.dataframe(contingency)


    else:
        st.warning("Silakan pilih metode asosiasi di bagian **4. Association Analysis** di atas.")

# ------------------ TAB PDF REPORT (FINAL MODIFIED VERSION) ------------------
with tab_pdf:
    st.markdown("### 8. Export PDF Report")

    # 1. TAMBAH INPUT NAMA FILE
    pdf_filename = st.text_input(
        "Nama file PDF yang akan diunduh (tanpa .pdf):",
        value="Laporan_Analisis_FOMO_GenZ"
    )
    
    # 2. TAMBAH PILIHAN JUMLAH GRAFIK HORIZONTAL
    st.markdown("---")
    st.write("**Pengaturan Visualisasi Layout dalam PDF:**")
    cols_per_row = st.radio(
        "Jumlah Grafik per Baris:",
        options=[1, 2, 3], # Opsi 1 (vertikal), 2, atau 3
        index=2, # Default 3
        horizontal=True
    )
    
    st.markdown("---")
    st.write("Pilih konten yang ingin dimasukkan ke PDF:")

    include_items = st.checkbox("Descriptive statistics – items (X & Y)", value=True)
    include_comp = st.checkbox("Descriptive statistics – composite scores (X_total & Y_total)", value=True)
    include_corr = st.checkbox("Association analysis summary", value=True)
    include_demo = st.checkbox("Demographic summary (Age & Gender)", value=True)
    include_normality = st.checkbox("Normality test result (Shapiro–Wilk)", value=True)
    
    st.markdown("---")
    st.markdown("**Visualizations**")
    
    include_freq_plot = st.checkbox("Frequency bar charts (All X and Y items)", value=True) 
    include_hist_x_plot = st.checkbox("Histogram X_total", value=True)
    include_hist_y_plot = st.checkbox("Histogram Y_total", value=True)
    include_scatter_plot = st.checkbox("Scatterplot X_total vs Y_total", value=True)
    include_age_plot = st.checkbox("Demographic bar chart (Age Group)", value=True)


    if st.button("Generate PDF Report"):
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Survey Analysis Report", styles["Title"]))
        story.append(Spacer(1, 12))
        # ... (Kode Data Cleaning, Group Members, dan add_table tetap sama) ...
        # [Bagian ini diabaikan untuk keringkasan, tapi asumsikan add_table dan paragraf awal ada]
        
        # --- LOGIKA KODE UNTUK PEMBUATAN PDF DIMULAI ---

        story.append(Paragraph("Survey Analysis Report", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(
                "FOMO & Social Media Addiction – Statistics 1 (Group 3)",
                styles["Heading2"],
            )
        )
        story.append(Spacer(1, 8))

        story.append(Paragraph("Group Members:", styles["Heading3"]))
        story.append(Paragraph("- Delon Raphael Andianto (004202200050)<br/>- Kallista Viasta (004202200039)<br/>- Nabila Putri Amalia (004202200049)<br/>- Pingkan R G Lumingkewas (004202200035)", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Info cleaning usia + grouping (TIDAK BERUBAH)
        story.append(Paragraph("Data Cleaning (Age Filter & Grouping):", styles["Heading3"]))
        story.append(
            Paragraph(
                "Only respondents whose age category was 13–18 years, 19–23 years, or 24–28 years "
                "were included in the analysis to represent Generation Z. Other age categories "
                "such as below 13 or above 28 years were excluded.",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 8))
        story.append(
            Paragraph(
                f"Respondents before cleaning: {before_clean}<br/>"
                f"Respondents after cleaning: {after_clean}<br/>"
                f"Removed respondents: {before_clean - after_clean}",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        def add_table(title, df_table):
            story.append(Paragraph(title, styles["Heading3"]))
            df_reset = df_table.reset_index()
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

        if include_normality:
            add_table("Normality Test (Shapiro–Wilk)", result_norm)
        
        if include_demo:
            add_table("Demographic Summary – Age Group", age_demo_df)
            if gender_demo_df is not None:
                add_table("Demographic Summary – Gender", gender_demo_df)

        if include_items:
            add_table("Descriptive Statistics – Selected Items", desc_items)

        if include_comp:
            add_table("Descriptive Statistics – Composite Scores (X_total & Y_total)", desc_comp)

        if include_corr:
            story.append(Paragraph("Association Analysis Summary", styles["Heading3"]))
            story.append(Paragraph(assoc_summary_text, styles["Normal"]))
            story.append(Spacer(1, 10))

        temp_imgs = []
        
        # --- HELPER UNTUK GRAFIK HORIZONTAL ---
        
        # Hitung lebar dan tinggi grafik berdasarkan jumlah kolom
        # Lebar halaman standar ReportLab adalah 600 unit
        if cols_per_row == 1:
            plot_width = 450
            plot_height = 300
        elif cols_per_row == 2:
            plot_width = 280
            plot_height = 200
        else: # 3 kolom
            plot_width = 190
            plot_height = 150
            
        def add_plot_to_list(fig, title_text, temp_list, width, height):
            """Saves plot to temp file and returns filename and title."""
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp_file.name, bbox_inches="tight")
            plt.close(fig)
            temp_list.append(tmp_file.name)
            return {'title': title_text, 'file': tmp_file.name, 'width': width, 'height': height}

        
        # --- KUMPULKAN SEMUA GRAFIK YANG DIPILIH KE DALAM LIST ---
        plots_to_render = []

        # 1. Age Group Bar Chart
        if include_age_plot:
            fig_pdf_age, ax_pdf_age = plt.subplots(figsize=(8, 5))
            age_counts.plot(kind='bar', ax=ax_pdf_age, color='skyblue', edgecolor='black')
            ax_pdf_age.set_title("Distribution of Respondents by Age Group")
            ax_pdf_age.set_xlabel("Age Group")
            ax_pdf_age.set_ylabel("Frequency")
            ax_pdf_age.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            plots_to_render.append(add_plot_to_list(fig_pdf_age, "Demographic – Age Group", temp_imgs, 400, 300))

        # 2. FREQUENCY BAR CHARTS - SEMUA ITEM (X1-Y5)
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
                
        # 3. Histogram X_total
        if include_hist_x_plot:
            fig_pdf_hist_x, ax_pdf_hist_x = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["X_total"].dropna()
            ax_pdf_hist_x.hist(d_hist, bins=5, edgecolor="black", color='lightcoral')
            ax_pdf_hist_x.set_title("Histogram X_total (FOMO)")
            ax_pdf_hist_x.set_xlabel("X_total Score (FOMO)")
            ax_pdf_hist_x.set_ylabel("Frequency")
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_x, "Histogram X_total", temp_imgs, plot_width, plot_height))
            
        # 4. Histogram Y_total
        if include_hist_y_plot:
            fig_pdf_hist_y, ax_pdf_hist_y = plt.subplots(figsize=(6, 4))
            d_hist = valid_xy["Y_total"].dropna()
            ax_pdf_hist_y.hist(d_hist, bins=5, edgecolor="black", color='lightgreen')
            ax_pdf_hist_y.set_title("Histogram Y_total (Addiction)")
            ax_pdf_hist_y.set_xlabel("Y_total Score (Addiction)")
            ax_pdf_hist_y.set_ylabel("Frequency")
            plots_to_render.append(add_plot_to_list(fig_pdf_hist_y, "Histogram Y_total", temp_imgs, plot_width, plot_height))

        # 5. Scatterplot X_total vs Y_total
        if include_scatter_plot:
            fig_pdf_sc, ax_pdf_sc = plt.subplots(figsize=(6, 4))
            ax_pdf_sc.scatter(valid_xy["X_total"], valid_xy["Y_total"])
            ax_pdf_sc.set_xlabel("X_total (FOMO)")
            ax_pdf_sc.set_ylabel("Y_total (Social media addiction)")
            ax_pdf_sc.set_title("Scatterplot X_total vs Y_total")
            plots_to_render.append(add_plot_to_list(fig_pdf_sc, "Scatterplot X vs Y", temp_imgs, plot_width, plot_height))


        # --- RENDERING GRAFIK SECARA HORIZONTAL (DALAM TABEL REPORTLAB) ---
        if plots_to_render:
            story.append(Paragraph("Visualizations", styles["Heading2"]))
            
            rows = []
            # Kelompokkan plots_to_render menjadi baris-baris dengan ukuran cols_per_row
            for i in range(0, len(plots_to_render), cols_per_row):
                row_plots = plots_to_render[i:i + cols_per_row]
                
                # Baris 1: Judul Grafik
                title_row = [Paragraph(p['title'], styles['Caption']) for p in row_plots]
                # Baris 2: Gambar Grafik
                image_row = [RLImage(p['file'], width=p['width'], height=p['height']) for p in row_plots]
                
                rows.append(title_row)
                rows.append(image_row)

            # Hitung proporsi lebar kolom (misal 3 kolom, proporsi 33% per kolom)
            col_widths = [None] * cols_per_row
            
            # Buat tabel untuk menampung semua grafik
            tbl = Table(rows, colWidths=col_widths)
            tbl.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.white),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.white),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 10))


        # --- FINALISASI PDF ---
        
        # Buat nama file yang aman dan tambahkan .pdf
        safe_filename = "".join(c for c in pdf_filename if c.isalnum() or c in (' ', '_')).rstrip()
        final_filename = (safe_filename if safe_filename else "Laporan_Analisis") + ".pdf"
        
        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(tmp_pdf.name)
        doc.build(story)

        with open(tmp_pdf.name, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name=final_filename, # Gunakan nama file yang dimasukkan pengguna
            mime="application/pdf",
        )

        # Hapus file sementara
        for path in temp_imgs:
            try:
                os.remove(path)
            except OSError:
                pass