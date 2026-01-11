# SideMenus.py
import streamlit as st


class SideMenus:
    def render_api_client_menu(self):
        with st.sidebar:
            with st.expander("session_state", expanded=False):
                st.write(st.session_state)
