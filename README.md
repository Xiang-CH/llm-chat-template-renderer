# Prompt Template Builder

A Streamlit web app for building and visualizing chat prompts for various LLMs. Convert chat messages into model-specific prompt formats with syntax highlighting.

<img width="1463" height="993" alt="Screenshot 2026-01-29 at 3 28 49 PM" src="https://github.com/user-attachments/assets/f69f0797-e09f-463c-b665-e2bef42f8bf4" />

## Supported Models

- **DeepSeek V3.1**
- **Qwen3**
- **GLM-4.5**
- **MiniMax-M2**

## Features

- **Model Selector** - Switch between different model templates
- **Message Editor** - Add, edit, delete, and reorder messages
- **Role Support** - System, user, assistant, tool, and developer roles
- **Reasoning Content** - Support for thinking/reasoning in assistant messages
- **Tool Calls** - Structured tool call editor with function name and JSON arguments
- **Tools Definition** - Include tool definitions in the prompt
- **Syntax Highlighting** - Color-coded special tokens in the preview
- **Token Counter** - Real-time token count using model-specific tokenizers
- **Export Options**:
  - Copy to clipboard
  - Save as .txt file
  - Save as PNG image with syntax highlighting
- **Edit Mode** - Directly edit the rendered prompt

## Installation

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
# Install dependencies
uv sync

# Run the app
uv run streamlit run app.py
```

The app will be available at http://localhost:8501

## Usage

### Basic Workflow

1. **Select a model** from the dropdown at the top of the sidebar
2. **Configure template options**:
   - Enable Thinking - Include reasoning content in `<think>` tags
   - Add Generation Prompt - Add assistant turn prompt at the end
3. **Add/edit messages** in the Messages section
4. **View the rendered prompt** in the main area with syntax highlighting
5. **Export** using Copy, Save .txt, or Save as Image buttons

### Adding Messages

Click "+ Add Message" to add a new message. For each message:

- **Role**: Select system, user, assistant, tool, or developer
- **Content**: Enter the message content
- **Reasoning Content** (assistant only): Internal reasoning shown in thinking mode
- **Tool Calls** (assistant only): Add function calls with name and JSON arguments

### Including Tools

1. Expand the "Tools (JSON)" section
2. Check "Include Tools"
3. Edit the JSON array of tool definitions

### Editing the Prompt Directly

1. Switch to the "Edit Prompt" tab
2. Modify the rendered prompt directly
3. Changes are reflected in the preview
4. Click "Reset to Generated Prompt" to discard edits

## Project Structure

```
prompt-builder/
├── app.py                      # Main entry point
├── chat_templates/             # Jinja2 templates for each model
│   ├── deepseek-v3.1.jinja
│   ├── qwen3.jinja
│   ├── glm-4.5.jinja
│   └── minimax-m2.jinja
├── components/
│   ├── config.py               # Model definitions and defaults
│   ├── state.py                # Session state management
│   ├── sidebar.py              # Sidebar UI components
│   ├── main_area.py            # Main content area
│   ├── prompt.py               # Prompt generation
│   ├── template_renderer.py    # Jinja2 template rendering
│   ├── highlighter.py          # HTML syntax highlighting
│   └── image_renderer.py       # PNG image generation
├── pyproject.toml              # Project dependencies
└── uv.lock                     # Locked dependency versions
```

## Adding a New Model

1. Add a Jinja2 template file to `chat_templates/`
2. Add a `ModelConfig` entry in `components/config.py`:

```python
"model-key": ModelConfig(
    name="Display Name",
    template_file="template-file.jinja",
    tokenizer_id="huggingface/tokenizer-id",
    bos_token="<bos>",
    eos_token="<eos>",
    token_patterns=[
        (r"<bos>", "bos_eos"),
        (r"<eos>", "bos_eos"),
        # Add patterns for syntax highlighting
    ],
    template_vars={"enable_thinking": True},
),
```

## Syntax Highlighting Colors

| Token Type | Color | Examples |
|------------|-------|----------|
| BOS/EOS | Purple | `<\|begin▁of▁sentence\|>`, `<\|im_start\|>` |
| Role | Orange | `<\|User\|>`, `<\|Assistant\|>` |
| Think | Magenta | `<think>`, `</think>` |
| DSML/Args | Blue | `<arg_key>`, `<parameter>` |
| Functions | Green | `<tools>`, `<tool_call>` |

## Dependencies

- streamlit - Web UI framework
- transformers - Tokenizers for token counting
- jinja2 - Template rendering
- pillow - Image generation

## License

MIT
