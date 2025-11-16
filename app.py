# app.py
import streamlit as st
import json
from pathlib import Path
import random
import string
from datetime import datetime
import io

# ------------------------------
# Config
# ------------------------------
DATA_FILE = Path("students.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Student Management", page_icon="🎓", layout="wide")

# ------------------------------
# Utility functions
# ------------------------------
def safe_read_data():
    """Return stored list of student dicts. If file missing -> create empty list."""
    try:
        if not DATA_FILE.exists():
            DATA_FILE.write_text("[]", encoding="utf-8")
            return []
        raw = DATA_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        return json.loads(raw)
    except Exception as e:
        st.error(f"Could not read data file: {e}")
        return []

def safe_write_data(data):
    """Write JSON atomically."""
    try:
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(DATA_FILE)
    except Exception as e:
        st.error(f"Could not write data file: {e}")

def generate_student_id():
    """Generate a human-friendly-but-unique ID similar to your CLI."""
    alpha = random.choices(string.ascii_letters, k=7)
    num = random.choices(string.digits, k=4)
    sp = random.choices("!@#$%&", k=1)
    parts = alpha + num + sp
    random.shuffle(parts)
    sid = "".join(parts)
    return sid.capitalize()

def find_student_by_id(data, stuid):
    return next((s for s in data if s.get("studentid") == stuid), None)

def normalize_courses(text):
    # store as comma-separated trimmed values
    parts = [c.strip() for c in text.split(",") if c.strip()]
    return ", ".join(parts)

# ------------------------------
# Data loading (single source of truth)
# ------------------------------
students = safe_read_data()

# Ensure session state holds selected student for update UI
if "selected_student" not in st.session_state:
    st.session_state.selected_student = None

# ------------------------------
# UI layout: sidebar navigation
# ------------------------------
st.sidebar.title("Student Management")
choice = st.sidebar.radio("Choose action", ["Dashboard", "Add Student", "Update / Delete", "Import / Export"])

st.sidebar.markdown("---")
st.sidebar.write("👤 Students saved:", len(students))
st.sidebar.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit • TriAI Labs")

# ------------------------------
# Dashboard (View / Search)
# ------------------------------
if choice == "Dashboard":
    st.title("Students — Dashboard")
    st.markdown("Search, filter and view the students dataset.")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        q = st.text_input("Search (name / email / id)", "")
    with col2:
        min_age = st.number_input("Min age", min_value=0, max_value=150, value=0, step=1)
    with col3:
        show_courses = st.multiselect("Filter by course (select from existing)", options=list({c.strip() for s in students for c in (s.get("courses","") or "").split(",") if c.strip()}))

    # Filtering
    filtered = []
    for s in students:
        match_q = True
        if q:
            qlow = q.lower()
            match_q = qlow in (s.get("name","").lower() + s.get("email","").lower() + s.get("studentid","").lower())
        match_age = s.get("age", 0) >= min_age
        if show_courses:
            sc = [c.strip() for c in (s.get("courses","") or "").split(",")]
            match_courses = all(any(sel.strip().lower() == c.lower() for c in sc) for sel in show_courses)
        else:
            match_courses = True
        if match_q and match_age and match_courses:
            filtered.append(s)

    st.write(f"Showing **{len(filtered)}** / {len(students)} students")
    if filtered:
        # show as table
        df_rows = []
        for s in filtered:
            df_rows.append({
                "Name": s.get("name"),
                "Email": s.get("email"),
                "Age": s.get("age"),
                "Student ID": s.get("studentid"),
                "Courses": s.get("courses"),
                "Grades": s.get("grades"),
            })
        st.dataframe(df_rows, use_container_width=True)

        # quick inspect single student
        with st.expander("Select a student to inspect / quick actions"):
            ids = [s.get("studentid") for s in filtered]
            sel = st.selectbox("Student ID", options=[""] + ids)
            if sel:
                s = find_student_by_id(students, sel)
                if s:
                    st.json(s)
                    st.write("**Actions**")
                    acol1, acol2 = st.columns(2)
                    with acol1:
                        if st.button("Edit this student", key=f"edit_{sel}"):
                            st.session_state.selected_student = sel
                            st.rerun()
                    with acol2:
                        if st.button("Delete this student", key=f"del_{sel}"):
                            # confirm
                            if st.confirm(f"Delete {s.get('name')} ({sel})?"):
                                students.remove(s)
                                safe_write_data(students)
                                st.success("Student deleted.")
                                st.rerun()
    else:
        st.info("No students match the filters or the dataset is empty.")

