"""
Prompt generation and tokenization
"""

import copy
import streamlit as st
from components.template_renderer import render_template, count_tokens as _count_tokens


def generate_prompt() -> str:
    """Generate the prompt from current messages and config"""
    # Deep copy messages to avoid modifying session state
    messages = copy.deepcopy(st.session_state.messages)

    # Get tools if enabled
    tools = None
    if st.session_state.include_tools and st.session_state.tools:
        tools = st.session_state.tools

    # Get selected model
    model_key = st.session_state.selected_model

    # Build template variables based on model
    template_vars = {
        "thinking": st.session_state.enable_thinking,
        "enable_thinking": st.session_state.enable_thinking,
    }

    try:
        return render_template(
            model_key=model_key,
            messages=messages,
            tools=tools,
            add_generation_prompt=st.session_state.add_generation_prompt,
            **template_vars,
        )
    except Exception as e:
        return f"Error generating prompt: {str(e)}"


def count_tokens(text: str) -> int:
    """Count tokens in the text using the selected model's tokenizer"""
    model_key = st.session_state.selected_model
    return _count_tokens(text, model_key)
