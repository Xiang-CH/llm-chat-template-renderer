"""
Sidebar UI components
"""

import json
from typing import Dict, Any
import streamlit as st
from components.state import add_message, delete_message, move_message
from components.config import MODELS, MODEL_NAMES


def render_sidebar():
    """Render the left sidebar with controls"""
    with st.sidebar:
        st.title("Prompt Builder")

        render_model_selector()
        render_template_options()
        render_tools_section()
        render_messages_section()


def render_model_selector():
    """Render model selector dropdown"""

    def on_model_change():
        st.session_state.selected_model = st.session_state.model_select
        st.session_state.use_edited_prompt = False

    model_keys = list(MODELS.keys())
    current_idx = (
        model_keys.index(st.session_state.selected_model)
        if st.session_state.selected_model in model_keys
        else 0
    )

    st.selectbox(
        "Model Template",
        options=model_keys,
        format_func=lambda x: MODEL_NAMES.get(x, x),
        index=current_idx,
        key="model_select",
        on_change=on_model_change,
        help="Select the model template to use",
    )


def render_template_options():
    """Render template configuration options"""
    with st.expander("Template Options", expanded=True):

        def on_thinking_change():
            st.session_state.enable_thinking = st.session_state.enable_thinking_checkbox
            st.session_state.use_edited_prompt = False

        st.checkbox(
            "Enable Thinking",
            value=st.session_state.enable_thinking,
            key="enable_thinking_checkbox",
            on_change=on_thinking_change,
            help="Enable thinking/reasoning mode",
        )

        def on_gen_prompt_change():
            st.session_state.add_generation_prompt = (
                st.session_state.add_gen_prompt_checkbox
            )
            st.session_state.use_edited_prompt = False

        st.checkbox(
            "Add Generation Prompt",
            value=st.session_state.add_generation_prompt,
            key="add_gen_prompt_checkbox",
            on_change=on_gen_prompt_change,
            help="Add assistant turn prompt at the end",
        )


def render_tools_section():
    """Render tools configuration section"""
    with st.expander("Tools (JSON)", expanded=False):

        def on_include_tools_change():
            st.session_state.include_tools = st.session_state.include_tools_checkbox
            st.session_state.use_edited_prompt = False

        st.checkbox(
            "Include Tools",
            value=st.session_state.include_tools,
            key="include_tools_checkbox",
            on_change=on_include_tools_change,
            help="Include tools definition in the prompt",
        )

        tools_input = st.text_area(
            "Tools Definition",
            value=st.session_state.tools_json,
            height=200,
            label_visibility="collapsed",
            disabled=not st.session_state.include_tools,
        )

        if tools_input != st.session_state.tools_json:
            st.session_state.tools_json = tools_input
            try:
                st.session_state.tools = (
                    json.loads(tools_input) if tools_input.strip() else []
                )
                st.session_state.use_edited_prompt = False
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")


def render_messages_section():
    """Render messages section"""
    st.subheader("Messages")

    for i, msg in enumerate(st.session_state.messages):
        render_message_editor(i, msg)

    st.button("+ Add Message", on_click=add_message, use_container_width=True)


def render_message_editor(index: int, msg: Dict[str, Any]):
    """Render an individual message editor"""
    role = msg.get("role", "user")
    role_labels = {
        "system": "S",
        "user": "U",
        "developer": "D",
        "assistant": "A",
        "tool": "T",
    }

    with st.expander(
        f"[{role_labels.get(role, '?')}] {role.capitalize()}", expanded=True
    ):
        # Role selector
        roles = ["system", "user", "developer", "assistant", "tool"]
        current_idx = roles.index(role) if role in roles else 1
        new_role = st.selectbox(
            "Role", options=roles, index=current_idx, key=f"role_{index}"
        )
        if new_role != role:
            st.session_state.messages[index]["role"] = new_role
            st.session_state.use_edited_prompt = False

        # Content
        content_value = msg.get("content") or ""
        content = st.text_area(
            "Content", value=content_value, height=100, key=f"content_{index}"
        )
        if content != content_value:
            st.session_state.messages[index]["content"] = content if content else None
            st.session_state.use_edited_prompt = False

        # Conditional fields for assistant role
        if new_role == "assistant":
            render_assistant_fields(index, msg)

        # Action buttons
        render_message_actions(index)