# ------------------------------
# Add Student form
# ------------------------------
elif choice == "Add Student":
    st.title("Add Student")
    st.markdown("Fill the form and press **Create**. Student ID will be auto-generated.")

    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Full name")
        email = st.text_input("Email")
        age = st.number_input("Age", min_value=0, max_value=150, value=18)
        courses = st.text_input("Courses (comma-separated)")
        grades = st.text_input("Grades / notes")
        submitted = st.form_submit_button("Create Student")

    if submitted:
        if not name or not email or not courses:
            st.error("Please provide at least name, email and courses.")
        elif age < 8:
            st.error("Age must be 8 or above.")
        else:
            sid = generate_student_id()
            record = {
                "name": name.strip(),
                "email": email.strip(),
                "age": int(age),
                "studentid": sid,
                "courses": normalize_courses(courses),
                "grades": grades.strip(),
                "created_at": datetime.utcnow().isoformat(),
            }
            students.append(record)
            safe_write_data(students)
            st.success(f"Student created — ID: {sid}")
            st.rerun()

# ------------------------------
# Update / Delete UI
# ------------------------------
elif choice == "Update / Delete":
    st.title("Update or Delete Students")
    st.markdown("Select a student to update or delete.")

    ids = [s.get("studentid") for s in students]
    sel = st.selectbox("Choose Student ID", options=[""] + ids, index=0)
    if sel:
        student = find_student_by_id(students, sel)
        if student:
            with st.form("update_form"):
                name = st.text_input("Full name", value=student.get("name",""))
                email = st.text_input("Email", value=student.get("email",""))
                age = st.number_input("Age", min_value=0, max_value=150, value=int(student.get("age",0)))
                courses = st.text_input("Courses (comma-separated)", value=student.get("courses",""))
                grades = st.text_input("Grades / notes", value=student.get("grades",""))
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.form_submit_button("Update Student"):
                        if not name or not email:
                            st.error("Name and email required.")
                        else:
                            student["name"] = name.strip()
                            student["email"] = email.strip()
                            student["age"] = int(age)
                            student["courses"] = normalize_courses(courses)
                            student["grades"] = grades.strip()
                            student["updated_at"] = datetime.utcnow().isoformat()
                            safe_write_data(students)
                            st.success("Student updated.")
                            st.rerun()
                with col2:
                    if st.form_submit_button("Delete Student"):
                        if st.confirm("Are you sure you want to permanently delete this student?"):
                            students.remove(student)
                            safe_write_data(students)
                            st.success("Student deleted.")
                            st.rerun()
        else:
            st.warning("Student not found (maybe deleted).")

# ------------------------------
# Import / Export
# ------------------------------
elif choice == "Import / Export":
    st.title("Import / Export Students")
    st.markdown("Export the full dataset, or upload a JSON file to import (merges, no duplicates).")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download JSON (all students)"):
            buf = io.BytesIO()
            buf.write(json.dumps(students, indent=2, ensure_ascii=False).encode("utf-8"))
            buf.seek(0)
            st.download_button("Download JSON", data=buf, file_name="students.json", mime="application/json")
    with col2:
        uploaded = st.file_uploader("Upload students.json to merge", type=["json"])
        if uploaded:
            try:
                uploaded_data = json.loads(uploaded.getvalue().decode("utf-8"))
                if not isinstance(uploaded_data, list):
                    st.error("Uploaded file must be a JSON array of student objects.")
                else:
                    added = 0
                    existing_ids = {s.get("studentid") for s in students}
                    for s in uploaded_data:
                        if not s.get("studentid") or s.get("studentid") in existing_ids:
                            # skip duplicates or invalid
                            continue
                        students.append(s)
                        existing_ids.add(s.get("studentid"))
                        added += 1
                    safe_write_data(students)
                    st.success(f"Imported {added} new students.")
            except Exception as e:
                st.error(f"Could not parse uploaded JSON: {e}")

    st.markdown("---")
    st.write("Dataset preview (first 10 rows)")
    preview = students[:10]
    st.dataframe([{ "Name": s.get("name"), "Email": s.get("email"), "Age": s.get("age"), "ID": s.get("studentid")} for s in preview], use_container_width=True)

# ------------------------------
# End
# ------------------------------
