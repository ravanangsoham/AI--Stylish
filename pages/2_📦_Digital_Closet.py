import streamlit as st
import pandas as pd

st.set_page_config(page_title="Digital Closet Ledger", layout="wide")
st.title("📦 Digital Wardrobe Inventory Management")

if "closet" not in st.session_state:
    st.write("Initializing closet system matrix...")
    st.experimental_rerun()

# EXPAND INVENTORY SUBMISSION FORM
with st.expander("➕ Register a New Clothing Item Block", expanded=False):
    with st.form("add_item_form", clear_on_submit=True):
        category = st.selectbox("Layer Category", ["Top", "Bottom", "Footwear", "Accessory"])
        name = st.text_input("Item Specification Name", placeholder="e.g., Suede Field Jacket")
        color = st.text_input("Primary Color Hue", placeholder="e.g., Earth Olive")
        vibe = st.selectbox("Aesthetic Style Vibe", ["Casual", "Formal", "Smart Casual", "Athletic", "Universal"])
        
        submit_item = st.form_submit_button("Save Item Asset to Closet", use_container_width=True)
        
        if submit_item and name.strip():
            new_row = {"Category": category, "Item": name, "Color": color if color else "Unspecified", "Vibe": vibe}
            st.session_state.closet = pd.concat([st.session_state.closet, pd.DataFrame([new_row])], ignore_index=True)
            st.toast(f"Saved: Added {name} successfully!", icon="✅")

st.markdown(" ")
st.subheader("📊 Complete Active Closet Database")
st.dataframe(st.session_state.closet, use_container_width=True, hide_index=True)

st.metric("Total Items Registered In Closet", len(st.session_state.closet))
