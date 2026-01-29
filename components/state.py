"""
Session state management for Prompt Builder
"""

import json
import copy
import streamlit as st
from components.config import DEFAULT_MESSAGES, DEFAULT_TOOLS, DEFAULT_MODEL


def deep_copy_list(items):
    """Deep copy a list of dicts"""
    return [copy.deepcopy(item) for item in items]


def init_session_state():
    """Initialize session state variables"""
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = DEFAULT_MODEL

    if "messages" not in st.session_state:
        st.session_state.messages = deep_copy_list(DEFAULT_MESSAGES)

    if "tools" not in st.session_state:
        st.session_state.tools = deep_copy_list(DEFAULT_TOOLS)

    if "tools_json" not in st.session_state:
        st.session_state.tools_json = json.dumps(DEFAULT_TOOLS, indent=2)

    if "include_tools" not in st.session_state:
        st.session_state.include_tools = False

    if "enable_thinking" not in st.session_state:
        st.session_state.enable_thinking = True

    if "add_generation_prompt" not in st.session_state:
        st.session_state.add_generation_prompt = True

    if "edited_prompt" not in st.session_state:
        st.session_state.edited_prompt = None

    if "use_edited_prompt" not in st.session_state:
        st.session_state.use_edited_prompt = False


def add_message():
    """Add a new message to the list"""
    st.session_state.messages.append({"role": "user", "content": ""})
    st.session_state.use_edited_prompt = False


def delete_message(index: int):
    """Delete a message at the given index"""
    if len(st.session_state.messages) > 1:
        st.session_state.messages.pop(index)
        st.session_state.use_edited_prompt = False


def move_message(index: int, direction: int):
    """Move a message up or down"""
    new_index = index + direction
    if 0 <= new_index < len(st.session_state.messages):
        messages = st.session_state.messages
        messages[index], messages[new_index] = messages[new_index], messages[index]
        st.session_state.use_edited_prompt = False
