"""
LLM Chat Template Builder - Streamlit Web App
Interactive tool for building and visualizing chat prompts for various LLMs
"""

import streamlit as st
from components.state import init_session_state
from components.sidebar import render_sidebar
from components.main_area import render_main_area


def main():
    st.set_page_config(
        page_title="LLM Chat Template Builder",
        page_icon="P",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    render_sidebar()
    render_main_area()


if __name__ == "__main__":
    main()
