import streamlit as st

st.set_page_config(page_title="Styling Log Archives", layout="wide")
st.title("📜 Lookbook Styling Generation Log History")
st.write("Review past curated styling entries generated during your active dashboard session usage cycles.")

if "history" not in st.session_state or len(st.session_state.history) == 0:
    st.info("No look generations logged yet. Go to the Style Engine page and create an outfit!")
else:
    if st.button("🗑️ Clear Archive Logs", type="secondary"):
        st.session_state.history = []
        st.rerun()

    for idx, entry in enumerate(st.session_state.history):
        with st.container():
            st.markdown(f"### 🗓️ Look Selection — Logged at {entry['timestamp']}")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.write(f"🎯 **Target:** {entry['occasion']}")
                st.write(f"🌤️ **Weather:** {entry['weather']}")
            with c2:
                st.markdown(f"👔 `👕 Top:` **{entry['top']}** | `👖 Bottom:` **{entry['bottom']}** | `👟 Shoes:` **{entry['footwear']}**")
            st.markdown("---")
