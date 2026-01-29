"""
Syntax highlighting for prompt output
"""

import re
from typing import List, Tuple
import streamlit as st
from components.config import MODELS


# CSS class mapping for color keys
COLOR_CLASS_MAP = {
    "bos_eos": "token-bos",
    "role": "token-role",
    "think": "token-think",
    "dsml": "token-dsml",
    "func": "token-func",
}


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_token_patterns() -> List[Tuple[str, str]]:
    """Get token patterns for the currently selected model"""
    model_key = st.session_state.get("selected_model", "deepseek-v3.1")
    if model_key in MODELS:
        return MODELS[model_key].token_patterns
    return []


def highlight_prompt(text: str) -> str:
    """Apply syntax highlighting to the prompt text based on selected model"""
    # First escape HTML
    escaped = escape_html(text)

    # Get patterns for current model
    patterns = get_token_patterns()

    if not patterns:
        return escaped

    # Build replacement list - we need to escape patterns for HTML-escaped text
    # and then apply regex replacements
    result = escaped

    for pattern, color_key in patterns:
        css_class = COLOR_CLASS_MAP.get(color_key, "token-dsml")

        # Convert the pattern to match HTML-escaped text
        # Replace < with &lt; and > with &gt; in the pattern
        html_pattern = pattern.replace("<", "&lt;").replace(">", "&gt;")

        # Escape special regex characters that aren't meant to be regex
        # but keep actual regex patterns working
        if not any(
            c in pattern
            for c in ["+", "*", "?", "[", "]", "(", ")", "{", "}", "|", "^", "$", "."]
        ):
            # Simple string pattern - escape for regex
            html_pattern = re.escape(html_pattern)

        try:
            result = re.sub(
                f"({html_pattern})", rf'<span class="{css_class}">\1</span>', result
            )
        except re.error:
            # If regex fails, try simple string replacement
            html_literal = pattern.replace("<", "&lt;").replace(">", "&gt;")
            if html_literal in result:
                result = result.replace(
                    html_literal, f'<span class="{css_class}">{html_literal}</span>'
                )

    return result


def get_highlight_styles() -> str:
    """Return CSS styles for syntax highlighting"""
    return """
        .highlighted-prompt {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 13px;
            line-height: 1.5;
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
        }
        .token-bos, .token-eos {
            color: #c586c0;
            font-weight: bold;
        }
        .token-role {
            color: #ce9178;
            font-weight: bold;
        }
        .token-think {
            color: #d16d9e;
            font-weight: bold;
        }
        .token-dsml {
            color: #569cd6;
            font-weight: bold;
        }
        .token-func {
            color: #6a9955;
            font-weight: bold;
        }
    """
