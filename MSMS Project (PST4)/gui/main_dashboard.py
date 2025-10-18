# gui/main_dashboard.py
import streamlit as st
import warnings
from app.schedule import ScheduleManager

# Import page modules
from gui.student_pages import show_student_management_page
from gui.teacher_pages import show_teacher_management_page
from gui.course_pages import show_course_management_page
from gui.instrument_pages import show_instrument_management_page
from gui.roster_pages import show_roster_page
from gui.admin_pages import show_admin_management_page
from gui.staff_pages import show_staff_management_page
from gui.payment_page import show_payments_page

#Remove future update warnings
warnings.filterwarnings("ignore", category=FutureWarning)


def login_screen(manager: ScheduleManager):
    """Login screen for staff/admin authentication."""
    st.title("🎼 Music School Management System (MSMS) - Login")

    #Using form so that we can login in with enter key
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

    if login_btn:
        # Try staff login
        if manager.sign_in_staff(username, password):
            st.session_state.is_authenticated = True
            st.session_state.role = "staff"
            st.session_state.username = username
            st.success(f"✅ Logged in as Staff: {username}")
            st.rerun()
            

        # Try admin login
        elif manager.sign_in_admin(username, password):
            st.session_state.is_authenticated = True
            st.session_state.role = "admin"
            st.session_state.username = username
            st.success(f"✅ Logged in as Admin: {username}")
            st.rerun()

        else:
            st.error("❌ Invalid username or password")


def launch():
    """Sets up the main Streamlit application window and navigation."""
    st.set_page_config(
        layout="wide",
        page_title="Music School Management System",
        page_icon="🎵"
    )

    if "manager" not in st.session_state:
        st.session_state.manager = ScheduleManager()
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
        st.session_state.role = None
        st.session_state.username = None

    manager = st.session_state.manager

    # If not logged in then only show login page only
    if not st.session_state.is_authenticated:
        login_screen(manager)
        return

    # If logged in then show sidebar and pages
    st.sidebar.title(f"📌 Navigation ({st.session_state.role.upper()})")
    st.sidebar.write(f"👤 {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.is_authenticated = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()

    # Sidebar menu
    page = st.sidebar.radio(
        "Go to",
        [
            "Student Management",
            "Teacher Management",
            "Course Management",
            "Instrument Management",
            "Daily Roster",
            "Admin Management",
            "Staff Management",
            "Payments"
        ],
    )

    # Route to correct page
    if page == "Student Management":
        show_student_management_page(manager)

    elif page == "Teacher Management":
        show_teacher_management_page(manager)

    elif page == "Course Management":
        show_course_management_page(manager)

    elif page == "Instrument Management":
        show_instrument_management_page(manager)

    elif page == "Daily Roster":
        show_roster_page(manager)

    elif page == "Admin Management":
        if st.session_state.role == "admin":
            show_admin_management_page(manager)
        else:
            st.error("❌ Access denied. Admins only.")

    elif page == "Staff Management":
        if st.session_state.role == "admin":
            show_staff_management_page(manager)
        else:
            st.error("❌ Access denied. Admins only.")

    elif page == "Payments":
        st.header("💳 Payments")
        show_payments_page()