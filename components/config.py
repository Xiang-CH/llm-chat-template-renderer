"""
Configuration and constants for Prompt Builder
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """Configuration for a model template"""

    name: str  # Display name
    template_file: str  # Jinja2 template filename
    tokenizer_id: str  # HuggingFace tokenizer ID
    bos_token: str  # Beginning of sentence token
    eos_token: str  # End of sentence token (if any)
    # Token patterns for syntax highlighting: (pattern, color_key)
    # color_key: "bos_eos", "role", "think", "dsml", "func"
    token_patterns: List[tuple] = field(default_factory=list)
    # Template variables
    template_vars: Dict[str, Any] = field(default_factory=dict)


# Model configurations
MODELS: Dict[str, ModelConfig] = {
    "deepseek-v3.1": ModelConfig(
        name="DeepSeek V3.1",
        template_file="deepseek-v3.1.jinja",
        tokenizer_id="deepseek-ai/DeepSeek-V3.1",
        bos_token="<｜begin▁of▁sentence｜>",
        eos_token="<｜end▁of▁sentence｜>",
        token_patterns=[
            (r"<｜begin▁of▁sentence｜>", "bos_eos"),
            (r"<｜end▁of▁sentence｜>", "bos_eos"),
            (r"<｜User｜>", "role"),
            (r"<｜Assistant｜>", "role"),
            (r"<think>", "think"),
            (r"</think>", "think"),
            (r"<｜tool▁calls▁begin｜>", "func"),
            (r"<｜tool▁calls▁end｜>", "func"),
            (r"<｜tool▁call▁begin｜>", "func"),
            (r"<｜tool▁call▁end｜>", "func"),
            (r"<｜tool▁sep｜>", "func"),
            (r"<｜tool▁output▁begin｜>", "func"),
            (r"<｜tool▁output▁end｜>", "func"),
        ],
        template_vars={"thinking": True},
    ),
    "qwen3": ModelConfig(
        name="Qwen3",
        template_file="qwen3.jinja",
        tokenizer_id="Qwen/Qwen3-235B-A22B",
        bos_token="",
        eos_token="<|im_end|>",
        token_patterns=[
            (r"<\|im_start\|>", "bos_eos"),
            (r"<\|im_end\|>", "bos_eos"),
            (r"<\|im_start\|>system", "role"),
            (r"<\|im_start\|>user", "role"),
            (r"<\|im_start\|>assistant", "role"),
            (r"<think>", "think"),
            (r"</think>", "think"),
            (r"<tools>", "func"),
            (r"</tools>", "func"),
            (r"<tool_call>", "func"),
            (r"</tool_call>", "func"),
            (r"<tool_response>", "func"),
            (r"</tool_response>", "func"),
        ],
        template_vars={"enable_thinking": True},
    ),
    "glm-4.5": ModelConfig(
        name="GLM-4.5",
        template_file="glm-4.5.jinja",
        tokenizer_id="zai-org/GLM-4.5",
        bos_token="[gMASK]<sop>",
        eos_token="",
        token_patterns=[
            (r"\[gMASK\]", "bos_eos"),
            (r"<sop>", "bos_eos"),
            (r"<\|system\|>", "role"),
            (r"<\|user\|>", "role"),
            (r"<\|assistant\|>", "role"),
            (r"<\|observation\|>", "role"),
            (r"<think>", "think"),
            (r"</think>", "think"),
            (r"<tools>", "func"),
            (r"</tools>", "func"),
            (r"<tool_call>", "func"),
            (r"</tool_call>", "func"),
            (r"<tool_response>", "func"),
            (r"</tool_response>", "func"),
            (r"<arg_key>", "dsml"),
            (r"</arg_key>", "dsml"),
            (r"<arg_value>", "dsml"),
            (r"</arg_value>", "dsml"),
        ],
        template_vars={"enable_thinking": True},
    ),
    "minimax-m2": ModelConfig(
        name="MiniMax-M2",
        template_file="minimax-m2.jinja",
        tokenizer_id="MiniMaxAI/MiniMax-M2.1",
        bos_token="]~!b[",
        eos_token="[e~[",
        token_patterns=[
            (r"\]~!b\[", "bos_eos"),
            (r"\]~b\]", "bos_eos"),
            (r"\[e~\[", "bos_eos"),
            (r"\]~b\]system", "role"),
            (r"\]~b\]user", "role"),
            (r"\]~b\]ai", "role"),
            (r"\]~b\]tool", "role"),
            (r"<think>", "think"),
            (r"</think>", "think"),
            (r"<tools>", "func"),
            (r"</tools>", "func"),
            (r"<tool>", "func"),
            (r"</tool>", "func"),
            (r"<minimax:tool_call>", "func"),
            (r"</minimax:tool_call>", "func"),
            (r"<invoke[^>]*>", "func"),
            (r"</invoke>", "func"),
            (r"<parameter[^>]*>", "dsml"),
            (r"</parameter>", "dsml"),
            (r"<response>", "func"),
            (r"</response>", "func"),
        ],
        template_vars={},
    ),
}

# Default model
DEFAULT_MODEL = "qwen3"

# Get list of model names for dropdown
MODEL_NAMES = {key: config.name for key, config in MODELS.items()}

DEFAULT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Use this tool to search the web for relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

DEFAULT_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Why is the sky blue?"},
    {
        "role": "assistant",
        "reasoning_content": "The user asked why the sky is blue. I can use the search tool to find relevant information.",
        "content": None,
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "search",
                    "arguments": {"query": "Why is the sky blue?"},
                },
            }
        ],
    },
    {
        "role": "tool",
        "name": "search",
        "content": "The sky appears blue due to a phenomenon called Rayleigh scattering, which is the scattering of sunlight by the molecules and tiny particles in Earth's atmosphere.",
    },
    {
        "role": "assistant",
        "reasoning_content": "The search tool returned the following information: The sky appears blue due to a phenomenon called Rayleigh scattering.",
        "content": "The sky appears blue due to a phenomenon called Rayleigh scattering, which is the scattering of sunlight by the molecules and tiny particles in Earth's atmosphere.",
    },
]
