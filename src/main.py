import streamlit as st

"""
# Welcome to [Streamlit](https://streamlit.io/)!

Edit `/src` and `/tests` to customize this app to your heart's desire :heart:.
"""

# サイドバーのページに移動
st.divider()
# st.page_link("pages/example_app.py", label="Go to Example App")
st.page_link(
    "pages/11_transcript_converter.py",
    label="Go to Transcript Converter",
    icon="🎬",
)
st.page_link(
    "pages/12_yt_frame_capture.py",
    label="Go to YouTube Frame Capture",
    icon="📸",
)

st.divider()
