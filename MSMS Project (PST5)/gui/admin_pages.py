import streamlit as st

def show_admin_management_page(manager):
    
    """
    Displays the Admin Management page in the Streamlit GUI.

    Responsibilities:
    - Add new admin accounts
    - Edit existing admin credentials
    - Remove admin accounts
    - Restrict access to admin users only

    Args:
        manager (ScheduleManager): Backend controller for managing admin accounts.
    """
    
    st.header("Admin Tools & Management")

    with st.form("add_admin_form"):
        name = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Add Admin")
        if submitted and name and password:
            manager.add_admin(name, password)
            st.success(f"Admin {name} added!")

    st.subheader("All Admins")
    st.write(manager.list_admins())

    admin_ids = {a.username: a.id for a in manager.admin}
    if admin_ids:
        selected = st.selectbox("Select Admin", admin_ids.keys())
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Update Admin"):
            manager.edit_admin(admin_ids[selected], new_user, new_pass)
            st.success("Admin updated!")
        if st.button("Remove Admin"):
            manager.remove_admin(admin_ids[selected])
            st.success("Admin removed!")
            
    st.subheader("Data Backup")
    st.write("You can manually back up all system data at any time.")

    if st.button("💾 Save Backup Now"):
        msg = manager.backup_data()
        if "successfully" in msg:
            st.success(msg)
        else:
            st.error(msg)

    st.info("We recommend you to backup your data before you shutdown the program.")
