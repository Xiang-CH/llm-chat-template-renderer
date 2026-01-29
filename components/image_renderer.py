"""
Image rendering for prompt output using Pillow
"""

import io
import re
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
import streamlit as st
from components.config import MODELS

# Color scheme matching the CSS highlighting
COLORS = {
    "background": (30, 30, 30),  # #1e1e1e
    "text": (212, 212, 212),  # #d4d4d4
    "bos_eos": (197, 134, 192),  # #c586c0 - purple
    "role": (206, 145, 120),  # #ce9178 - orange
    "think": (209, 109, 158),  # #d16d9e - magenta
    "dsml": (86, 156, 214),  # #569cd6 - blue
    "func": (106, 153, 85),  # #6a9955 - green
}


def get_token_patterns() -> List[Tuple[str, str]]:
    """Get token patterns for the currently selected model"""
    model_key = st.session_state.get("selected_model", "deepseek-v3.1")
    if model_key in MODELS:
        return MODELS[model_key].token_patterns
    return []


def get_font(size: int = 14) -> ImageFont.FreeTypeFont:
    """Get a monospace font, falling back to default if needed"""
    font_paths = [
        "/System/Library/Fonts/Monaco.ttf",  # macOS
        "/System/Library/Fonts/SFNSMono.ttf",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",  # Arch Linux
        "C:\\Windows\\Fonts\\consola.ttf",  # Windows
        "C:\\Windows\\Fonts\\cour.ttf",  # Windows fallback
    ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue

    # Fall back to default font
    return ImageFont.load_default()


def tokenize_with_colors(text: str) -> List[Tuple[str, str]]:
    """
    Parse text and return list of (text, color_key) tuples.
    Handles syntax highlighting tokens based on selected model.
    """
    patterns = get_token_patterns()

    if not patterns:
        return [(text, "text")]

    # Build a combined pattern for all tokens
    # Need to handle patterns that might be regex vs literal strings
    regex_patterns = []
    for pattern, _ in patterns:
        # Check if it's already a regex pattern or needs escaping
        if any(
            c in pattern
            for c in ["+", "*", "?", "[", "]", "(", ")", "{", "}", "|", "^", "$"]
        ):
            regex_patterns.append(f"({pattern})")
        else:
            regex_patterns.append(f"({re.escape(pattern)})")

    combined_pattern = "|".join(regex_patterns)

    result = []
    last_end = 0

    try:
        for match in re.finditer(combined_pattern, text):
            # Add any text before this match as normal text
            if match.start() > last_end:
                result.append((text[last_end : match.start()], "text"))

            # Determine which pattern matched
            matched_text = match.group(0)
            color_key = "text"
            for pattern, key in patterns:
                try:
                    if re.fullmatch(pattern, matched_text):
                        color_key = key
                        break
                except re.error:
                    if pattern == matched_text:
                        color_key = key
                        break

            result.append((matched_text, color_key))
            last_end = match.end()
    except re.error:
        # If regex fails, return plain text
        return [(text, "text")]

    # Add remaining text
    if last_end < len(text):
        result.append((text[last_end:], "text"))

    return result


def wrap_text_preserve_tokens(text: str, width: int) -> str:
    """
    Wrap text at specified character width, trying to break at token boundaries.
    Preserves existing newlines and adds new ones for long lines.
    """
    # First, split by existing newlines
    lines = text.split("\n")
    wrapped_lines = []

    for line in lines:
        if len(line) <= width:
            wrapped_lines.append(line)
        else:
            # Try to wrap at token boundaries (special markers)
            # Look for patterns like <...> or <｜...｜> to break after
            current_line = ""
            i = 0
            while i < len(line):
                char = line[i]
                current_line += char

                # Check if we just closed a token
                if char in (">", "｜") and len(current_line) >= width * 0.7:
                    # Look ahead to see if there's more content
                    if i + 1 < len(line):
                        wrapped_lines.append(current_line)
                        current_line = ""
                elif len(current_line) >= width:
                    # Force break if line is too long
                    # Try to find a good break point (space or after >)
                    break_pos = -1
                    for j in range(
                        len(current_line) - 1, max(0, len(current_line) - 30), -1
                    ):
                        if current_line[j] in (" ", ">", "｜"):
                            break_pos = j + 1
                            break

                    if break_pos > 0:
                        wrapped_lines.append(current_line[:break_pos])
                        current_line = current_line[break_pos:]
                    else:
                        # No good break point, just break at width
                        wrapped_lines.append(current_line)
                        current_line = ""

                i += 1

            if current_line:
                wrapped_lines.append(current_line)

    return "\n".join(wrapped_lines)


def render_prompt_to_image(
    text: str,
    font_size: int = 28,
    padding: int = 40,
    line_height: float = 1.5,
    max_width: int = 2400,
    wrap_width: int = 120,
) -> bytes:
    """
    Render the prompt text to a PNG image with syntax highlighting.
    Returns PNG bytes.

    Args:
        text: The prompt text to render
        font_size: Font size in pixels
        padding: Padding around the content
        line_height: Line height multiplier
        max_width: Maximum image width in pixels
        wrap_width: Character width to wrap lines at
    """
    font = get_font(font_size)

    # Calculate character width (approximate for monospace)
    try:
        char_width = font.getlength("M")
    except AttributeError:
        # Fallback for older Pillow versions
        char_width = font_size * 0.6

    line_pixel_height = int(font_size * line_height)

    # Wrap text to prevent extremely long lines
    wrapped_text = wrap_text_preserve_tokens(text, wrap_width)

    # Split text into lines
    lines = wrapped_text.split("\n")

    # Calculate image dimensions
    max_line_len = max(len(line) for line in lines) if lines else 0
    content_width = int(max_line_len * char_width)
    img_width = min(content_width + padding * 2, max_width)
    img_height = len(lines) * line_pixel_height + padding * 2

    # Ensure minimum dimensions
    img_width = max(img_width, 400)
    img_height = max(img_height, 100)

    # Create image
    img = Image.new("RGB", (img_width, img_height), COLORS["background"])
    draw = ImageDraw.Draw(img)

    # Render each line
    y = padding
    for line in lines:
        tokens = tokenize_with_colors(line)
        x = padding

        for token_text, color_key in tokens:
            color = COLORS.get(color_key, COLORS["text"])
            draw.text((x, y), token_text, font=font, fill=color)
            try:
                x += font.getlength(token_text)
            except AttributeError:
                x += len(token_text) * char_width

        y += line_pixel_height

    # Convert to PNG bytes
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return buffer.getvalue()
