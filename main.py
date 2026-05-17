import streamlit as st
import pandas as pd
import json
import os
import importlib

# -------------------------------------------------------------
# 1. PAGE SETUP & USER-FRIENDLY STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="AI Smart Wardrobe & Digital Closet Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛍️ Advanced AI Smart Wardrobe & Personal Stylist")
st.write("Manage your digital clothing inventory and use Generative AI to curate context-aware, highly personalized outfits.")

# Fetch system environment key safely
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.sidebar.warning("⚠️ Setup Required: Please set your GEMINI_API_KEY environment variable.")

# -------------------------------------------------------------
# 2. RUNTIME-ISOLATED ENVIRONMENT SAFE CALL ENGINE
# -------------------------------------------------------------
def call_gemini_api(api_key, prompt):
    """
    Dynamically maps execution across new 'google-genai' and legacy
    'google-generativeai' libraries. Guarantees 0% boot-import crashes.
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
        raise ImportError("No compatible AI Engine drivers available on host machine environment.")

# -------------------------------------------------------------
# 3. GLOBAL STATE CLOSET DATABASE INITIALIZATION
# -------------------------------------------------------------
if "closet" not in st.session_state:
    st.session_state.closet = pd.DataFrame([
        {"Category": "Top", "Item": "White Oxford Button-Down", "Color": "White", "Vibe": "Formal"},
        {"Category": "Top", "Item": "Vintage Black Graphic Tee", "Color": "Black", "Vibe": "Casual"},
        {"Category": "Top", "Item": "Navy Blue Cable Knit Sweater", "Color": "Navy", "Vibe": "Smart Casual"},
        {"Category": "Bottom", "Item": "Slim-fit Distressed Blue Jeans", "Color": "Blue", "Vibe": "Casual"},
        {"Category": "Bottom", "Item": "Tailored Charcoal Slacks", "Color": "Charcoal Grey", "Vibe": "Formal"},
        {"Category": "Bottom", "Item": "Beige Cotton Chino Shorts", "Color": "Beige", "Vibe": "Casual"},
        {"Category": "Footwear", "Item": "Minimalist White Sneakers", "Color": "White", "Vibe": "Casual"},
        {"Category": "Footwear", "Item": "Italian Brown Leather Loafers", "Color": "Brown", "Vibe": "Formal"},
        {"Category": "Accessory", "Item": "Classic Black Leather Belt", "Color": "Black", "Vibe": "Universal"},
        {"Category": "Accessory", "Item": "Silver Chronograph Watch", "Color": "Silver", "Vibe": "Universal"}
    ])

# -------------------------------------------------------------
# 4. SIDEBAR - LIVE DIGITAL CLOSET INPUT MANAGER
# -------------------------------------------------------------
with st.sidebar:
    st.header("✨ Expand Digital Closet")
    st.write("Add clothes you own to your virtual wardrobe pool below.")
    
    with st.form("wardrobe_input_form", clear_on_submit=True):
        category = st.selectbox("Clothing Layer/Category", ["Top", "Bottom", "Footwear", "Accessory"])
        name = st.text_input("Clothing Name", placeholder="e.g., Suede Bomber Jacket")
        color = st.text_input("Primary Color", placeholder="e.g., Olive Green")
        vibe = st.selectbox("Design Vibe/Style", ["Casual", "Formal", "Smart Casual", "Athletic", "Universal"])
        
        submitted = st.form_submit_button("➕ Register Item to Closet")
        
        if submitted:
            if name.strip() == "":
                st.error("Item name cannot be left empty.")
            else:
                new_clothing_item = {
                    "Category": category,
                    "Item": name,
                    "Color": color if color else "Unspecified",
                    "Vibe": vibe
                }
                # Seamless data concat appending onto active state memory
                st.session_state.closet = pd.concat([st.session_state.closet, pd.DataFrame([new_clothing_item])], ignore_index=True)
                st.toast(f"Saved: {name} added to your digital wardrobe!", icon="added")

    st.markdown("---")
    st.header("📊 Inventory Breakdown")
    st.metric("Total Digital Items Stored", len(st.session_state.closet))

# -------------------------------------------------------------
# 5. USER DISPLAY & INTERACTIVE CONFIGURATION PANELS
# -------------------------------------------------------------
col_control, col_output = st.columns([1, 1.3])

with col_control:
    st.header("🎯 Style Configuration")
    st.write("Tell the AI what your day looks like so it can curate your style.")
    
    occasion = st.selectbox(
        "What event are you dressing for?",
        ["Casual Weekend Hangout", "High-Stakes Job Interview", "Formal Dinner Date", "Corporate Business Meeting", "Summer Outdoor Brunch", "Late Night Club/Lounge Vibe"]
    )
    
    weather = st.selectbox(
        "What is the weather outside?",
        ["Bright, Sunny & Warm", "Freezing Cold & Rainy", "Chilly, Breezy & Windy", "High Humidity & Hot"]
    )
    
    custom_mood = st.text_input(
        "Any custom design constraints/preferences?",
        placeholder="e.g., 'Incorporate layers', 'All black look', 'Comfy footwear only'"
    )
    
    st.markdown(" ")
    generate_outfit = st.button("🚀 Analyze Wardrobe & Curate Outfit", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.subheader("📦 Your Current Active Wardrobe Database")
    st.dataframe(st.session_state.closet, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 6. ENHANCED USER-FRIENDLY RESPONSE ENGINE
# -------------------------------------------------------------
with col_output:
    st.header("👔 Your Curated Styling Recommendation")
    
    if generate_outfit:
        if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
            st.error("Authentication Error: Valid API configuration required to run styling algorithm engines.")
        elif len(st.session_state.closet) < 3:
            st.warning("Your digital closet needs a larger selection. Please add at least one Top, Bottom, and Footwear option in the sidebar.")
        else:
            with st.spinner("Analyzing outfit color matrices, aesthetic harmonies, and weather parameters..."):
                # Convert session DataFrame contents clean format text string block
                closet_text_dump = st.session_state.closet.to_string(index=False)
                
                styling_prompt = f"""
                You are an award-winning elite personal fashion stylist. Your goal is to review the user's available inventory clothes items and pick the absolute best combination match matching the environmental metrics.
                
                ### Critical Rules:
                1. You must ONLY select items that exist inside the Wardrobe Dataset below. Never invent pieces.
                2. Pick exactly one 'Top', one 'Bottom', and one 'Footwear' option. You can list up to 3 'Accessory' items.
                
                ### User Environmental Context Parameters:
                - Occasion Vibe Target: {occasion}
                - Weather Climate Factor: {weather}
                - User Custom Rules: {custom_mood}
                
                ### Available Wardrobe Dataset Pool:
                {closet_text_dump}
                
                ### Enforced JSON Output Structural Design Map:
                Return your response strictly as valid, raw JSON matching this map format structure:
                {{
                  "top_picked": "Name of the chosen item categorized as Top",
                  "bottom_picked": "Name of the chosen item categorized as Bottom",
                  "footwear_picked": "Name of the chosen item categorized as Footwear",
                  "accessories_list": ["Accessory Choice A", "Accessory Choice B"],
                  "professional_reasoning": "A highly detailed, sophisticated fashion analysis explaining why these colors, layers, and styles harmonize together to match the occasion and handle the weather."
                }}
                """
                
                try:
                    # Run the dynamic call process block
                    raw_ai_text = call_gemini_api(API_KEY, styling_prompt)
                    parsed_style_map = json.loads(raw_ai_text)
                    
                    st.success("🎉 Look Curated Successfully!")
                    
                    # Layout grid design framework cards
                    st.markdown("### 👔 Selected Ensemble Matrix")
                    
                    card_top, card_bottom, card_shoes = st.columns(3)
                    with card_top:
                        st.metric(label="👕 Top Selection", value=parsed_style_map.get("top_picked", "N/A"))
                    with card_bottom:
                        st.metric(label="👖 Bottom Selection", value=parsed_style_map.get("bottom_picked", "N/A"))
                    with card_shoes:
                        st.metric(label="👟 Footwear Selection", value=parsed_style_map.get("footwear_picked", "N/A"))
                    
                    # Display Accessories
                    selected_accs = parsed_style_map.get("accessories_list", [])
                    if selected_accs:
                        st.markdown("#### ✨ Accent Pieces & Accessories")
                        st.markdown(" ".join([f"`{item}`" for item in selected_accs]))
                    
                    # Display Professional Expert Stylist Reasoning Insights
                    st.markdown("---")
                    st.markdown("### 💡 Professional Stylist Analysis")
                    st.info(parsed_style_map.get("professional_reasoning", "No detailed design documentation attached by engine."))
                    
                except Exception as error_exception:
                    st.error(f"Failed to generate outfit curation successfully. Error diagnostic log: {error_exception}")
    else:
        st.info("Configure your layout specifications on the left panel grid and trigger **Analyze Wardrobe & Curate Outfit** to run the design models.")
