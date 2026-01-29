"""
Jinja2 template renderer for chat prompts
"""

import os
import json
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import streamlit as st

from components.config import MODELS

# Template directory
TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "chat_templates"
)


def custom_tojson(value, ensure_ascii=True, indent=None):
    """Custom tojson filter that supports ensure_ascii parameter"""
    return json.dumps(value, ensure_ascii=ensure_ascii, indent=indent)


def raise_exception(message):
    """Helper function to raise exceptions from templates"""
    raise ValueError(message)


def get_jinja_env() -> Environment:
    """Get or create Jinja2 environment"""
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Add custom tojson filter that supports ensure_ascii
    env.filters["tojson"] = custom_tojson
    # Add raise_exception to globals
    env.globals["raise_exception"] = raise_exception
    return env


def prepare_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare messages for template rendering.
    Converts tool_calls arguments from JSON strings to dicts if needed.
    """
    prepared = []
    for msg in messages:
        msg_copy = msg.copy()

        # Handle tool_calls - ensure arguments are dicts, not strings
        if "tool_calls" in msg_copy and msg_copy["tool_calls"]:
            tool_calls = []
            for tc in msg_copy["tool_calls"]:
                tc_copy = tc.copy()
                if "function" in tc_copy:
                    func = tc_copy["function"].copy()
                    if isinstance(func.get("arguments"), str):
                        try:
                            func["arguments"] = json.loads(func["arguments"])
                        except json.JSONDecodeError:
                            func["arguments"] = {}
                    tc_copy["function"] = func
                tool_calls.append(tc_copy)
            msg_copy["tool_calls"] = tool_calls

        prepared.append(msg_copy)

    return prepared


def render_template(
    model_key: str,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    add_generation_prompt: bool = True,
    **extra_vars,
) -> str:
    """
    Render a chat template for the specified model.

    Args:
        model_key: Key from MODELS dict
        messages: List of chat messages
        tools: Optional list of tool definitions
        add_generation_prompt: Whether to add generation prompt
        **extra_vars: Additional template variables

    Returns:
        Rendered prompt string
    """
    if model_key not in MODELS:
        raise ValueError(f"Unknown model: {model_key}")

    config = MODELS[model_key]
    env = get_jinja_env()

    try:
        template = env.get_template(config.template_file)
    except Exception as e:
        return f"Error loading template {config.template_file}: {e}"

    # Prepare messages
    prepared_messages = prepare_messages(messages)

    # Build template context
    context = {
        "messages": prepared_messages,
        "tools": tools if tools else None,
        "add_generation_prompt": add_generation_prompt,
        "bos_token": config.bos_token,
        "eos_token": config.eos_token,
        **config.template_vars,
        **extra_vars,
    }

    try:
        return template.render(**context)
    except Exception as e:
        return f"Error rendering template: {e}"


@st.cache_resource
def load_tokenizer(tokenizer_id: str):
    """Load and cache the tokenizer for a model"""
    from transformers import AutoTokenizer

    try:
        return AutoTokenizer.from_pretrained(tokenizer_id, use_fast=True)
    except Exception as e:
        st.warning(f"Could not load tokenizer {tokenizer_id}: {e}")
        return None


def count_tokens(text: str, model_key: str) -> int:
    """Count tokens for a given model"""
    if model_key not in MODELS:
        return 0

    config = MODELS[model_key]
    tokenizer = load_tokenizer(config.tokenizer_id)

    if tokenizer is None:
        return 0

    try:
        return len(tokenizer.encode(text))
    except Exception:
        return 0
