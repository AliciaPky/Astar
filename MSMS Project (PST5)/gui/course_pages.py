import streamlit as st

def show_course_management_page(manager):
    
    """
    Displays the Course Management page in the Streamlit GUI.

    Responsibilities:
    - Add new courses linked to teachers and instruments
    - Add or remove lessons within a course
    - Enrol students into courses
    - Switch students between courses
    - Remove courses

    Args:
        manager (ScheduleManager): Backend controller for managing course and lesson data.
    """
    
    st.header("Course Management")

    # --- Add Course ---
    st.subheader("Create New Course")
    with st.form("add_course_form"):
        name = st.text_input("Course Name")
        instrument = st.text_input("Instrument")
        teacher_ids = {t.name: t.id for t in manager.teachers}
        teacher_name = st.selectbox("Assign Teacher", teacher_ids.keys()) if teacher_ids else None
        submitted = st.form_submit_button("Add Course")
        if submitted and teacher_name:
            manager.add_course(name, instrument, teacher_ids[teacher_name])
            st.success(f"Course {name} added!")

    # --- Add Lesson to Course ---
    st.subheader("Add Lesson to Course")
    course_ids = {c.name: c.id for c in manager.courses}
    if course_ids:
        selected_course = st.selectbox(
            "Select Course", course_ids.keys(), key="lesson_course_select"
        )
        title = st.text_input("Lesson Title")
        day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="lesson_day_select")
        time = st.text_input("Start Time (e.g. 15:00)")
        duration = st.number_input("Duration (minutes)", min_value=15, step=15, key="lesson_duration")
        if st.button("Add Lesson"):
            manager.add_lesson_to_course(course_ids[selected_course], title, day, time, duration)
            st.success(f"Lesson '{title}' added!")

    # --- Enroll Student ---
    st.subheader("Enroll Student in Course")
    students = {s.name: s.id for s in manager.students}
    courses = {c.name: c.id for c in manager.courses}
    if students and courses:
        sname = st.selectbox("Select Student", students.keys(), key="enroll_student_select")
        cname = st.selectbox("Select Course", courses.keys(), key="enroll_course_select")
        if st.button("Enroll"):
            manager.enroll_student_in_course(students[sname], courses[cname])
            st.success(f"{sname} enrolled in {cname}")

