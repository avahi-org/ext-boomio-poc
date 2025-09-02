import streamlit as st

st.set_page_config(
    page_title="Boomio game assets generator",
    page_icon="🎨",
    layout="wide"
)

spc_1, spc_2, spc_3 = st.columns([2, 2, 2]) # Adjust ratios for desired spacing
with spc_2:
    st.image("src/boomio_logo.svg", width=800)
st.title("🎨 Boomio game assets generator")
st.sidebar.success("Select image generation mode")

st.markdown("##### This platform allows you to: \n" \
"- Generate individual game assets (characters, obstacles, backgrounds) based on prompts and pre-processing. \n" \
"- Generate individual game assets (characters, obstacles, backgrounds) based on upload brandbook information and pre-processing.")

