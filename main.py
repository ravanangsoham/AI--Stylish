import streamlit as st
import pandas as pd
import json
import os
import importlib

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & INTERFACE THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="Hyper-Personalized AI Fashion Stylist Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👗 Hyper-Personalized AI Stylist & Closet Engine")
st.write("Input your unique physical build, upload profile specs, and use Generative AI to discover tailored looks.")

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
# 4. SIDEBAR - PROFILE DATA & INVENTORY MANAGER
# -------------------------------------------------------------
with st.sidebar:
    st.header("👤 Your Physical Build Profile")
    st.write("Provide your dimensions so the AI can suggest cuts and fits that look best on you.")
    
    # User Measurements Panel
    col_h, col_w = st.columns(2)
    with col_h:
        height_cm = st.number_input("Height (cm)", min_value=100, max_value=250, value=175, step=1)
    with col_w:
        weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70, step=1)
        
    body_shape = st.selectbox(
        "Body Type / Silhouette",
        ["Rectangle / Athletic", "Inverted Triangle (Broad Shoulders)", "Oval / Round", "Triangle / Pear", "Hourglass"]
    )
    
    user_photo_url = st.text_input(
        "Style Reference Photo URL (Optional)", 
        placeholder="https://example.com/your-image.jpg"
    )
    if user_photo_url.strip():
        st.image(user_photo_url, caption="Your Reference Style / Profile", use_container_width=True)

    st.markdown("---")
    st.header("✨ Expand Digital Closet")
    
    with st.form("wardrobe_input_form", clear_on_submit=True):
        category = st.selectbox("Clothing Layer", ["Top", "Bottom", "Footwear", "Accessory"])
        name = st.text_input("Clothing Name", placeholder="e.g., Suede Bomber Jacket")
        color = st.text_input("Primary Color", placeholder="e.g., Olive Green")
        vibe = st.selectbox("Design Vibe/Style", ["Casual", "Formal", "Smart Casual", "Athletic", "Universal"])
        
        submitted = st.form_submit_button("➕ Register Item to Closet")
        
        if submitted and name.strip():
            new_clothing_item = {
                "Category": category,
                "Item": name,
                "Color": color if color else "Unspecified",
                "Vibe": vibe
            }
            st.session_state.closet = pd.concat([st.session_state.closet, pd.DataFrame([new_clothing_item])], ignore_index=True)
            st.toast(f"Saved: {name} added to your digital wardrobe!", icon="✨")

    st.markdown("---")
    st.metric("Total Digital Items Stored", len(st.session_state.closet))

# -------------------------------------------------------------
# 5. MAIN CONFIGURATION PANE
# -------------------------------------------------------------
col_control, col_output = st.columns([1, 1.2])

with col_control:
    st.header("🎯 Context & Environment Settings")
    
    occasion = st.selectbox(
        "What event are you dressing for?",
        ["Casual Weekend Hangout", "High-Stakes Job Interview", "Formal Dinner Date", "Corporate Business Meeting", "Summer Outdoor Brunch", "Late Night Club/Lounge Vibe"]
    )
    
    weather = st.selectbox(
        "What is the weather outside?",
        ["Bright, Sunny & Warm", "Freezing Cold & Rainy", "Chilly, Breezy & Windy", "High Humidity & Hot"]
    )
    
    custom_mood = st.text_input(
        "Specific aesthetic guidelines?",
        placeholder="e.g., 'Minimize torso look', 'Highlight shoulders', 'Earth tones only'"
    )
    
    st.markdown(" ")
    generate_outfit = st.button("🚀 Curate Custom Silhouette Outfit", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.subheader("📦 Your Current Active Wardrobe Database")
    st.dataframe(st.session_state.closet, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 6. ENHANCED RESPONSE GENERATION MATRIX
# -------------------------------------------------------------
with col_output:
    st.header("👔 Your Custom Tailored Look")
    
    if generate_outfit:
        if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
            st.error("Authentication Error: Valid API configuration required to run styling algorithm engines.")
        elif len(st.session_state.closet) < 3:
            st.warning("Your digital closet needs a larger selection. Please register items using the sidebar configuration panels.")
        else:
            with st.spinner("Calculating physical build matching indexes, layer weight, and proportions..."):
                closet_text_dump = st.session_state.closet.to_string(index=False)
                
                styling_prompt = f"""
                You are a world-class premier fashion stylist specializing in geometric body shape tailoring and proportion styling.
                Your task is to pick the ultimate outfit combination from the user's available wardrobe list based on their physical profile dimensions, weather conditions, and occasion.
                
                ### User Physical Silhouette Profile:
                - Height: {height_cm} cm
                - Weight: {weight_kg} kg
                - Stated Body Frame Silhouette Type: {body_shape}
                - Reference Portrait Media URL: {user_photo_url if user_photo_url else 'None provided'}
                
                ### Environmental Metrics:
                - Target Occasion: {occasion}
                - Weather Climate Factor: {weather}
                - Custom Tailoring Adjustments: {custom_mood}
                
                ### Available Wardrobe Dataset Pool:
                {closet_text_dump}
                
                ### Rules:
                1. Pick exactly one Top, one Bottom, and one Footwear choice from the list. Do not invent non-existent clothes.
                2. Explicitly explain how this clothing configuration flatters a person who is {height_cm}cm tall and weighs {weight_kg}kg with an {body_shape} build type.
                
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
                    # Run the dynamic call process block
                    raw_ai_text = call_gemini_api(API_KEY, styling_prompt)
                    parsed_style_map = json.loads(raw_ai_text)
                    
                    st.success("🎉 Look Tailored Successfully!")
                    
                    # Layout grid design framework cards
                    st.markdown("### 👔 Selected Ensemble Matrix")
                    
                    card_top, card_bottom, card_shoes = st.columns(3)
                    with card_top:
                        st.metric(label="👕 Top Choice", value=parsed_style_map.get("top_picked", "N/A"))
                    with card_bottom:
                        st.metric(label="👖 Bottom Choice", value=parsed_style_map.get("bottom_picked", "N/A"))
                    with card_shoes:
                        st.metric(label="👟 Footwear Choice", value=parsed_style_map.get("footwear_picked", "N/A"))
                    
                    # Display Accessories
                    selected_accs = parsed_style_map.get("accessories_list", [])
                    if selected_accs:
                        st.markdown("#### ✨ Accent Pieces & Accessories")
                        st.markdown(" ".join([f"`{item}`" for item in selected_accs]))
                    
                    # Display Pro Fit & Fit Customization Breakdown
                    st.markdown("---")
                    st.markdown("### 💡 Silhouette Proportional Analysis")
                    st.info(parsed_style_map.get("tailoring_fit_analysis", "No structural metrics returned by the generative engine."))
                    
                except Exception as error_exception:
                    st.error(f"Failed to generate outfit curation successfully. Error diagnostic log: {error_exception}")
    else:
        st.info("Tailor your dimension metrics on the left pane and press **Curate Custom Silhouette Outfit** to generate recommendations.")
