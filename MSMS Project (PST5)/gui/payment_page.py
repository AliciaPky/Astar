# gui/finance_pages.py
import streamlit as st
from datetime import datetime

def show_finance_page(manager):
    """Display the Finance Page for recording and viewing payments."""
    st.title("Finance & Payments")

    tabs = st.tabs(["Record Payment", "View Payment History"])

    # ----------------------------------------------------------------
    # TAB 1 – Record a New Payment
    # ----------------------------------------------------------------
    with tabs[0]:
        st.subheader("Record a New Payment")

        # Student selection
        student_options = {s.name: s.id for s in manager.students}
        if not student_options:
            st.warning("No students found. Please register students first.")
            return

        selected_name = st.selectbox("Select Student", list(student_options.keys()))
        student_id = student_options[selected_name]

        # Payment form
        with st.form("payment_form"):
            amount = st.number_input("Amount (RM)", min_value=0.0, format="%.2f")
            method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Online Transfer"])
            submit = st.form_submit_button("Record Payment")

            if submit:
                success = manager.record_payment(student_id, amount, method)
                if success:
                    st.success(f"Payment recorded successfully for {selected_name}.")
                else:
                    st.error("Failed to record payment. Please check inputs.")

    # ----------------------------------------------------------------
    # TAB 2 – View Payment History
    # ----------------------------------------------------------------
    with tabs[1]:
        st.subheader("Payment History")

        student_options = {s.name: s.id for s in manager.students}
        if not student_options:
            st.warning("No students available.")
            return

        selected_name = st.selectbox("Select Student to View History", list(student_options.keys()), key="history")
        student_id = student_options[selected_name]

        history = manager.get_payment_history(student_id)

        if not history:
            st.info(f"No payment history found for {selected_name}.")
        else:
            st.dataframe(history, use_container_width=True)

            # Export options
            export_type = st.radio("Export Report As", ["JSON", "CSV"], horizontal=True)
            export_btn = st.button("Export Report")

            if export_btn:
                filename = f"{selected_name.replace(' ', '_')}_payments.{export_type.lower()}"
                manager.export_report("payments", filename)
                st.success(f"Report exported as {filename}")
