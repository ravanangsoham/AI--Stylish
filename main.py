import streamlit as st
import pandas as pd
import json
import os
from google import genai

# -------------------------------------------------------------
# 1. INITIALIZATION & SETUP
# -------------------------------------------------------------
st.set_page_config(page_title="AI Personal Fashion Stylist", layout="wide")
st.title("👗 Personal AI Fashion Stylist")
st.write("Get personalized, context-aware outfit recommendations from your own wardrobe.")

# Configure your Gemini API Key
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    st.warning("Please configure your GEMINI_API_KEY to enable the AI recommendations.")

# Initialize the GenAI client safely
try:
    if API_KEY and API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        client = genai.Client(api_key=API_KEY)
    else:
        client = genai.Client()
except Exception:
    if API_KEY and API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        os.environ["GEMINI_API_KEY"] = API_KEY
    client = genai.Client()

# -------------------------------------------------------------
# 2. MOCK WARDROBE DATABASE
# -------------------------------------------------------------
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = pd.DataFrame([
        {"ID": 1, "Category": "Top", "Item": "White Button-down Shirt", "Color": "White", "Style": "Formal"},
        {"ID": 2, "Category": "Top", "Item": "Black Graphic Tee", "Color": "Black", "Style": "Casual"},
        {"ID": 3, "Category": "Top", "Item": "Navy Blue Cable Knit Sweater", "Color": "Navy", "Style": "Smart Casual"},
        {"ID": 4, "Category": "Bottom", "Item": "Slim-fit Blue Jeans", "Color": "Blue Jeans", "Style": "Casual"},
        {"ID": 5, "Category": "Bottom", "Item": "Tailored Black Slacks", "Color": "Black", "Style": "Formal"},
        {"ID": 6, "Category": "Bottom", "Item": "Beige Chino Shorts", "Color": "Beige", "Style": "Casual"},
        {"ID": 7, "Category": "Footwear", "Item": "Classic White Sneakers", "Color": "White", "Style": "Casual"},
        {"ID": 8, "Category": "Footwear", "Item": "Brown Leather Loafers", "Color": "Brown", "Style": "Formal"},
        {"ID": 9, "Category": "Accessory", "Item": "Black Leather Belt", "Color": "Black", "Style": "Universal"},
        {"ID": 10, "Category": "Accessory", "Item": "Silver Minimalist Watch", "Color": "Silver", "Style": "Universal"}
    ])

# -------------------------------------------------------------
# 3. USER INTERFACE (SIDEBAR & INPUTS)
# -------------------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🛠️ Context Settings")
    occasion = st.selectbox(
        "What is the occasion?",
        ["Casual Hangout", "Job Interview", "Romantic Dinner Date", "Business Meeting", "Summer Brunch"]
    )
    
    weather = st.selectbox(
        "What is the weather like?",
        ["Sunny & Warm", "Cold & Rainy", "Chilly & Windy", "Hot & Humid"]
    )
    
    additional_notes = st.text_input("Any specific preferences? (e.g., 'No shorts', 'Prefer dark colors')")
    
    generate_btn = st.button("✨ Generate Outfit Combo", type="primary")

    with st.expander("📦 View Your Wardrobe"):
        st.dataframe(st.session_state.wardrobe, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# 4. AI ENGINE & INFERENCE
# -------------------------------------------------------------
with col2:
    st.header("👔 Your Recommended Look")
    
    if generate_btn:
        if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
            st.error("Cannot proceed without a valid Gemini API Key configuration.")
        else:
            with st.spinner("Analyzing style combinations..."):
                wardrobe_context = st.session_state.wardrobe.to_string(index=False)
                
                # Construct the styling prompt
                prompt = f"""
                You are a highly fashionable AI Personal Stylist. Your task is to pick the best outfit combination from the user's available wardrobe based on the provided occasion and weather.
                
                ### Constraints:
                1. You MUST ONLY pick items that exist in the Wardrobe List provided below. Do not invent items.
                2. Select exactly one Top, one Bottom, one Footwear option, and optionally up to 2 Accessories if relevant.
                
                ### Context:
                - Occasion: {occasion}
                - Weather: {weather}
                - User Preferences: {additional_notes}
                
                ### Wardrobe List:
                {wardrobe_context}
                
                ### Expected Output Format:
                Return your response strictly in valid JSON format with the following keys:
                {{
                  "top": "Name of the chosen top",
                  "bottom": "Name of the chosen bottom",
                  "footwear": "Name of the chosen footwear",
                  "accessories": ["Accessory 1", "Accessory 2"],
                  "styling_tip": "A 2-sentence explanation of why this look fits the occasion and weather beautifully."
                }}
                """
                
                try:
                    # Use the correct parameter name: generation_config
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type='application/json'
                        )
                    )
                    response_text = response.text
                    
                    # Parse the JSON outcome
                    result = json.loads(response_text)
                    
                    # Display recommendations cleanly
                    st.success("Stylist Recommendation Ready!")
                    
                    st.subheader("📋 Outfit Components")
                    st.markdown(f"👕 **Top:** {result.get('top', 'N/A')}")
                    st.markdown(f"👖 **Bottom:** {result.get('bottom', 'N/A')}")
                    st.markdown(f"👟 **Footwear:** {result.get('footwear', 'N/A')}")
                    
                    accs = ", ".join(result.get('accessories', []))
                    st.markdown(f"⌚ **Accessories:** {accs if accs else 'None suggested'}")
                    
                    st.subheader("💡 Stylist Note")
                    st.info(result.get('styling_tip', 'No style notes provided.'))
                    
                except Exception as e:
                    st.error(f"An error occurred during generation: {e}")
    else:
        st.info("Adjust the settings on the left and click **Generate Outfit Combo** to run the AI engine.")
