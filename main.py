import streamlit as st
import pandas as pd
from PIL import Image

# 1. PAGE SETUP & MOBILE-RESPONSIVE VIEW
st.set_page_config(
    page_title="Pro AI Stylist Hub", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS for Multi-Device Scaling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: calc(1.3rem + 1vw) !important; }
    .stImage > img { border-radius: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .block-container { padding-top: 1.5rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Welcome to Your AI Smart Wardrobe Hub")
st.write("Navigate using the sidebar menu to add clothes, generate outfits, or view your history.")

# 2. INVENTORY & SESSION GLOBAL MEMORY SETUP
if "closet" not in st.session_state:
    st.session_state.closet = pd.DataFrame([
        {"Category": "Top", "Item": "White Oxford Button-Down", "Color": "White", "Vibe": "Formal"},
        {"Category": "Top", "Item": "Oversized Charcoal Hoodie", "Color": "Charcoal Grey", "Vibe": "Casual"},
        {"Category": "Bottom", "Item": "Slim-fit Blue Jeans", "Color": "Blue Jeans", "Vibe": "Casual"},
        {"Category": "Bottom", "Item": "Tailored Black Slacks", "Color": "Black", "Vibe": "Formal"},
        {"Category": "Footwear", "Item": "Minimalist White Sneakers", "Color": "White", "Vibe": "Casual"},
        {"Category": "Footwear", "Item": "Italian Brown Loafers", "Color": "Brown", "Vibe": "Formal"}
    ])

if "history" not in st.session_state:
    st.session_state.history = []

# 3. GLOBAL PROFILE SETUP (COMPATIBLE WITH TOUCH PHONES/TABLETS)
st.header("👤 Your Core Physical Profile")
col1, col2 = st.columns([1, 1])

with col1:
    st.number_input("Height (cm)", min_value=100, max_value=250, value=175, key="p_height")
    st.number_input("Weight (kg)", min_value=30, max_value=200, value=70, key="p_weight")
    st.selectbox(
        "Body Frame Configuration",
        ["Rectangle / Athletic", "Inverted Triangle (Broad Shoulders)", "Oval / Round", "Triangle / Pear", "Hourglass"],
        key="p_shape"
    )

with col2:
    st.markdown("**📸 Device Camera / Gallery Image Upload**")
    uploaded_file = st.file_uploader(
        "Upload a snapshot profile photo...", 
        type=["jpg", "jpeg", "png"],
        help="Access your smartphone camera or select an image asset directly from your library."
    )
    
    if uploaded_file is not None:
        st.session_state['p_img_uploaded'] = True
        image = Image.open(uploaded_file)
        st.image(image, caption="Profile Active Blueprint", use_container_width=True)
    else:
        st.session_state['p_img_uploaded'] = False
        st.info("No photo attached yet. Using generic silhouette mapping metrics.")
