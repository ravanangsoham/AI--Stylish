import streamlit as st
import pandas as pd
import json
import os
import importlib
from PIL import Image

# -------------------------------------------------------------
# 1. PAGE SETUP & MOBILE-RESPONSIVE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="Hyper-Personalized AI Fashion Stylist Pro", 
    layout="wide", # Allows flexible expanding on tablets/desktops
    initial_sidebar_state="collapsed" # Better default initial view for mobile screens
)

# Custom CSS injected to optimize spacing, form elements, and card padding on mobile viewports
st.markdown("""
    <style>
    /* Make metrics text scale down cleanly on small smartphone screens */
    [data-testid="stMetricValue"] {
        font-size: calc(1.5rem + 1vw) !important;
    }
    /* Ensure user uploaded profile images don't overflow layout limits */
    .stImage > img {
        max-width: 100%;
        border-radius: 12px;
        height: auto;
    }
    /* Add subtle container padding adjustment for touch device optimizations */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛍️ AI Smart Closet & Personal Stylist")
st.write("Upload your photo, set your body dimensions, and let generative AI design perfectly proportioned outfits.")

# Secure System API Key Verification
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.sidebar.warning("⚠️ Setup Required: Please set your GEMINI_API_KEY environment variable.")

# -------------------------------------------------------------
# 2. RUNTIME-ISOLATED ENVIRONMENT SAFE CALL ENGINE
# -------------------------------------------------------------
def call_gemini_api(api_key, prompt):
    """
    Dynamically maps execution across new 'google-genai' and legacy
    'google-generativeai' libraries. Ensures zero boot-import crashes.
    """
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
        os.environ["GEMINI_API_KEY"] = api_key

    # Strategy A: New google-genai library matching
    try:
        google_module = importlib.import_module('google')
        if hasattr(google_module, 'genai'):
            from google import genai
            local_client = genai.Client()
            
            if hasattr(local_client, 'models'):
                response = local_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
            else:
                response = local_client.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
            return response.text
    except (ImportError, AttributeError):
        pass

    # Strategy B: Legacy fallback routing
    try:
        import google.generativeai as legacy_genai
        if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
            legacy_genai.configure(api_key=api_key)
        else:
            legacy_genai.configure()
            
        model = legacy_genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        return response.text
    except ImportError:
        raise ImportError("No compatible AI Engine drivers available on the host machine environment.")

# -------------------------------------------------------------
# 3. CLOSET MEMORY INITIALIZATION
# -------------------------------------------------------------
if "closet" not in st.session_state:
    st.session_state.closet = pd.DataFrame([
        {"Category": "Top", "Item": "White Oxford Button-Down", "Color": "White", "Vibe": "Formal"},
        {"Category": "Top", "Item": "Oversized Charcoal Hooded Sweatshirt", "Color": "Charcoal Grey", "Vibe": "Casual"},
        {"Category": "Top", "Item": "Navy Blue Cable Knit Sweater", "Color": "Navy", "Vibe": "Smart Casual"},
        {"Category": "Bottom", "Item": "Slim-fit Blue Jeans", "Color": "Blue Jeans", "Vibe": "Casual"},
        {"Category": "Bottom", "Item": "Tailored Black Slacks", "Color": "Black", "Vibe": "Formal"},
        {"Category": "Bottom", "Item": "Beige Cotton Chino Shorts", "Color": "Beige", "Vibe": "Casual"},
        {"Category": "Footwear", "Item": "Minimalist White Sneakers", "Color": "White", "Vibe": "Casual"},
        {"Category": "Footwear", "Item": "Italian Brown Leather Loafers", "Color": "Brown", "Vibe": "Formal"},
        {"Category": "Accessory", "Item": "Classic Black Leather Belt", "Color": "Black", "Vibe": "Universal"},
        {"Category": "Accessory", "Item": "Silver Chronograph Watch", "Color": "Silver", "Vibe": "Universal"}
    ])

# -------------------------------------------------------------
# 4. PHONE/TABLET MULTI-COLUMN DESIGN LAYOUT
# -------------------------------------------------------------
# Using tabs for clear smartphone-level segment separation instead of wide crowded screens
tab_stylist, tab_closet, tab_profile = st.tabs(["✨ Style Engine", "📦 My Wardrobe", "👤 Body Profile"])

# --- TAB 1: STYLE ENGINE & GENERATION ---
with tab_stylist:
    col_control, col_output = st.columns([1, 1.2])

    with col_control:
        st.subheader("🎯 Styling Criteria")
        
        occasion = st.selectbox(
            "What event are you dressing for?",
            ["Casual Weekend Hangout", "High-Stakes Job Interview", "Formal Dinner Date", "Corporate Business Meeting", "Summer Outdoor Brunch", "Late Night Club/Lounge Vibe"]
        )
        
        weather = st.selectbox(
            "What is the weather outside?",
            ["Bright, Sunny & Warm", "Freezing Cold & Rainy", "Chilly, Breezy & Windy", "High Humidity & Hot"]
        )
        
        custom_mood = st.text_input(
            "Specific style choices or adjustments?",
            placeholder="e.g., 'Incorporate layers', 'All black look', 'No shorts'"
        )
        
        st.markdown(" ")
        generate_outfit = st.button("🚀 Curate Custom Silhouette Outfit", type="primary", use_container_width=True)

    with col_output:
        st.subheader("👔 Your Curated Look")
        
        if generate_outfit:
            if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
                st.error("Authentication Error: Valid API configuration required to run styling algorithm engines.")
            elif len(st.session_state.closet) < 3:
                st.warning("Your digital closet needs a larger selection. Please add items in the Wardrobe tab.")
            else:
                with st.spinner("Calculating physical build matching indexes, layer weight, and proportions..."):
                    closet_text_dump = st.session_state.closet.to_string(index=False)
                    
                    # Safely pass profile properties from session storage defaults
                    h_cm = st.session_state.get('p_height', 175)
                    w_kg = st.session_state.get('p_weight', 70)
                    b_sh = st.session_state.get('p_shape', 'Rectangle / Athletic')
                    has_img = "Yes (User uploaded reference avatar)" if st.session_state.get('p_img_uploaded', False) else "None provided"
                    
                    styling_prompt = f"""
                    You are a world-class premier fashion stylist specializing in geometric body shape tailoring and proportion styling.
                    Your task is to pick the ultimate outfit combination from the user's available wardrobe list based on their physical profile dimensions, weather conditions, and occasion.
                    
                    ### User Physical Silhouette Profile:
                    - Height: {h_cm} cm
                    - Weight: {w_kg} kg
                    - Stated Body Frame Silhouette Type: {b_sh}
                    - Reference Photo State: {has_img}
                    
                    ### Environmental Metrics:
                    - Target Occasion: {occasion}
                    - Weather Climate Factor: {weather}
                    - Custom Tailoring Adjustments: {custom_mood}
                    
                    ### Available Wardrobe Dataset Pool:
                    {closet_text_dump}
                    
                    ### Rules:
                    1. Pick exactly one Top, one Bottom, and one Footwear choice from the list. Do not invent non-existent clothes.
                    2. Explicitly explain how this clothing configuration flatters a person who is {h_cm}cm tall and weighs {w_kg}kg with an {b_sh} build type.
                    
                    ### Enforced JSON Output Structural Design Map:
                    Return your response strictly as valid, raw JSON matching this map format structure:
                    {{
                      "top_picked": "Name of the chosen item categorized as Top",
                      "bottom_picked": "Name of the chosen item categorized as Bottom",
                      "footwear_picked": "Name of the chosen item categorized as Footwear",
                      "accessories_list": ["Accessory Choice A", "Accessory Choice B"],
                      "tailoring_fit_analysis": "An expert analysis explaining how these selected cuts, structures, and item fits specifically optimize, flatter, and balance their physical proportions based on their height, weight, and body frame type."
                    }}
                    """
                    
                    try:
                        raw_ai_text = call_gemini_api(API_KEY, styling_prompt)
                        parsed_style_map = json.loads(raw_ai_text)
                        
                        st.success("🎉 Look Tailored Successfully!")
                        
                        # Layout grid architecture scales safely across small and big panels
                        st.markdown("#### 📋 Selected Ensemble Matrix")
                        
                        card_top, card_bottom, card_shoes = st.columns(3)
                        with card_top:
                            st.metric(label="👕 Top Choice", value=parsed_style_map.get("top_picked", "N/A"))
                        with card_bottom:
                            st.metric(label="👖 Bottom Choice", value=parsed_style_map.get("bottom_picked", "N/A"))
                        with card_shoes:
                            st.metric(label="👟 Footwear Choice", value=parsed_style_map.get("footwear_picked", "N/A"))
                        
                        selected_accs = parsed_style_map.get("accessories_list", [])
                        if selected_accs:
                            st.markdown("**✨ Accent Pieces & Accessories:**")
                            st.markdown(" ".join([f"`{item}`" for item in selected_accs]))
                        
                        st.markdown("---")
                        st.markdown("#### 💡 Silhouette Proportional Analysis")
                        st.info(parsed_style_map.get("tailoring_fit_analysis", "No metrics returned."))
                        
                    except Exception as error_exception:
                        st.error(f"Failed to generate outfit curation safely. Diagnostic log: {error_exception}")
        else:
            st.info("Tailor your criteria on the left and click **Curate Custom Silhouette Outfit**.")

# --- TAB 2: INVENTORY & EXPANSION CLOSER ---
with tab_closet:
    st.subheader("📦 Closet Database Ledger")
    
    with st.expander("➕ Register a New Clothing Piece", expanded=False):
        with st.form("wardrobe_input_form", clear_on_submit=True):
            category = st.selectbox("Clothing Layer", ["Top", "Bottom", "Footwear", "Accessory"])
            name = st.text_input("Clothing Name", placeholder="e.g., Brushed Twill Overshirt")
            color = st.text_input("Primary Color", placeholder="e.g., Muted Sage")
            vibe = st.selectbox("Design Vibe/Style", ["Casual", "Formal", "Smart Casual", "Athletic", "Universal"])
            
            submitted = st.form_submit_button("➕ Register Item to Closet", use_container_width=True)
            
            if submitted and name.strip():
                new_clothing_item = {
                    "Category": category,
                    "Item": name,
                    "Color": color if color else "Unspecified",
                    "Vibe": vibe
                }
                st.session_state.closet = pd.concat([st.session_state.closet, pd.DataFrame([new_clothing_item])], ignore_index=True)
                st.toast(f"Saved: {name} registered!", icon="✨")

    st.markdown(" ")
    st.dataframe(st.session_state.closet, use_container_width=True, hide_index=True)
    st.metric("Total Active Inventory Items", len(st.session_state.closet))

# --- TAB 3: PERSONAL PHYSICAL PROFILE MANAGEMENT ---
with tab_profile:
    st.subheader("👤 Tailoring Metrics & Identity Specs")
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        # Dynamic inputs save instantly to memory via keys
        st.number_input("Height (cm)", min_value=100, max_value=250, value=175, step=1, key="p_height")
        st.number_input("Weight (kg)", min_value=30, max_value=200, value=70, step=1, key="p_weight")
        st.selectbox(
            "Body Frame Configuration",
            ["Rectangle / Athletic", "Inverted Triangle (Broad Shoulders)", "Oval / Round", "Triangle / Pear", "Hourglass"],
            key="p_shape"
        )
        
    with col_p2:
        st.markdown("**📸 Device Camera / Gallery Image Upload**")
        # FIXED: Added file_uploader to allow native device photo access on phones & tablets
        uploaded_file = st.file_uploader(
            "Choose a full-body portrait photo...", 
            type=["jpg", "jpeg", "png"],
            help="Upload an image from your device gallery or take a picture directly using your phone's camera."
        )
        
        if uploaded_file is not None:
            st.session_state['p_img_uploaded'] = True
            image = Image.open(uploaded_file)
            st.image(image, caption="Profile Avatar Reference Active", use_container_width=True)
        else:
            st.session_state['p_img_uploaded'] = False
            st.caption("No custom image asset active. Using standard silhouette matrix defaults.")
