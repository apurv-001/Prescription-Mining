import streamlit as st
import pandas as pd
import io
import re
from datetime import datetime, date
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f0f4f8; }

/* ── Sidebar full fix ── */
[data-testid="stSidebar"] {
    background-color: #1a365d !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #243f6a !important;
    border-color: #3a5a8a !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] input {
    background-color: #243f6a !important;
    color: #ffffff !important;
    border-color: #3a5a8a !important;
}
[data-testid="stSidebar"] .stDateInput > div > div {
    background-color: #243f6a !important;
    border-color: #3a5a8a !important;
}
[data-testid="stSidebar"] hr {
    border-color: #3a5a8a !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #93c5fd !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 1rem;
}
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #3a5a8a !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: #ffffff !important;
}

/* ── Header ── */
.main-header {
    background: linear-gradient(135deg, #1a365d 0%, #2d6a9f 100%);
    color: white;
    padding: 1.8rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(26,54,93,0.3);
}
.main-header h1 { margin: 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.3px; }
.main-header p  { margin: 0.3rem 0 0; opacity: 0.8; font-size: 0.9rem; }

/* ── Cards ── */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
}

/* ── Badges ── */
.badge-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0; }
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.2px;
}
.badge-Radiology     { background:#dbeafe; color:#1e40af; }
.badge-Lab           { background:#d1fae5; color:#065f46; }
.badge-Procedure     { background:#ede9fe; color:#5b21b6; }
.badge-Pharmacy      { background:#fef3c7; color:#92400e; }
.badge-Physiotherapy { background:#fce7f3; color:#9d174d; }
.badge-Admission     { background:#fee2e2; color:#991b1b; }
.badge-Homecare      { background:#f0fdf4; color:#14532d; }
.badge-Consultation  { background:#e0f2fe; color:#0c4a6e; }

/* ── Stat boxes ── */
.stat-box {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.stat-num   { font-size: 1.9rem; font-weight: 700; color: #1a365d; }
.stat-label { font-size: 0.78rem; color: #6b7280; margin-top: 2px; }

/* ── Highlight ── */
.highlight {
    background: #fef9c3;
    border-radius: 3px;
    padding: 0 3px;
    font-weight: 600;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: white;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 500;
    padding: 8px 20px;
}
.stTabs [aria-selected="true"] {
    background-color: #1a365d !important;
    color: white !important;
}

/* ── Upload zone ── */
.upload-zone {
    border: 2px dashed #cbd5e1;
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    background: white;
    transition: border-color 0.2s;
}
.upload-zone:hover { border-color: #2d6a9f; }

/* ── Manual entry card ── */
.manual-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
    border-left: 4px solid #2d6a9f;
}

/* ── Section label ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏥 Discharge Summary Lead Extractor</h1>
    <p>Upload files or enter summaries manually · Keyword matching · Export structured leads · 100% Free</p>
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

HOSPITAL_LIST = [
    "All Hospitals",
    "City General Hospital",
    "Apollo Hospital",
    "Fortis Hospital",
    "Manipal Hospital",
    "AIIMS",
    "Narayana Health",
    "Max Hospital",
    "Medanta",
    "Columbia Asia",
    "Other",
]

DEPARTMENT_LIST = [
    "All Departments",
    "General Medicine",
    "Orthopedics",
    "Cardiology",
    "Neurology",
    "Oncology",
    "Pediatrics",
    "Gynecology & Obstetrics",
    "General Surgery",
    "Urology",
    "Nephrology",
    "Pulmonology",
    "Gastroenterology",
    "Endocrinology",
    "Dermatology",
    "ENT",
    "Ophthalmology",
    "Psychiatry",
    "Emergency Medicine",
    "ICU / Critical Care",
]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Discharge Lead Extractor")
    st.markdown("---")

    # Hospital
    st.markdown("### 🏨 Hospital")
    selected_hospital = st.selectbox(
        "Select Hospital",
        HOSPITAL_LIST,
        label_visibility="collapsed"
    )
    if selected_hospital == "Other":
        custom_hospital = st.text_input("Enter hospital name:", placeholder="Hospital name...")

    # Date Range
    st.markdown("### 📅 Date Range")
    date_from = st.date_input("From", value=date(2024, 1, 1), label_visibility="visible")
    date_to   = st.date_input("To",   value=date.today(),      label_visibility="visible")

    # Department
    st.markdown("### 🏢 Department")
    selected_dept = st.selectbox(
        "Select Department",
        DEPARTMENT_LIST,
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Lead Categories as multiselect dropdown
    st.markdown("### 🏷️ Lead Categories")
    selected_categories = st.multiselect(
        "Active categories",
        options=list(DEFAULT_CATEGORIES.keys()),
        default=list(DEFAULT_CATEGORIES.keys()),
        label_visibility="collapsed"
    )

    # Custom category
    st.markdown("### ➕ Custom Category")
    custom_cat_name = st.text_input("Category name", placeholder="e.g. Respiratory", label_visibility="collapsed")
    custom_cat_kws  = st.text_area("Keywords (comma-separated)", placeholder="e.g. oxygen, nebulizer, inhaler", height=70, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### ⚙️ Options")
    show_keywords   = st.checkbox("Show matched keywords", value=True)
    case_sensitive  = st.checkbox("Case sensitive", value=False)

# Build active categories
active_categories = {k: DEFAULT_CATEGORIES[k] for k in selected_categories}
if custom_cat_name.strip() and custom_cat_kws.strip():
    active_categories[custom_cat_name.strip()] = [kw.strip() for kw in custom_cat_kws.split(",") if kw.strip()]

# ── Core logic ────────────────────────────────────────────────────────────────
def extract_leads(summary, categories, case_sensitive=False):
    text = summary if case_sensitive else summary.lower()
    sentences = re.split(r'[.!?\n;]+', summary)
    leads = []
    for category, keywords in categories.items():
        matched_kws, matched_sents = [], []
        for kw in keywords:
            skw = kw if case_sensitive else kw.lower()
            if skw in text:
                matched_kws.append(kw.strip())
                for sent in sentences:
                    chk = sent if case_sensitive else sent.lower()
                    if skw in chk and sent.strip() and sent.strip() not in matched_sents:
                        matched_sents.append(sent.strip())
        if matched_kws:
            leads.append({
                "category": category,
                "matched_keywords": ", ".join(sorted(set(matched_kws))),
                "context": " | ".join(matched_sents[:2]),
            })
    return leads


def highlight_keywords(text, categories, case_sensitive):
    all_kws = sorted([kw for kws in categories.values() for kw in kws], key=len, reverse=True)
    result  = text
    flags   = 0 if case_sensitive else re.IGNORECASE
    for kw in all_kws:
        result = re.sub(re.escape(kw),
                        lambda m: f'<span class="highlight">{m.group()}</span>',
                        result, flags=flags)
    return result


def detect_columns(df):
    id_cands  = ["patient id","patient_id","patientid","id","mrn","patient no","pid","patient number"]
    sum_cands = ["discharge summary","summary","discharge_summary","notes","clinical notes","report","text"]
    id_col = sum_col = None
    for col in df.columns:
        cl = col.strip().lower()
        if cl in id_cands  and id_col  is None: id_col  = col
        if cl in sum_cands and sum_col is None: sum_col = col
    return id_col, sum_col


def render_results(results, active_categories, show_keywords, case_sensitive):
    total_leads         = sum(len(r["leads"]) for r in results)
    patients_with_leads = sum(1 for r in results if r["leads"])
    all_cats            = [l["category"] for r in results for l in r["leads"]]
    top_cat             = max(set(all_cats), key=all_cats.count) if all_cats else "—"

    st.markdown("### 📊 Summary")
    s1, s2, s3, s4 = st.columns(4)
    for col, num, label in [
        (s1, len(results),       "Patients Processed"),
        (s2, patients_with_leads,"With Leads"),
        (s3, total_leads,        "Total Leads"),
        (s4, top_cat,            "Top Category"),
    ]:
        col.markdown(f"""
        <div class="stat-box">
            <div class="stat-num">{num}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    if all_cats:
        st.markdown("### 📈 Leads by Category")
        cat_df = pd.DataFrame(Counter(all_cats).items(), columns=["Category","Count"]).sort_values("Count", ascending=False)
        st.bar_chart(cat_df.set_index("Category"))
    else:
        cat_df = pd.DataFrame(columns=["Category","Count"])

    st.markdown("### 🧑‍⚕️ Patient Results")
    search = st.text_input("🔎 Filter by Patient ID or Category:", placeholder="Type to filter…", key="search_results")

    for r in results:
        pid, leads = r["patient_id"], r["leads"]
        if search.strip():
            s = search.lower()
            if s not in pid.lower() and not any(s in l["category"].lower() for l in leads):
                continue
        label = f"Patient {pid} — {len(leads)} lead(s)" if leads else f"Patient {pid} — No leads"
        with st.expander(label, expanded=False):
            if not leads:
                st.info("No matching leads found.")
            else:
                badge_html = '<div class="badge-row">'
                for lead in leads:
                    cls = lead["category"].split("/")[0].strip().replace(" ","")
                    badge_html += f'<span class="badge badge-{cls}">{lead["category"]}</span>'
                badge_html += '</div><br>'
                st.markdown(badge_html, unsafe_allow_html=True)

                cols = ["category","matched_keywords","context"] if show_keywords else ["category","context"]
                ldf  = pd.DataFrame(leads)[cols]
                ldf.columns = [c.replace("_"," ").title() for c in cols]
                st.dataframe(ldf, use_container_width=True, hide_index=True)

            st.markdown("**Original Summary (highlighted keywords):**")
            hl = highlight_keywords(r["summary"], active_categories, case_sensitive)
            st.markdown(
                f'<div style="background:#f8fafc;padding:0.8rem 1rem;border-radius:8px;'
                f'border-left:3px solid #2d6a9f;font-size:0.9rem;line-height:1.7">{hl}</div>',
                unsafe_allow_html=True)

    # Export
    st.markdown("### 💾 Export Results")
    rows = []
    for r in results:
        meta = {
            "Hospital":   selected_hospital,
            "Department": selected_dept,
            "Date From":  str(date_from),
            "Date To":    str(date_to),
        }
        if not r["leads"]:
            rows.append({"Patient ID": r["patient_id"], "Category":"", "Matched Keywords":"", "Context":"", "Lead Count":0, **meta})
        else:
            for lead in r["leads"]:
                rows.append({"Patient ID": r["patient_id"], "Category": lead["category"],
                             "Matched Keywords": lead["matched_keywords"], "Context": lead["context"],
                             "Lead Count": len(r["leads"]), **meta})
    export_df = pd.DataFrame(rows)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Download CSV", export_df.to_csv(index=False).encode(),
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


# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_upload, tab_manual = st.tabs(["📂  Upload File", "✏️  Manual Entry"])

# ════════════════════════════════════════════════════════════
# TAB 1 — FILE UPLOAD
# ════════════════════════════════════════════════════════════
with tab_upload:
    col_up, col_info = st.columns([2, 1])

    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Excel or CSV",
            type=["xlsx", "xls", "csv"],
            help="Must contain a Patient ID column and a Discharge Summary column",
            label_visibility="collapsed"
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

    if not uploaded_file:
        st.markdown("""
        <div class="upload-zone">
            <div style="font-size:3rem">📂</div>
            <h3 style="color:#1a365d;margin:0.5rem 0">Upload your discharge summary file</h3>
            <p style="color:#64748b">Supports Excel (.xlsx, .xls) and CSV formats</p>
        </div>
        """, unsafe_allow_html=True)

        sample_df = pd.DataFrame({
            "Patient ID": ["PT001","PT002","PT003"],
            "Discharge Summary": [
                "Patient advised to perform limb elevation exercises. Take Paracetamol 500mg twice daily. Come for review after 7 days.",
                "Order MRI of right knee. Blood tests including CBC and LFT. Start Physiotherapy for rehabilitation. Wound dressing at home.",
                "Discharged post appendectomy. Prescribed antibiotics for 5 days. Ultrasound abdomen after 2 weeks. OPD follow-up in 10 days."
            ]
        })
        st.download_button("📥 Download Sample Template",
                           sample_df.to_csv(index=False).encode(),
                           "sample_discharge_template.csv", "text/csv")
    else:
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

        if st.button("🔍  Extract Leads from File", type="primary", use_container_width=True):
            results  = []
            progress = st.progress(0, text="Starting…")
            total    = len(df)
            for i, row in df.iterrows():
                pid     = str(row[id_col])
                summary = str(row[summary_col])
                progress.progress((i+1)/total, text=f"Processing {i+1}/{total} — Patient {pid}")
                if not summary.strip() or summary.lower() in ["nan","none",""]:
                    results.append({"patient_id": pid, "summary": summary, "leads": []})
                    continue
                results.append({"patient_id": pid, "summary": summary,
                                 "leads": extract_leads(summary, active_categories, case_sensitive)})
            progress.progress(1.0, text="✅ Done!")
            render_results(results, active_categories, show_keywords, case_sensitive)


# ════════════════════════════════════════════════════════════
# TAB 2 — MANUAL ENTRY
# ════════════════════════════════════════════════════════════
with tab_manual:
    st.markdown("### ✏️ Enter Patient Summaries Manually")
    st.markdown("Add one or more patients below, then click **Extract Leads**.")

    # Session state for dynamic rows
    if "manual_rows" not in st.session_state:
        st.session_state.manual_rows = [{"id": "PT001", "dept": "General Medicine", "summary": ""}]

    def add_row():
        n = len(st.session_state.manual_rows) + 1
        st.session_state.manual_rows.append({"id": f"PT{n:03d}", "dept": "General Medicine", "summary": ""})

    def remove_row(idx):
        if len(st.session_state.manual_rows) > 1:
            st.session_state.manual_rows.pop(idx)

    # Render rows
    for i, row_data in enumerate(st.session_state.manual_rows):
        st.markdown(f'<div class="manual-card">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1.5, 2, 5, 0.6])
        with c1:
            st.session_state.manual_rows[i]["id"] = st.text_input(
                "Patient ID", value=row_data["id"],
                key=f"pid_{i}", label_visibility="visible"
            )
        with c2:
            dept_idx = DEPARTMENT_LIST.index(row_data["dept"]) if row_data["dept"] in DEPARTMENT_LIST else 0
            st.session_state.manual_rows[i]["dept"] = st.selectbox(
                "Department", DEPARTMENT_LIST,
                index=dept_idx, key=f"dept_{i}", label_visibility="visible"
            )
        with c3:
            st.session_state.manual_rows[i]["summary"] = st.text_area(
                "Discharge Summary", value=row_data["summary"],
                placeholder="Type or paste discharge summary here…",
                height=100, key=f"summary_{i}", label_visibility="visible"
            )
        with c4:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{i}", help="Remove this row"):
                remove_row(i)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    col_add, col_extract = st.columns([1, 3])
    with col_add:
        if st.button("➕  Add Patient", use_container_width=True):
            add_row()
            st.rerun()
    with col_extract:
        if st.button("🔍  Extract Leads from Manual Entries", type="primary", use_container_width=True):
            valid_rows = [r for r in st.session_state.manual_rows if r["summary"].strip()]
            if not valid_rows:
                st.warning("Please enter at least one discharge summary.")
            else:
                results = []
                for row_data in valid_rows:
                    results.append({
                        "patient_id": row_data["id"] or "Unknown",
                        "summary":    row_data["summary"],
                        "leads":      extract_leads(row_data["summary"], active_categories, case_sensitive)
                    })
                st.markdown("---")
                render_results(results, active_categories, show_keywords, case_sensitive)
