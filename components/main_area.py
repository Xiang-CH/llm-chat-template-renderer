"""
Main content area UI components
"""

import json
import streamlit as st
import streamlit.components.v1 as components
from components.prompt import generate_prompt, count_tokens
from components.highlighter import highlight_prompt, get_highlight_styles
from components.image_renderer import render_prompt_to_image


def render_main_area():
    """Render the main content area with prompt output"""
    st.title("Rendered Prompt")

    # Generate prompt
    generated_prompt = generate_prompt()

    # Determine which prompt to display
    if (
        st.session_state.use_edited_prompt
        and st.session_state.edited_prompt is not None
    ):
        display_prompt = st.session_state.edited_prompt
    else:
        display_prompt = generated_prompt
        st.session_state.edited_prompt = generated_prompt

    # Token count
    token_count = count_tokens(display_prompt)

    # Display metrics
    render_metrics(token_count, display_prompt)

    # Tabs for highlighted view and editable view
    tab1, tab2 = st.tabs(["Preview", "Edit Prompt"])

    with tab1:
        render_preview_tab(display_prompt)

    with tab2:
        render_edit_tab(display_prompt, generated_prompt)


def render_metrics(token_count: int, display_prompt: str):
    """Render metrics bar"""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tokens", f"{token_count:,}")
    with col2:
        st.metric("Characters", f"{len(display_prompt):,}")
    with col3:
        st.metric("Messages", len(st.session_state.messages))


def render_preview_tab(display_prompt: str):
    """Render the preview tab with syntax highlighting"""
    # Render highlighted prompt
    render_highlighted_prompt(display_prompt)

    # Action buttons for preview
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
    with btn_col1:
        render_copy_button(display_prompt)

    with btn_col2:
        # Download as image file
        image_bytes = render_prompt_to_image(display_prompt)
        st.download_button(
            label="Save as Image",
            data=image_bytes,
            file_name="prompt.png",
            mime="image/png",
        )


def render_copy_button(display_prompt: str):
    """Render copy to clipboard button"""
    copy_js = f"""
    <script>
    function copyToClipboard() {{
        const text = {json.dumps(display_prompt)};
        navigator.clipboard.writeText(text).then(function() {{
            document.getElementById('copy-status').innerText = 'Copied!';
            setTimeout(function() {{
                document.getElementById('copy-status').innerText = '';
            }}, 2000);
        }});
    }}
    </script>
    <button onclick="copyToClipboard()" style="padding: 8px 16px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: #f0f0f0;">Copy</button>
    <span id="copy-status" style="margin-left: 8px; color: green;"></span>
    """
    components.html(copy_js, height=45)


def render_highlighted_prompt(display_prompt: str):
    """Render the syntax highlighted prompt"""
    highlighted = highlight_prompt(display_prompt)
    # Calculate height based on content (approximate lines * line height)
    num_lines = display_prompt.count("\n") + 1
    height = min(max(num_lines * 20 + 40, 1000), 400)

    styles = get_highlight_styles()
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
        margin: 0;
        padding: 0;
    }}
    {styles}
    </style>
    </head>
    <body>
    <pre class="highlighted-prompt">{highlighted}</pre>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=True)


def render_edit_tab(display_prompt: str, generated_prompt: str):
    """Render the edit tab"""
    st.caption(
        "Edit the prompt directly. Changes here won't sync back to the message controls."
    )
    edited = st.text_area(
        "Edit Prompt",
        value=display_prompt,
        height=500,
        key="prompt_editor",
        label_visibility="collapsed",
    )

    if edited != display_prompt:
        st.session_state.edited_prompt = edited
        st.session_state.use_edited_prompt = True

    # Reset button
    if st.session_state.use_edited_prompt:
        if st.button("Reset to Generated Prompt"):
            st.session_state.use_edited_prompt = False
            st.session_state.edited_prompt = generated_prompt
            st.rerun()
