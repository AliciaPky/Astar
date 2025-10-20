import streamlit as st

def show_instrument_management_page(manager):
    
    """
    Displays the Instrument Management page in the Streamlit GUI.

    Responsibilities:
    - Add new instruments
    - Rename existing instruments
    - Remove instruments

    Args:
        manager (ScheduleManager): Backend controller for managing instrument data.
    """
    
    st.header("Instrument Management")

    # --- Add Instrument ---
    with st.form("add_instrument_form"):
        new_instrument = st.text_input("New Instrument Name")
        submitted = st.form_submit_button("Add Instrument")
        if submitted and new_instrument:
            manager.add_instrument(new_instrument)
            st.success(f"Instrument {new_instrument} added!")

    # --- List Instruments ---
    st.subheader("Current Instruments")
    st.write(manager.list_instruments())

    # --- Rename / Remove Instrument ---
    if manager.instruments:
        selected = st.selectbox("Select Instrument", manager.instruments)
        new_name = st.text_input("Rename Instrument")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Rename"):
                manager.edit_instrument(selected, new_name)
                st.success(f"Renamed {selected} to {new_name}")
        with col2:
            if st.button("Remove"):
                manager.remove_instrument(selected)
                st.success(f"Instrument {selected} removed")
