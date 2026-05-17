import streamlit as st
import pandas as pd
import json
import os
import importlib

# -------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# -------------------------------------------------------------
st.set_page_config(
    page_title="Pro AI Fashion Stylist & Wardrobe Manager", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("👗 Pro AI Fashion Stylist & Digital Closet")
st.write("An advanced engine to manage your inventory and generate intelligent, context-aware outfits.")

# Secure API Key Check
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.sidebar.warning("⚠️ API Key missing! Set GEMINI_API_KEY as an environment variable.")

# -------------------------------------------------------------
# 2. RUNTIME-AGNOSTIC AI ENGINE WRAPPER
# -------------------------------------------------------------
def call_gemini_api(api_key, prompt):
    """
    Safely executes the prompt across multiple SDK variations.
    Guarantees no deployment-shattering 'ImportError' or 'MarshallingError'.
    """
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
        os.environ["GEMINI_API_KEY"] = api_key

    # Attempt New google-genai SDK Strategy
    try:
        google_module = importlib.import_module('google')
        if hasattr(google_module, 'genai'):
            from google import genai
            local_client = genai.Client()
            
            # Route based on nested objects structure
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

    # Fallback to Legacy google-generativeai SDK Strategy
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
        raise ImportError("No compatible Google GenAI libraries found on server environment.")

# -------------------------------------------------------------
# 3. PERSISTENT CLOSET DATABASE INITIALIZATION
# -------------------------------------------------------------
if "closet" not in st.session_state:
    # Pre-populate with standard initial items
    st.session_state.closet = pd.DataFrame([
        {"Category": "Top", "Item": "White Button-down Shirt", "Color": "White", "Style": "Formal"},
        {"Category": "Top", "Item": "Black Graphic Tee", "Color": "Black", "Style": "Casual"},
        {"Category": "Top", "Item": "Navy Blue Cable Knit Sweater", "Color": "Navy", "Style": "Smart Casual"},
        {"Category": "Bottom", "Item": "Slim-fit Blue Jeans", "Color": "Blue Jeans", "Style": "Casual"},
        {"Category": "Bottom", "Item": "Tailored Black Slacks", "Color": "Black", "Style": "Formal"},
        {"Category": "Bottom", "Item": "Beige Chino Shorts", "Color": "Beige", "Style": "Casual"},
        {"Category": "Footwear", "Item": "Classic White Sneakers", "Color": "White", "Style": "Casual"},
        {"Category": "Footwear", "Item": "Brown Leather Loafers", "Color": "Brown", "Style": "Formal"},
        {"Category": "Accessory", "Item": "Black Leather Belt", "Color": "Black", "Style": "Universal"},
        {"Category": "Accessory", "Item": "Silver Minimalist Watch", "Color": "Silver", "Style": "Universal"}
    ])

# -------------------------------------------------------------
# 4. SIDEBAR - WARDROBE MANAGER (ADD ITEMS LIVE)
# -------------------------------------------------------------
with st.sidebar:
    st.header("➕ Expand Your Closet")
    with st.form("add_item_form", clear_on_submit=True):
        new_category = st.selectbox("Category", ["Top", "Bottom", "Footwear", "Accessory"])
        new_name = st.text_input("Item Name", placeholder="e.g., Charcoal Overcoat")
        new_color = st.text_input("Color", placeholder="e.g., Dark Grey")
        new_style = st.selectbox("Vibe/Style", ["Casual", "Formal", "Smart Casual", "Athletic", "Universal"])
        
        submit_item = st.form_submit_button("Save Item to Database")
        
        if submit_item and new_name:
            new_row = {
                "Category": new_category, 
                "Item": new_name, 
                "Color": new_color, 
                "Style": new_style
            }
            # Append new clothing item seamlessly to session memory
            st.session_state.closet = pd.concat([st.session_state.closet, pd.DataFrame([new_row])], ignore_index=True)
            st.toast(f" Added {new_name} successfully!", icon="✨")

    # Display Real-time Wardrobe Metrics
    st.markdown("---")
    st.header("📊 Inventory Analytics")
    st.metric("Total Items", len(st.session_state.closet))
    st.caption("Add items above to expand what your AI Stylist can pick from.")

# -------------------------------------------------------------
# 5. MAIN INTERFACE LAYOUT
# -------------------------------------------------------------
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("🛠️ Stylist Request Settings")
    
    occasion = st.selectbox(
        "What is the occasion?",
        ["Casual Hangout", "Job Interview", "Romantic Dinner Date", "Business Meeting", "Summer Brunch", "Night Out at a Club"]
    )
    
    weather = st.selectbox(
        "Current Environmental Weather?",
        ["Sunny & Warm", "Cold & Snowy", "Chilly & Windy", "Hot & Humid", "Heavy Monsoons"]
    )
    
    additional_notes = st.text_input(
        "Special instructions for the stylist?", 
        placeholder="e.g., 'Incorporate layers', 'Make it edgy', 'No jeans'"
    )
    
    generate_btn = st.button("🚀 Analyze & Generate Look", type="primary", use_container_width=True)

    st.markdown("---")
    st.subheader("📦 Live Wardrobe Stream")
    st.dataframe(st.session_state.closet, use_container_width=True, hide_index=True)

with col2:
    st.header("👔 Your Curated Custom Look")
    
    if generate_btn:
        if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
            st.error("Operation suspended. Please enter a valid Gemini API Key in your deployment environment.")
        else:
            with st.spinner("Running deep algorithmic fashion matching..."):
                # Format current session wardrobe state cleanly for the prompt context
                wardrobe_context = st.session_state.closet.to_string(index=False)
                
                prompt = f"""
                You are a premium, highly exclusive AI personal stylist. Your job is to select the ultimate outfit combination from the user's wardrobe list based on context.
                
                ### Critical Constraints:
                1. Only use explicitly stated pieces found inside the Wardrobe Dataset. Never invent items.
                2. Return exactly one Top, one Bottom, and one Footwear choice. You may recommend up to 3 Accessories.
                
                ### Context:
                - Occasion Target: {occasion}
                - Weather Pattern: {weather}
                - Special Constraints: {additional_notes}
                
                ### Wardrobe Dataset:
                {wardrobe_context}
                
                ### JSON Strict Output Architecture:
                Return your response as raw, valid JSON matching this exact map structure:
                {{
                  "top": "Name of chosen top",
                  "bottom": "Name of chosen bottom",
                  "footwear": "Name of chosen footwear",
                  "accessories": ["Accessory A", "Accessory B"],
                  "styling_tip": "An expert multi-sentence breakdown detailing why these selected colors and styles match the requested vibe and climate parameters."
                }}
                """
                
                try:
                    # Run the decoupled cross-version API connection
                    response_raw = call_gemini_api(API_KEY, prompt)
                    result = json.loads(response_raw)
                    
                    st.success("🎉 Your Personal Look Is Ready!")
                    
                    # Beautiful UI Components Display cards
                    st.markdown("### 📋 Chosen Ensemble Components")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.info(f"👕 **Top**\n\n{result.get('top', 'None Selected')}")
                    with c2:
                        st.info(f"👖 **Bottom**\n\n{result.get('bottom', 'None Selected')}")
                    with c3:
                        st.info(f"👟 **Footwear**\n\n{result.get('footwear', 'None Selected')}")
                    
                    # Accessories Section
                    acc_list = result.get('accessories', [])
                    if acc_list:
                        st.markdown("**✨ Accents & Accessories:**")
                        st.write(", ".join([f" `{a}`" for a in acc_list]))
                    
                    # Professional Style Insight Breakdown
                    st.markdown("### 💡 Professional Stylist Breakdown")
                    st.success(result.get('styling_tip', 'No style insight returned.'))
                    
                except Exception as e:
                    st.error(f"Failed to generate outfit composition. Error details: {e}")
    else:
        st.info("Tailor your configuration specs on the left pane and press **Analyze & Generate Look**.")
