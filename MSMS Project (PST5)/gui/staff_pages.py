import streamlit as st

def show_staff_management_page(manager):
    
    """
    Displays the Staff Management page in the Streamlit GUI.

    Responsibilities:
    - Add new staff accounts
    - Edit existing staff credentials
    - Remove staff accounts
    - Restrict access to admin users only

    Args:
        manager (ScheduleManager): Backend controller for managing staff accounts.
    """
    
    st.header("Staff Management")

    with st.form("add_staff_form"):
        name = st.text_input("Staff Name")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Add Staff")
        if submitted and name and password:
            manager.add_staff(name, password)
            st.success(f"Staff {name} added!")

    st.subheader("All Staff")
    st.write(manager.list_staff())

    staff_ids = {s.name: s.id for s in manager.staff}
    if staff_ids:
        selected = st.selectbox("Select Staff", staff_ids.keys())
        new_name = st.text_input("New Name")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Update Staff"):
            manager.edit_staff(staff_ids[selected], new_name, new_pass)
            st.success("Staff updated!")
        if st.button("Remove Staff"):
            manager.remove_staff(staff_ids[selected])
            st.success("Staff removed!")
