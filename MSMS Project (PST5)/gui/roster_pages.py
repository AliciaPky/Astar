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
    # Step 1: Select Student
    student_options = {s.name: s.id for s in manager.students}
    student_name = st.selectbox("Select Student", list(student_options.keys()))
    selected_student_id = student_options[student_name]

    # Step 2: Get only the enrolled courses for this student
    enrolled_courses = manager.get_enrolled_courses_for_student(selected_student_id)

    if not enrolled_courses:
        st.info("This student is not enrolled in any course.")
        return

    # Step 3: Show available courses
    course_options = {f"{c.name} ({c.instrument})": c.id for c in enrolled_courses}
    selected_course = st.selectbox("Select Course", list(course_options.keys()))

    # Step 4: Check-in button
    if st.button("Check In"):
        course_id = course_options[selected_course]
        success = manager.check_in_student(selected_student_id, course_id)
        if success:
            st.success("Check-in successful!")
        else:
            st.error("Check-in failed.")
