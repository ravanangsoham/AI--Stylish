import streamlit as st
import pandas as pd
import json
import os
import importlib
from PIL import Image
from datetime import datetime

# -------------------------------------------------------------
# 1. PAGE SETUP & MOBILE RESPONSIVE UI TWEAKS
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Smart Wardrobe & Stylist Pro", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injected CSS to optimize touch interfaces and responsive scaling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: calc(1.2rem + 0.8vw) !important; }
    .stImage > img { border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
    div[data-testid="stExpander"] { border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# Secure API Key Check
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# -------------------------------------------------------------
# 2. BULLETPROOF DYNAMIC API CALL WRAPPER
# -------------------------------------------------------------
def call_gemini_api(api_key, prompt):
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
        os.environ["GEMINI_API_KEY"] = api_key
    try:
        google_module = importlib.import_module('google')
        if hasattr(google_module, 'genai'):
            from google import genai
            local_client = genai.Client()
            target = local_client.models if hasattr(local_client, 'models') else local_client
            response = target.generate_content(
                model='gemini-2.5-flash', contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return response.text
    except Exception:
        pass

    import google.generativeai as legacy_genai
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE": 
        legacy_genai.configure(api_key=api_key)
    model = legacy_genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    return model.generate_content(prompt).text

# -------------------------------------------------------------
# 3. GLOBAL STATE STATE INITIALIZATION (PERSISTENT MEMORY)
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# 4. APP LAYOUT & CENTRAL NAVIGATION TABS
# -------------------------------------------------------------
st.title("🛍️ AI Smart Wardrobe Hub")
st.write("Manage your closet inventory, set physical builds, and generate context-tailored styles.")

tab_engine, tab_closet, tab_profile, tab_history = st.tabs([
    "✨ Style Engine", 
    "📦 Digital Closet", 
    "👤 Body Profile", 
    "📜 Lookbook History"
])

# --- TAB 1: STYLE ENGINE & GENERATOR ---
with tab_engine:
    if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
        st.warning("⚠️ API Key Missing: Please configure your GEMINI_API_KEY to clear the restriction.")
        
    col_ctrl, col_out = st.columns([1, 1.2])
    
    with col_ctrl:
        st.subheader("🎯 Context Settings")
        occasion = st.selectbox("What event are you dressing for?", ["Casual Weekend Hangout", "High-Stakes Job Interview", "Formal Dinner Date", "Corporate Business Meeting", "Late Night Club Vibe"])
        weather = st.selectbox("What is the climate like?", ["Bright, Sunny & Warm", "Freezing Cold & Rainy", "Chilly, Breezy & Windy", "High Humidity & Hot"])
        custom_mood = st.text_input("Special tailoring requests?", placeholder="e.g., 'Incorporate layers', 'Highlight broad shoulders'")
        
        generate_btn = st.button("🚀 Analyze & Curate Outfit", type="primary", use_container_width=True)
        
    with col_out:
        st.subheader("👔 Your Curated Look")
        
        if generate_btn:
            if len(st.session_state.closet) < 3:
                st.warning("Your digital closet database needs a larger selection. Please add elements inside the Digital Closet tab.")
            else:
                with st.spinner("Running styling metrics and build ratios..."):
                    closet_dump = st.session_state.closet.to_string(index=False)
                    h_cm = st.session_state.get('p_height', 175)
                    w_kg = st.session_state.get('p_weight', 70)
                    b_sh = st.session_state.get('p_shape', 'Rectangle / Athletic')
                    has_photo = "Yes (User uploaded custom portrait blueprint)" if st.session_state.get('p_img_uploaded', False) else "None provided"
                    
                    prompt = f"""
                    You are an award-winning personal master stylist specializing in height balancing and proportion framing.
                    Select the ultimate combination match from the user's wardrobe list parameter arrays.
                    
                    ### User Dimensions:
                    - Height: {h_cm} cm | Weight: {w_kg} kg | Frame Type: {b_sh}
                    - Photo Blueprint Provided: {has_photo}
                    
                    ### Context Metrics:
                    - Target Occasion: {occasion} | Weather: {weather} | Rules: {custom_mood}
                    
                    ### Available Wardrobe List Pool:
                    {closet_dump}
                    
                    Return your response strictly as valid raw JSON matching this map architecture:
                    {{
                      "top_picked": "Name of chosen Top item",
                      "bottom_picked": "Name of chosen Bottom item",
                      "footwear_picked": "Name of chosen Footwear item",
                      "tailoring_fit_analysis": "A sophisticated breakdown explaining why these items optimize visual appeal based on their height, weight, and frame configuration."
                    }}
                    """
                    try:
                        raw_text = call_gemini_api(API_KEY, prompt)
                        result = json.loads(raw_text)
                        
                        st.success("🎉 Look Curated Successfully!")
                        
                        # High-visibility response metrics cards
                        c1, c2, c3 = st.columns(3)
                        with c1: st.metric("👕 Top Chosen", result.get('top_picked', 'N/A'))
                        with c2: st.metric("👖 Bottom Chosen", result.get('bottom_picked', 'N/A'))
                        with c3: st.metric("👟 Footwear Chosen", result.get('footwear_picked', 'N/A'))
                        
                        st.markdown("#### 💡 Structural Analysis")
                        st.info(result.get('tailoring_fit_analysis', 'No design records provided.'))
                        
                        # Add tracking entry to lookbook history log
                        log_entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "occasion": occasion,
                            "weather": weather,
                            "top": result.get('top_picked'),
                            "bottom": result.get('bottom_picked'),
                            "footwear": result.get('footwear_picked')
                        }
                        st.session_state.history.insert(0, log_entry)
                        
                    except Exception as e:
                        st.error(f"Failed to generate outfit composition: {e}")
        else:
            st.info("Adjust the criteria panels and click **Analyze & Curate Outfit** to run your design layout models.")

# --- TAB 2: DIGITAL WARDROBE MANAGEMENT ---
with tab_closet:
    st.subheader("📦 Closet Database Ledger")
    
    with st.expander("➕ Register a New Clothing Piece", expanded=False):
        with st.form("inventory_input_form", clear_on_submit=True):
            category = st.selectbox("Clothing Layer", ["Top", "Bottom", "Footwear", "Accessory"])
            name = st.text_input("Clothing Item Name", placeholder="e.g., Suede Bomber Jacket")
            color = st.text_input("Primary Color", placeholder="e.g., Midnight Black")
            vibe = st.selectbox("Design Vibe Style", ["Casual", "Formal", "Smart Casual", "Athletic", "Universal"])
            
            submit_item = st.form_submit_button("➕ Save Item to Closet Database", use_container_width=True)
            if submit_item and name.strip():
                new_clothing_item = {"Category": category, "Item": name, "Color": color if color else "Unspecified", "Vibe": vibe}
                st.session_state.closet = pd.concat([st.session_state.closet, pd.DataFrame([new_clothing_item])], ignore_index=True)
                st.toast(f"Saved: {name} uploaded!", icon="✨")

    st.markdown(" ")
    st.dataframe(st.session_state.closet, use_container_width=True, hide_index=True)
    st.metric("Total Items Stored In Closet Pool", len(st.session_state.closet))

# --- TAB 3: USER BODY PROFILE ---
with tab_profile:
    st.subheader("👤 Personal Proportional Profiles")
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        st.number_input("Height (cm)", min_value=100, max_value=250, value=175, step=1, key="p_height")
        st.number_input("Weight (kg)", min_value=30, max_value=200, value=70, step=1, key="p_weight")
        st.selectbox(
            "Body Shape / Silhouette Type",
            ["Rectangle / Athletic", "Inverted Triangle (Broad Shoulders)", "Oval / Round", "Triangle / Pear", "Hourglass"],
            key="p_shape"
        )
        
    with col_p2:
        st.markdown("**📸 Device Camera / Gallery Image Upload**")
        uploaded_file = st.file_uploader(
            "Upload a custom full-body portrait profile shot...", 
            type=["jpg", "jpeg", "png"],
            help="Access your native mobile camera or select an image directly from your device gallery."
        )
        if uploaded_file is not None:
            st.session_state['p_img_uploaded'] = True
            image = Image.open(uploaded_file)
            st.image(image, caption="Profile Reference Asset Sync Active", use_container_width=True)
        else:
            st.session_state['p_img_uploaded'] = False
            st.caption("No custom photo attached. Using fallback configuration mapping models.")

# --- TAB 4: ACTIVE LOOKBOOK HISTORY ---
with tab_history:
    st.subheader("📜 Lookbook Styling Generation Log History")
    
    if not st.session_state.history:
        st.info("No curated style generations logged yet during this session.")
    else:
        if st.button("🗑️ Clear Archive Logs", type="secondary"):
            st.session_state.history = []
            st.rerun()
            
        for entry in st.session_state.history:
            with st.container():
                st.markdown(f"##### 🗓️ Look Curated — Logged at {entry['timestamp']}")
                h_c1, h_c2 = st.columns([1, 2])
                with h_c1:
                    st.write(f"🎯 **Target:** {entry['occasion']}")
                    st.write(f"🌤️ **Weather:** {entry['weather']}")
                with h_c2:
                    st.markdown(f"👔 `👕 Top:` **{entry['top']}** | `👖 Bottom:` **{entry['bottom']}** | `👟 Shoes:` **{entry['footwear']}**")
                st.markdown("---")
