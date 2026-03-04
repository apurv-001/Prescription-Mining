import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Discharge Summary Lead Extractor",
    page_icon="🏥",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f0f4f8; }

.main-header {
    background: linear-gradient(135deg, #1a365d 0%, #2d6a9f 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(26,54,93,0.3);
}
.main-header h1 { margin: 0; font-size: 1.9rem; font-weight: 600; }
.main-header p  { margin: 0.4rem 0 0; opacity: 0.8; font-size: 0.95rem; }

.card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
}

.badge-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
}
.badge-Radiology     { background:#dbeafe; color:#1e40af; }
.badge-Lab           { background:#d1fae5; color:#065f46; }
.badge-Procedure     { background:#ede9fe; color:#5b21b6; }
.badge-Pharmacy      { background:#fef3c7; color:#92400e; }
.badge-Physiotherapy { background:#fce7f3; color:#9d174d; }
.badge-Admission     { background:#fee2e2; color:#991b1b; }
.badge-Homecare      { background:#f0fdf4; color:#14532d; }
.badge-Consultation  { background:#e0f2fe; color:#0c4a6e; }

.stat-box {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.stat-num   { font-size: 2rem; font-weight: 600; color: #1a365d; }
.stat-label { font-size: 0.8rem; color: #6b7280; margin-top: 2px; }

.highlight {
    background: #fef9c3;
    border-radius: 3px;
    padding: 0 2px;
    font-weight: 500;
}

section[data-testid="stSidebar"] { background: #1a365d; }
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCheckbox span { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏥 Discharge Summary Lead Extractor</h1>
    <p>Upload patient discharge summaries · Keyword matching · Export structured leads · 100% Free — No API needed</p>
</div>
""", unsafe_allow_html=True)

# ── Default keyword categories ────────────────────────────────────────────────
DEFAULT_CATEGORIES = {
    "Radiology": [
        "x-ray", "xray", "x ray", "mri", "ct scan", "ct-scan", "ultrasound", "usg",
        "imaging", "scan", "radiograph", "echo", "echocardiogram", "doppler",
        "mammogram", "pet scan", "fluoroscopy", "angiogram", "dexa"
    ],
    "Lab": [
        "blood test", "lab test", "laboratory", "culture", "biopsy", "specimen",
        "urine test", "cbc", "complete blood count", "lft", "liver function",
        "rft", "renal function", "hba1c", "lipid profile", "thyroid",
        "glucose", "haemogram", "hemogram", "serology", "stool test",
        "swab", "pathology", "send sample", "collect sample"
    ],
    "Procedure": [
        "procedure", "dressing", "suture", "stitch", "catheter", "injection",
        "infusion", "dialysis", "endoscopy", "colonoscopy", "bronchoscopy",
        "lumbar puncture", "nebulization", "nebulize",
        "plaster", "cast", "splint", "wound care", "debridement", "drain"
    ],
    "Pharmacy": [
        "tablet", "tab", "capsule", "cap", "syrup", "medication", "medicine",
        "drug", "paracetamol", "antibiotic", "dose", " mg",
        "prescription", "ointment", "cream", "drops", "inhaler",
        "insulin", "steroid", "analgesic", "antipyretic",
        "antihypertensive", "antidiabetic", "antifungal", "antiviral",
        "ibuprofen", "amoxicillin", "metformin", "atorvastatin", "omeprazole",
        "pantoprazole", "aspirin", "clopidogrel", "warfarin", "heparin",
        "salbutamol", "prednisolone", "tramadol", "cetirizine", "loratadine"
    ],
    "Physiotherapy": [
        "physiotherapy", "physio", "physical therapy", "exercise", "rehabilitation",
        "rehab", "limb elevation", "elevate limb", "mobility", "stretching",
        "walking aid", "crutches", "walker", "gait training", "occupational therapy",
        "breathing exercise", "chest physiotherapy", "range of motion",
        "strengthen", "muscle training", "balance training"
    ],
    "Admission": [
        "admit", "admission", "hospitalize", "hospitalise", "inpatient",
        "surgery", "operation", "ot booking", "operation theatre",
        "icu", "intensive care", "ward admission", "elective surgery",
        "plan surgery", "schedule surgery", "surgical intervention"
    ],
    "Homecare": [
        "homecare", "home care", "home visit", "home nurse", "home nursing",
        "dressing at home", "caregiver", "home health", "district nurse",
        "home physiotherapy", "home injection", "home iv", "home oxygen",
        "home nebulization", "self care at home"
    ],
    "Consultation": [
        "review", "consultation", "follow-up", "follow up", "followup",
        "opd", "clinic", "appointment", "outpatient", "specialist",
        "refer", "referral", "second opinion", "come back", "return visit",
        "review after", "come after", "visit after", "see doctor", "consult"
    ],
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Lead Categories")
    st.markdown("Enable / disable categories:")

    enabled = {}
    for cat in DEFAULT_CATEGORIES:
        enabled[cat] = st.checkbox(cat, value=True)

    st.markdown("---")
    st.markdown("### ➕ Custom Category")
    custom_category = st.text_input("Category name:", placeholder="e.g. Respiratory")
    custom_keywords = st.text_area(
        "Keywords (comma-separated):",
        placeholder="e.g. oxygen, nebulizer, inhaler",
        height=80,
    )

    st.markdown("---")
    st.markdown("### 🔧 Options")
    show_matched_words = st.checkbox("Show matched keywords", value=True)
    case_sensitive = st.checkbox("Case sensitive matching", value=False)

# Build active categories
active_categories = {k: v for k, v in DEFAULT_CATEGORIES.items() if enabled.get(k, True)}
if custom_category.strip() and custom_keywords.strip():
    active_categories[custom_category.strip()] = [
        kw.strip() for kw in custom_keywords.split(",") if kw.strip()
    ]

# ── Core extraction logic ─────────────────────────────────────────────────────
def extract_leads(summary: str, categories: dict, case_sensitive: bool = False) -> list[dict]:
    text = summary if case_sensitive else summary.lower()
    sentences = re.split(r'[.!?\n;]+', summary)
    leads = []

    for category, keywords in categories.items():
        matched_kws = []
        matched_sentences = []

        for kw in keywords:
            search_kw = kw if case_sensitive else kw.lower()
            if search_kw in text:
                matched_kws.append(kw.strip())
                for sent in sentences:
                    check = sent if case_sensitive else sent.lower()
                    if search_kw in check and sent.strip():
                        if sent.strip() not in matched_sentences:
                            matched_sentences.append(sent.strip())

        if matched_kws:
            leads.append({
                "category": category,
                "matched_keywords": ", ".join(sorted(set(matched_kws))),
                "context": " | ".join(matched_sentences[:2]),
            })

    return leads


def highlight_keywords(text: str, categories: dict, case_sensitive: bool) -> str:
    all_kws = sorted(
        [kw for kws in categories.values() for kw in kws],
        key=len, reverse=True
    )
    result = text
    flags = 0 if case_sensitive else re.IGNORECASE
    for kw in all_kws:
        result = re.sub(
            re.escape(kw),
            lambda m: f'<span class="highlight">{m.group()}</span>',
            result,
            flags=flags
        )
    return result


def detect_columns(df):
    id_candidates = ["patient id", "patient_id", "patientid", "id", "mrn", "patient no", "pid", "patient number"]
    summary_candidates = ["discharge summary", "summary", "discharge_summary", "notes", "clinical notes", "report", "text"]
    id_col, summary_col = None, None
    for col in df.columns:
        cl = col.strip().lower()
        if cl in id_candidates and id_col is None:
            id_col = col
        if cl in summary_candidates and summary_col is None:
            summary_col = col
    return id_col, summary_col


def build_export_df(results):
    rows = []
    for r in results:
        if not r["leads"]:
            rows.append({
                "Patient ID": r["patient_id"],
                "Category": "",
                "Matched Keywords": "",
                "Context": "",
                "Lead Count": 0,
            })
        else:
            for lead in r["leads"]:
                rows.append({
                    "Patient ID": r["patient_id"],
                    "Category": lead["category"],
                    "Matched Keywords": lead["matched_keywords"],
                    "Context": lead["context"],
                    "Lead Count": len(r["leads"]),
                })
    return pd.DataFrame(rows)

# ── File upload ───────────────────────────────────────────────────────────────
col_up, col_info = st.columns([2, 1])

with col_up:
    uploaded_file = st.file_uploader(
        "Upload Excel or CSV",
        type=["xlsx", "xls", "csv"],
        help="Must contain a Patient ID column and a Discharge Summary column"
    )

with col_info:
    st.markdown("""
    <div class="card">
        <strong>📋 Expected Format</strong><br><br>
        Your file needs at least:<br>
        • <code>Patient ID</code> column<br>
        • <code>Discharge Summary</code> column<br><br>
        <span style="font-size:0.82rem;color:#6b7280">Column names are auto-detected</span>
    </div>
    """, unsafe_allow_html=True)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    st.success(f"✅ Loaded **{len(df)} rows** from `{uploaded_file.name}`")

    id_col, summary_col = detect_columns(df)

    with st.expander("🗂️ Column Mapping", expanded=(not id_col or not summary_col)):
        c1, c2 = st.columns(2)
        with c1:
            id_col = st.selectbox("Patient ID column:", df.columns.tolist(),
                                  index=df.columns.tolist().index(id_col) if id_col else 0)
        with c2:
            summary_col = st.selectbox("Discharge Summary column:", df.columns.tolist(),
                                       index=df.columns.tolist().index(summary_col) if summary_col else min(1, len(df.columns)-1))

    with st.expander("👁️ Data Preview"):
        st.dataframe(df[[id_col, summary_col]].head(5), use_container_width=True)

    st.markdown("---")

    if st.button("🔍 Extract Leads", type="primary", use_container_width=True):
        results = []
        progress = st.progress(0, text="Starting...")
        total = len(df)

        for i, row in df.iterrows():
            patient_id = str(row[id_col])
            summary = str(row[summary_col])
            progress.progress((i + 1) / total, text=f"Processing {i+1}/{total} — Patient {patient_id}")

            if not summary.strip() or summary.lower() in ["nan", "none", ""]:
                results.append({"patient_id": patient_id, "summary": summary, "leads": []})
                continue

            leads = extract_leads(summary, active_categories, case_sensitive)
            results.append({"patient_id": patient_id, "summary": summary, "leads": leads})

        progress.progress(1.0, text="✅ Done!")

        # ── Stats ─────────────────────────────────────────────────────────
        total_leads = sum(len(r["leads"]) for r in results)
        patients_with_leads = sum(1 for r in results if r["leads"])
        all_cats = [l["category"] for r in results for l in r["leads"]]
        top_cat = max(set(all_cats), key=all_cats.count) if all_cats else "—"

        st.markdown("### 📊 Summary")
        s1, s2, s3, s4 = st.columns(4)
        for col, num, label in [
            (s1, total, "Patients Processed"),
            (s2, patients_with_leads, "With Leads"),
            (s3, total_leads, "Total Leads"),
            (s4, top_cat, "Top Category"),
        ]:
            col.markdown(f"""
            <div class="stat-box">
                <div class="stat-num">{num}</div>
                <div class="stat-label">{label}</div>
            </div>""", unsafe_allow_html=True)

        # ── Chart ─────────────────────────────────────────────────────────
        if all_cats:
            st.markdown("### 📈 Leads by Category")
            cat_df = pd.DataFrame(Counter(all_cats).items(), columns=["Category", "Count"]).sort_values("Count", ascending=False)
            st.bar_chart(cat_df.set_index("Category"))
        else:
            cat_df = pd.DataFrame(columns=["Category", "Count"])

        # ── Per-patient results ───────────────────────────────────────────
        st.markdown("### 🧑‍⚕️ Patient Results")
        search = st.text_input("🔎 Filter by Patient ID or Category:", placeholder="Type to filter...")

        for r in results:
            pid = r["patient_id"]
            leads = r["leads"]

            if search.strip():
                s = search.lower()
                if s not in pid.lower() and not any(s in l["category"].lower() for l in leads):
                    continue

            label = f"Patient {pid} — {len(leads)} lead(s)" if leads else f"Patient {pid} — No leads"
            with st.expander(label, expanded=False):
                if not leads:
                    st.info("No matching leads found for this summary.")
                else:
                    badge_html = '<div class="badge-row">'
                    for lead in leads:
                        cls = lead["category"].split("/")[0].strip().replace(" ", "")
                        badge_html += f'<span class="badge badge-{cls}">{lead["category"]}</span>'
                    badge_html += '</div><br>'
                    st.markdown(badge_html, unsafe_allow_html=True)

                    cols_to_show = ["category", "matched_keywords", "context"] if show_matched_words else ["category", "context"]
                    leads_df = pd.DataFrame(leads)[cols_to_show]
                    leads_df.columns = [c.replace("_", " ").title() for c in cols_to_show]
                    st.dataframe(leads_df, use_container_width=True, hide_index=True)

                st.markdown("**Original Summary (highlighted keywords):**")
                highlighted = highlight_keywords(r["summary"], active_categories, case_sensitive)
                st.markdown(
                    f'<div style="background:#f8fafc;padding:0.8rem 1rem;border-radius:8px;'
                    f'border-left:3px solid #2d6a9f;font-size:0.9rem;line-height:1.6">{highlighted}</div>',
                    unsafe_allow_html=True
                )

        # ── Export ────────────────────────────────────────────────────────
        st.markdown("### 💾 Export Results")
        export_df = build_export_df(results)

        c1, c2 = st.columns(2)
        with c1:
            csv_bytes = export_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv_bytes,
                               f"leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                               "text/csv", use_container_width=True)
        with c2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Leads")
                if not cat_df.empty:
                    cat_df.to_excel(writer, index=False, sheet_name="Category Summary")
            st.download_button("⬇️ Download Excel", buf.getvalue(),
                               f"leads_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)

else:
    st.markdown("""
    <div class="card" style="text-align:center;padding:3rem 2rem;border:2px dashed #cbd5e1;">
        <div style="font-size:3rem">📂</div>
        <h3 style="color:#1a365d;margin:0.5rem 0">Upload your discharge summary file</h3>
        <p style="color:#64748b">Supports Excel (.xlsx, .xls) and CSV formats</p>
    </div>
    """, unsafe_allow_html=True)

    sample_df = pd.DataFrame({
        "Patient ID": ["PT001", "PT002", "PT003"],
        "Discharge Summary": [
            "Patient advised to perform limb elevation exercises. Take Paracetamol 500mg twice daily. Come for review after 7 days for follow-up consultation.",
            "Order MRI of right knee. Blood tests including CBC and LFT. Start Physiotherapy for knee rehabilitation. Wound dressing to be done at home.",
            "Patient discharged post appendectomy. Prescribed antibiotics for 5 days. Ultrasound abdomen after 2 weeks. OPD follow-up in 10 days."
        ]
    })
    st.download_button(
        "📥 Download Sample Template",
        sample_df.to_csv(index=False).encode("utf-8"),
        "sample_discharge_template.csv",
        "text/csv"
    )
