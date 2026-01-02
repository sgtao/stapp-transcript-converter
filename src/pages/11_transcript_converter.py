# 11_transcript_converter.py
# app.py
import streamlit as st

from logic.add_subsections_to_transcript import add_subsections_to_transcript

APP_TITLE = "Transcript Subsection Converter"


def initialize_session_state():
    if "original_text" not in st.session_state:
        st.session_state.original_text = ""
    if "converted_text" not in st.session_state:
        st.session_state.converted_text = ""


def main():
    st.set_page_config(
        page_title="Transcript Subsection Converter", layout="wide"
    )

    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.title(f"🎬 {APP_TITLE}")
    st.subheader("YouTube文字起こし サブセクション変換")

    original_text = st.text_area(
        label="Original Transcript:",
        # type="default",
        placeholder="YouTubeの文字起こし文を貼り付けてください",
        value=st.session_state.original_text,
    )

    if st.button("変換する"):
        if not original_text.strip():
            st.warning("文字起こし文を入力してください")
        else:
            st.session_state.original_text = original_text
            converted_text = add_subsections_to_transcript(original_text)
            st.session_state.converted_text = converted_text

    with st.expander(label="変換結果", expanded=False):
        # st.text_area(
        #     label="Converted Transcript",
        #     value=converted,
        #     height=400,
        # )
        st.code(
            # label="Converted Transcript",
            # body=converted,
            body=st.session_state.converted_text,
            language=None,
            height=400,
        )


if __name__ == "__main__":
    initialize_session_state()
    main()