def render_assistant_fields(index: int, msg: Dict[str, Any]):
    """Render additional fields for assistant messages"""
    # Reasoning content (for thinking mode)
    if st.session_state.enable_thinking:
        reasoning = st.text_area(
            "Reasoning Content",
            value=msg.get("reasoning_content", ""),
            height=80,
            key=f"reasoning_{index}",
            help="Internal reasoning (shown in thinking mode)",
        )
        if reasoning != msg.get("reasoning_content", ""):
            st.session_state.messages[index]["reasoning_content"] = reasoning
            st.session_state.use_edited_prompt = False

    # Tool calls - structured input
    st.markdown("**Tool Calls**")

    tool_calls = msg.get("tool_calls", [])

    # Add tool call button
    if st.button("+ Add Tool Call", key=f"add_tool_call_{index}"):
        if "tool_calls" not in st.session_state.messages[index]:
            st.session_state.messages[index]["tool_calls"] = []
        st.session_state.messages[index]["tool_calls"].append(
            {"type": "function", "function": {"name": "", "arguments": {}}}
        )
        st.session_state.use_edited_prompt = False
        st.rerun()

    # Render each tool call
    for tc_idx, tool_call in enumerate(tool_calls):
        render_tool_call_editor(index, tc_idx, tool_call)


def render_tool_call_editor(msg_index: int, tc_idx: int, tool_call: Dict[str, Any]):
    """Render a single tool call editor"""
    func = tool_call.get("function", {})
    with st.container():
        st.markdown(f"*Tool Call {tc_idx + 1}*")

        tc_col1, tc_col2 = st.columns([3, 1])
        with tc_col1:
            func_name = st.text_input(
                "Function Name",
                value=func.get("name", ""),
                key=f"tc_name_{msg_index}_{tc_idx}",
            )
            if func_name != func.get("name", ""):
                st.session_state.messages[msg_index]["tool_calls"][tc_idx]["function"][
                    "name"
                ] = func_name
                st.session_state.use_edited_prompt = False

        with tc_col2:
            st.space()
            if st.button(
                "❌", key=f"del_tc_{msg_index}_{tc_idx}", help="Remove tool call"
            ):
                st.session_state.messages[msg_index]["tool_calls"].pop(tc_idx)
                st.session_state.use_edited_prompt = False
                st.rerun()

        # Handle arguments - could be dict or string
        args = func.get("arguments", {})
        if isinstance(args, dict):
            args_str = json.dumps(args, indent=2)
        else:
            args_str = str(args)

        func_args = st.text_area(
            "Arguments (JSON)",
            value=args_str,
            height=60,
            key=f"tc_args_{msg_index}_{tc_idx}",
        )
        if func_args != args_str:
            # Validate and store as dict
            try:
                parsed_args = json.loads(func_args)
                st.session_state.messages[msg_index]["tool_calls"][tc_idx]["function"][
                    "arguments"
                ] = parsed_args
                st.session_state.use_edited_prompt = False
            except json.JSONDecodeError:
                st.error("Invalid JSON for arguments")

        st.divider()


def render_message_actions(index: int):
    """Render action buttons for a message"""
    col1, col2, col3 = st.columns(3)
    with col1:
        col11, col12 = st.columns(2)
        with col11:
            if st.button("⬆️", key=f"up_{index}", help="Move up", disabled=index == 0):
                move_message(index, -1)
                st.rerun()
        with col12:
            if st.button(
                "⬇️",
                key=f"down_{index}",
                help="Move down",
                disabled=index == len(st.session_state.messages) - 1,
            ):
                move_message(index, 1)
                st.rerun()
    with col2:
        pass  # Spacer
    with col3:
        if st.button(
            "❌",
            key=f"del_{index}",
            help="Remove the message from the list",
            disabled=len(st.session_state.messages) <= 1,
            use_container_width=True,
        ):
            delete_message(index)
            st.rerun()
