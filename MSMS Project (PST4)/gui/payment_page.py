# gui/payments_page.py
import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def show_payments_page():
    
    """
    Displays the Payments (Stub) page in the Streamlit GUI.

    Responsibilities:
    - Provide a placeholder for future payment system (PST5)
    - Show a preview image and message
    - Encourage user support

    Args:
        None (does not require manager as no data operations are performed yet).
    """
    
    """Displays the Payments page with an image."""
    st.header("Payments")

    st.subheader("The true feature will be implemented in PST5. For now, enjoy this preview image! Remember to support me if you like my work!!! 🥳")

    # Show image (replace with your actual path)
    st.image("Photo\Maybank QR.jpeg", caption="Payments System Preview")
