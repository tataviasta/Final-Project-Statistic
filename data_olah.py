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
# GANTI DENGAN NAMA ASLI KALIAN
st.sidebar.write("- Delon Raphael Andianto (004202200050)")
st.sidebar.write("- Kallista Viasta (004202200039)")
st.sidebar.write("- Nabila Putri Amalia (004202200049)")
st.sidebar.write("- Pingkan R G Lumingkewas (004202200035)")

# ------------------------------------------------------------------
# 1. UPLOAD DATASET
# ------------------------------------------------------------------
st.subheader("1. Upload Dataset")

uploaded = st.file_uploader(
    "Upload file CSV atau Excel (export Google Form):",
    type=["csv", "xlsx"]
)

if uploaded is None:
    st.info("Silakan upload dataset terlebih dahulu.")
    st.stop()

if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

st.write("Preview data (5 baris pertama, sebelum cleaning usia):")
st.dataframe(df.head())

with st.expander("Lihat semua nama kolom (header):"):
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

st.write("**Distribusi kelompok usia (Age_Group):**")
st.dataframe(df["Age_Group"].value_counts().rename("Number of respondents"))

st.write("Preview data after cleaning & age grouping:")
st.dataframe(df.head())

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
        "FOMO (X) – pilih item:",
        options=fixed_x_all,
        default=fixed_x_all,
        help="Hanya X1–X5 (sesuai kuesioner).",
    )
    st.markdown("**Selected FOMO items:**")
    for code in x_items:
        st.caption(f"**{code}** — {FOMO_LABELS[code]}")

with cB:
    y_items = st.multiselect(
        "Social Media Addiction (Y) – pilih item:",
        options=fixed_y_all,
        default=fixed_y_all,
        help="Hanya Y1–Y5 (sesuai kuesioner).",
    )
    st.markdown("**Selected Addiction items:**")
    for code in y_items:
        st.caption(f"**{code}** — {ADDICTION_LABELS[code]}")

if len(x_items) == 0 or len(y_items) == 0:
    st.warning("Pilih minimal 1 item X dan 1 item Y.")
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

m1, m2, m3 = st.columns(3)
m1.metric("Valid respondents (after age filter)", n_valid)
m2.metric("Average FOMO (X_total)", f"{mean_x:.2f}")
m3.metric("Average Addiction (Y_total)", f"{mean_y:.2f}")

# ------------------------------------------------------------------
# 5. HELPER – DESCRIPTIVE TABLE
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

# ------------------------------------------------------------------
# 6. ASSOCIATION METHOD – CHOOSE ONE
# ------------------------------------------------------------------
st.subheader("4. Association Analysis – Choose One Method")

assoc_method = st.radio(
    "Association method for X and Y:",
    ["Pearson Correlation", "Spearman Rank Correlation", "Chi-square Test (categorical X & Y)"],
    index=0,
)

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
tab_desc, tab_vis, tab_assoc, tab_pdf = st.tabs(
    ["📋 Descriptive Statistics", "📈 Visualizations", "🔗 Association", "📄 PDF Report"]
)

# ------------------ TAB DESCRIPTIVES ------------------
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

# ------------------ TAB VISUALS ------------------
with tab_vis:
    st.markdown("### 6.1 Histogram")

    var_plot = st.selectbox(
        "Choose variable for histogram:",
        x_items + y_items + ["X_total", "Y_total"],
        key="plot_var",
    )
    data_plot = df[var_plot].dropna()

    fig_var, ax_var = plt.subplots()
    ax_var.hist(data_plot, bins=5, edgecolor="black")
    ax_var.set_title(f"Histogram of {var_plot}")
    ax_var.set_xlabel(var_plot)
    ax_var.set_ylabel("Frequency")

    st.pyplot(fig_var)

    buf_var = io.BytesIO()
    fig_var.savefig(buf_var, format="png", bbox_inches="tight")
    buf_var.seek(0)
    st.download_button(
        "Download histogram as PNG",
        data=buf_var,
        file_name=f"{var_plot}_histogram.png",
        mime="image/png",
    )
    plt.close(fig_var)

    st.markdown("### 6.2 Scatterplot X_total vs Y_total")
    fig_scatter, ax_scatter = plt.subplots()
    ax_scatter.scatter(valid_xy["X_total"], valid_xy["Y_total"])
    ax_scatter.set_xlabel("X_total (FOMO)")
    ax_scatter.set_ylabel("Y_total (Social media addiction)")
    ax_scatter.set_title("Scatterplot of X_total vs Y_total")
    st.pyplot(fig_scatter)

    buf_scat = io.BytesIO()
    fig_scatter.savefig(buf_scat, format="png", bbox_inches="tight")
    buf_scat.seek(0)
    st.download_button(
        "Download scatterplot as PNG",
        data=buf_scat,
        file_name="scatter_X_total_Y_total.png",
        mime="image/png",
    )
    plt.close(fig_scatter)

