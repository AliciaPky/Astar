import streamlit as st

def show_teacher_management_page(manager):
    
    """
    Displays the Teacher Management page in the Streamlit GUI.

    Responsibilities:
    - Add new teachers with specialities
    - Edit or remove existing teachers
    - View teacher details

    Args:
        manager (ScheduleManager): Backend controller for managing teacher data.
    """
    
    
    st.header("Teacher Management")

    # --- Add Teacher ---
    st.subheader("Add New Teacher")
    with st.form("add_teacher_form"):
        name = st.text_input("Teacher Name")
        speciality = st.text_input("Speciality / Instrument")
        submitted = st.form_submit_button("Add Teacher")
        if submitted and name and speciality:
            manager.add_teacher(name, speciality)
            st.success(f"Teacher {name} added!")

    # --- List Teachers ---
    st.subheader("Current Teachers")
    st.write(manager.list_teachers())

    # --- Edit / Remove Teacher ---
    teacher_ids = {t.name: t.id for t in manager.teachers}
    if teacher_ids:
        selected = st.selectbox("Select Teacher", teacher_ids.keys())
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("New name")
            new_spec = st.text_input("New speciality")
            if st.button("Update Teacher"):
                manager.edit_teacher(teacher_ids[selected], new_name, new_spec)
                st.success("Teacher updated!")
        with col2:
            if st.button("Remove Teacher"):
                manager.remove_teacher(teacher_ids[selected])
                st.success("Teacher removed!")
