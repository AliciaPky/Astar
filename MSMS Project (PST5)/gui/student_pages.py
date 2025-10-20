#gui\student_pages.py

import streamlit as st

def show_student_management_page(manager):
    
    """
    Displays the Student Management page in the Streamlit GUI.

    Responsibilities:
    - Register new students with name and instrument
    - Edit or remove existing student records
    - Print student cards
    - Enrol students into courses

    Args:
        manager (ScheduleManager): Backend controller for managing student data.
    """
    
    st.header("Student Management")

    # --- Search Students ---
    st.subheader("Find a Student")
    search_name = st.text_input("Enter student name")
    if st.button("Search"):
        results = [s.display_info() for s in manager.students if search_name.lower() in s.name.lower()]
        if results:
            st.write(results)
        else:
            st.warning("No student found.")

    # --- Register New Student ---
    st.subheader("Register New Student")
    with st.form("registration_form"):
        reg_name = st.text_input("Student Name")
        submitted = st.form_submit_button("Add Student")
        if submitted and reg_name:
            new_student = manager.add_student(reg_name)
            st.success(f"Added {reg_name}!")

    # --- Edit / Remove Student ---
    st.subheader("Edit or Remove Student")
    student_ids = {s.name: s.id for s in manager.students}
    if student_ids:
        selected = st.selectbox("Select student", student_ids.keys())
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("New name")
            if st.button("Update Name"):
                manager.edit_student(student_ids[selected], new_name)
                st.success("Student updated!")
        with col2:
            if st.button("Remove Student"):
                manager.remove_student(student_ids[selected])
                st.success("Student removed!")