# ------------------ TAB ASSOCIATION ------------------
with tab_assoc:
    st.markdown("### 7. Association Analysis Result")

    if assoc_stats.get("type") == "correlation":
        st.write(f"**Method:** {assoc_stats['method']} Correlation")
        st.write(f"**Correlation coefficient (r):** {assoc_stats['r']:.3f}")
        st.write(f"**p-value:** {assoc_stats['p']:.4f}")
        st.write(
            f"**Interpretation:** {assoc_stats['direction']}, "
            f"{assoc_stats['strength']}, and {assoc_stats['signif_text']}."
        )
    else:
        st.write("**Method:** Chi-square Test")
        st.write(f"**X variable:** {assoc_stats['x']}")
        st.write(f"**Y variable:** {assoc_stats['y']}")
        st.write(f"**Chi-square (χ²):** {assoc_stats['chi2']:.3f}")
        st.write(f"**df:** {assoc_stats['dof']}")
        st.write(f"**p-value:** {assoc_stats['p']:.4f}")
        st.write(f"**Interpretation:** {assoc_stats['signif_text']}.")

    st.markdown("**Summary (bisa langsung dipakai di laporan):**")
    st.write(assoc_summary_text)

# ------------------ TAB PDF REPORT ------------------
with tab_pdf:
    st.markdown("### 8. Export PDF Report")

    st.write("Pilih konten yang ingin dimasukkan ke PDF:")

    include_items = st.checkbox("Descriptive statistics – items (X & Y)", value=True)
    include_comp = st.checkbox("Descriptive statistics – composite scores (X_total & Y_total)", value=True)
    include_corr = st.checkbox("Association analysis summary", value=True)
    include_freq_plot = st.checkbox("Frequency bar chart", value=True)
    include_hist_plot = st.checkbox("Histogram (one variable)", value=True)
    include_scatter_plot = st.checkbox("Scatterplot X_total vs Y_total", value=True)

    pdf_var_freq = var_freq
    pdf_var_plot = var_plot

    if st.button("Generate PDF Report"):
        styles = getSampleStyleSheet()
        story = []

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
        story.append(Paragraph("Member 1, Member 2, Member 3, Member 4", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Info cleaning usia + grouping
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

        if include_items:
            add_table("Descriptive Statistics – Selected Items", desc_items)

        if include_comp:
            add_table("Descriptive Statistics – Composite Scores (X_total & Y_total)", desc_comp)

        if include_corr:
            story.append(Paragraph("Association Analysis Summary", styles["Heading3"]))
            story.append(Paragraph(assoc_summary_text, styles["Normal"]))
            story.append(Spacer(1, 10))

        temp_imgs = []

        # Bar chart
        if include_freq_plot:
            fig_pdf_bar, ax_pdf_bar = plt.subplots()
            ax_pdf_bar.bar(freq.index.astype(str), freq.values)
            ax_pdf_bar.set_xlabel(pdf_var_freq)
            ax_pdf_bar.set_ylabel("Frequency")
            ax_pdf_bar.set_title(f"Frequency of {pdf_var_freq}")
            tmp_bar = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_pdf_bar.savefig(tmp_bar.name, bbox_inches="tight")
            plt.close(fig_pdf_bar)
            temp_imgs.append(tmp_bar.name)

            story.append(Paragraph(f"Frequency Bar Chart – {pdf_var_freq}", styles["Heading3"]))
            story.append(RLImage(tmp_bar.name, width=400, height=300))
            story.append(Spacer(1, 10))

        # Histogram
        if include_hist_plot:
            fig_pdf_hist, ax_pdf_hist = plt.subplots()
            d_hist = df[pdf_var_plot].dropna()
            ax_pdf_hist.hist(d_hist, bins=5, edgecolor="black")
            ax_pdf_hist.set_title(f"Histogram of {pdf_var_plot}")
            ax_pdf_hist.set_xlabel(pdf_var_plot)
            ax_pdf_hist.set_ylabel("Frequency")
            tmp_hist = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_pdf_hist.savefig(tmp_hist.name, bbox_inches="tight")
            plt.close(fig_pdf_hist)
            temp_imgs.append(tmp_hist.name)

            story.append(Paragraph(f"Histogram of {pdf_var_plot}", styles["Heading3"]))
            story.append(RLImage(tmp_hist.name, width=400, height=300))
            story.append(Spacer(1, 10))

        # Scatterplot
        if include_scatter_plot:
            fig_pdf_sc, ax_pdf_sc = plt.subplots()
            ax_pdf_sc.scatter(valid_xy["X_total"], valid_xy["Y_total"])
            ax_pdf_sc.set_xlabel("X_total (FOMO)")
            ax_pdf_sc.set_ylabel("Y_total (Social media addiction)")
            ax_pdf_sc.set_title("Scatterplot of X_total vs Y_total")
            tmp_sc = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig_pdf_sc.savefig(tmp_sc.name, bbox_inches="tight")
            plt.close(fig_pdf_sc)
            temp_imgs.append(tmp_sc.name)

            story.append(Paragraph("Scatterplot X_total vs Y_total", styles["Heading3"]))
            story.append(RLImage(tmp_sc.name, width=400, height=300))
            story.append(Spacer(1, 10))

        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(tmp_pdf.name)
        doc.build(story)

        with open(tmp_pdf.name, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name="survey_analysis_report.pdf",
            mime="application/pdf",
        )

        for path in temp_imgs:
            try:
                os.remove(path)
            except OSError:
                pass
