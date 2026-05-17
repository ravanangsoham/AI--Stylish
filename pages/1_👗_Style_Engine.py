import streamlit as st
import json
import os
import importlib
from datetime import datetime

st.set_page_config(page_title="AI Style Engine", layout="wide")
st.title("👗 AI Fashion Styling Engine")

API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

def call_gemini_api(api_key, prompt):
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
        os.environ["GEMINI_API_KEY"] = api_key
        
    # STRATEGY A: Clean dynamic loading of the new google-genai library
    try:
        google_module = importlib.import_module('google')
        if hasattr(google_module, 'genai'):
            from google import genai
            local_client = genai.Client()
            target = local_client.models if hasattr(local_client, 'models') else local_client
            response = target.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return response.text
    except Exception:
        pass

    # STRATEGY B: Fallback directly to legacy google-generativeai core
    import google.generativeai as legacy_genai
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE": 
        legacy_genai.configure(api_key=api_key)
    model = legacy_genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    return model.generate_content(prompt).text

# -------------------------------------------------------------
# CONTROL PANEL & FORM FIELDS
# -------------------------------------------------------------
col_ctrl, col_out = st.columns([1, 1.2])

with col_ctrl:
    st.subheader("🎯 Context Settings")
    occasion = st.selectbox("Occasion Target", ["Casual Hangout", "Job Interview", "Dinner Date", "Business Meeting", "Club/Night Out"])
    weather = st.selectbox("Current Climate Conditions", ["Sunny & Warm", "Cold & Rainy", "Chilly & Windy", "Hot & Humid"])
    custom_mood = st.text_input("Special requests?", placeholder="e.g., 'Layered look', 'Comfy items only'")
    
    generate_btn = st.button("🚀 Curate Custom Look", type="primary", use_container_width=True)

with col_out:
    st.subheader("👔 Curated Output Result")
    
    if generate_btn:
        if API_KEY == "YOUR_GEMINI_API_KEY_HERE" and not os.getenv("GEMINI_API_KEY"):
            st.error("Please configure your GEMINI_API_KEY environment variable.")
        elif "closet" not in st.session_state or len(st.session_state.closet) < 3:
            st.warning("Your digital closet database needs more items to compute selections.")
        else:
            with st.spinner("Analyzing style metrics..."):
                closet_text = st.session_state.closet.to_string(index=False)
                h_cm = st.session_state.get('p_height', 175)
                w_kg = st.session_state.get('p_weight', 70)
                b_sh = st.session_state.get('p_shape', 'Rectangle / Athletic')
                
                prompt = f"""
                You are a world-class premier personal stylist. Pick the best outfit combo from the user's closet matrix based on their dimensions, weather, and occasion.
                User Physical Profile: Height {h_cm}cm, Weight {w_kg}kg, Build Type '{b_sh}'.
                Context: Event '{occasion}', Weather '{weather}', Rules '{custom_mood}'.
                Closet Dataset Pool:
                {closet_text}
                
                Return response strictly as a raw JSON map matching this schema structure:
                {{
                  "top_picked": "Name of chosen Top item",
                  "bottom_picked": "Name of chosen Bottom item",
                  "footwear_picked": "Name of chosen Footwear item",
                  "tailoring_fit_analysis": "A brief analysis explaining why this look balances their physical build profile and targets the environmental criteria perfectly."
                }}
                """
                try:
                    raw_text = call_gemini_api(API_KEY, prompt)
                    result = json.loads(raw_text)
                    
                    st.success("🎉 Look Tailored Successfully!")
                    st.markdown(f"👕 **Top Layer:** {result.get('top_picked')}")
                    st.markdown(f"👖 **Bottom Layer:** {result.get('bottom_picked')}")
                    st.markdown(f"👟 **Footwear Selection:** {result.get('footwear_picked')}")
                    st.info(result.get('tailoring_fit_analysis'))
                    
                    # LOG GENERATION EVENT INTO SESSIONS HISTORY
                    history_entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "occasion": occasion,
                        "weather": weather,
                        "top": result.get('top_picked'),
                        "bottom": result.get('bottom_picked'),
                        "footwear": result.get('footwear_picked')
                    }
                    st.session_state.history.insert(0, history_entry)
                    
                except Exception as e:
                    st.error(f"Failed to generate outfit curation safely: {e}")
