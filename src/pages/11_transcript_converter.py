# 11_transcript_converter.py
import streamlit as st
from typing import List

from logic.add_subsections_to_transcript import add_subsections_to_transcript

APP_TITLE = "Transcript Subsection Converter"


def initialize_session_state() -> None:
    if "original_text" not in st.session_state:
        st.session_state.original_text = ""
    if "converted_text" not in st.session_state:
        st.session_state.converted_text = ""
    if "subsections" not in st.session_state:
        st.session_state.subsections = []


def extract_subsections(converted_text: str) -> List[str]:
    """
    変換後トランスクリプトからサブセクション見出しを抽出する。
    """
    return [
        line.replace("### ", "", 1)
        for line in converted_text.splitlines()
        if line.startswith("### ")
    ]


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.title(f"🎬 {APP_TITLE}")
    st.subheader("YouTube文字起こし サブセクション変換")

    original_text = st.text_area(
        label="Original Transcript:",
        placeholder="YouTubeの文字起こし文を貼り付けてください",
        value=st.session_state.original_text,
        height=300,
    )

    if st.button("変換する"):
        if not original_text.strip():
            st.warning("文字起こし文を入力してください")
        else:
            st.session_state.original_text = original_text
            converted_text = add_subsections_to_transcript(original_text)
            st.session_state.converted_text = converted_text
            st.session_state.subsections = extract_subsections(converted_text)

    with st.expander(label="変換結果", expanded=False):
        st.markdown("#### トランスクリプト（変換後）")
        st.code(
            body=st.session_state.converted_text,
            language=None,
            height=400,
        )

        if st.session_state.subsections:
            subsection_text = ""
            for subsection in st.session_state.subsections:
                subsection_text += f"- {subsection}\n"
            st.markdown("#### サブセクション一覧")
            st.code(
                body=subsection_text,
                language=None,
                height=200,
            )


if __name__ == "__main__":
    initialize_session_state()
    main()
