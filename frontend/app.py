import streamlit as st
import requests
import pandas as pd

API = "http://localhost:5000"

st.set_page_config(page_title="Student Report Card", page_icon="🎓", layout="wide")
st.title("🎓 Student Report Card System")

menu = st.sidebar.radio("📌 Navigation", ["➕ Add Student", "📝 Add Marks", "📊 View Report", "👥 All Students"])

# ── ADD STUDENT ──────────────────────────────────────────────────────────────
if menu == "➕ Add Student":
    st.header("Add New Student")

    col1, col2 = st.columns(2)
    with col1:
        name    = st.text_input("Full Name")
        roll_no = st.text_input("Roll Number")
    with col2:
        cls     = st.selectbox("Class", [str(i) for i in range(1, 13)])
        section = st.selectbox("Section", ["A", "B", "C", "D"])

    if st.button("✅ Add Student", use_container_width=True):
        if name and roll_no:
            res = requests.post(f"{API}/students", json={
                "name": name, "roll_no": roll_no,
                "class": cls, "section": section
            })
            data = res.json()
            if data["success"]:
                st.success(f"Student added! Student ID = **{data['id']}** (save this to add marks)")
            else:
                st.error(f"Error: {data['error']}")
        else:
            st.warning("Please fill in all fields.")

# ── ADD MARKS ────────────────────────────────────────────────────────────────
elif menu == "📝 Add Marks":
    st.header("Add Marks for a Student")

    student_id = st.number_input("Student ID", min_value=1, step=1)
    subjects   = ["Mathematics", "Science", "English", "Tamil", "Social Science"]

    st.subheader("Enter Marks")
    marks_data = []
    for subj in subjects:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.write(subj)
        with col2:
            scored = st.number_input("Marks Scored", 0, 100, key=f"{subj}_scored")
        with col3:
            total  = st.number_input("Max Marks",    0, 100, value=100, key=f"{subj}_max")
        marks_data.append({"subject": subj, "marks": scored, "max_marks": total})

    if st.button("💾 Save Marks", use_container_width=True):
        res  = requests.post(f"{API}/marks", json={
            "student_id": int(student_id),
            "subjects"  : marks_data
        })
        data = res.json()
        if data["success"]:
            st.success("Marks saved successfully!")
        else:
            st.error(f"Error: {data['error']}")

# ── VIEW REPORT ──────────────────────────────────────────────────────────────
elif menu == "📊 View Report":
    st.header("View Student Report Card")

    student_id = st.number_input("Enter Student ID", min_value=1, step=1)

    if st.button("🔍 Get Report", use_container_width=True):
        res  = requests.get(f"{API}/report/{int(student_id)}")
        data = res.json()

        if data["success"]:
            s = data["student"]
            st.subheader(f"📋 Report Card — {s['name']}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Roll No",  s["roll_no"])
            col2.metric("Class",    s["class"])
            col3.metric("Section",  s["section"])

            st.divider()

            # Build marks table with grade
            rows = []
            total_scored, total_max = 0, 0
            for m in data["marks"]:
                pct   = round((m["marks"] / m["max_marks"]) * 100, 1) if m["max_marks"] else 0
                grade = (
                    "A+" if pct >= 90 else
                    "A"  if pct >= 80 else
                    "B"  if pct >= 70 else
                    "C"  if pct >= 60 else
                    "D"  if pct >= 50 else "F"
                )
                rows.append({
                    "Subject"   : m["subject"],
                    "Marks"     : int(m["marks"]),
                    "Max Marks" : int(m["max_marks"]),
                    "Percentage": f"{pct}%",
                    "Grade"     : grade
                })
                total_scored += m["marks"]
                total_max    += m["max_marks"]

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Summary
            st.divider()
            overall = round((total_scored / total_max) * 100, 1) if total_max else 0
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Marks",    f"{int(total_scored)} / {int(total_max)}")
            c2.metric("Overall %",      f"{overall}%")
            c3.metric("Final Grade",    "A+" if overall>=90 else "A" if overall>=80 else "B" if overall>=70 else "C" if overall>=60 else "D" if overall>=50 else "F")

            # Bar chart
            st.subheader("📈 Marks Chart")
            chart_data = pd.DataFrame({
                "Subject": [r["Subject"]  for r in rows],
                "Marks"  : [r["Marks"]    for r in rows]
            }).set_index("Subject")
            st.bar_chart(chart_data)

        else:
            st.error(f"Error: {data['error']}")

# ── ALL STUDENTS ─────────────────────────────────────────────────────────────
elif menu == "👥 All Students":
    st.header("All Registered Students")

    res  = requests.get(f"{API}/students")
    data = res.json()

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.info(f"Total Students: {len(data)}")
    else:
        st.warning("No students found.")