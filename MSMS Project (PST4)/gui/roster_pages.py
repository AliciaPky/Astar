import streamlit as st
import pandas as pd

def show_roster_page(manager):
    
    """
    Displays the Daily Roster page in the Streamlit GUI.

    Responsibilities:
    - Select a day and view the scheduled lessons
    - Display roster in a tabular format
    - Check-in students for lessons (attendance tracking)

    Args:
        manager (ScheduleManager): Backend controller for handling rosters and check-ins.
    """
    
    st.header("Daily Roster")

    day = st.selectbox("Select a day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    roster = manager.get_daily_roster(day)
    if roster:
        df = pd.DataFrame(roster)
        st.dataframe(df)
    else:
        st.info("No lessons scheduled for this day.")

    # --- Student Check-in ---
    st.subheader("Student Check-in")
    students = {s.name: s.id for s in manager.students}
    courses = {c.name: c.id for c in manager.courses}
    if students and courses:
        sname = st.selectbox("Select Student", students.keys())
        cname = st.selectbox("Select Course", courses.keys())
        if st.button("Check-in Student"):
            manager.check_in_student(students[sname], courses[cname])
            st.success(f"Checked in {sname} for {cname}")
