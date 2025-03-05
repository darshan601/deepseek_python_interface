import re
from typing import Dict, List
import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

# Custom CSS styling
st.markdown("""
<style>
    /* Existing styles */
    .main {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #2d2d2d;
    }
    .stTextInput textarea {
        color: #ffffff !important;
    }
    
    /* Add these new styles for select box */
    .stSelectbox div[data-baseweb="select"] {
        color: white !important;
        background-color: #3d3d3d !important;
    }
    
    .stSelectbox svg {
        fill: white !important;
    }
    
    .stSelectbox option {
        background-color: #2d2d2d !important;
        color: white !important;
    }
    
    /* For dropdown menu items */
    div[role="listbox"] div {
        background-color: #2d2d2d !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title(" DeepSeek Code Companion ")
st.caption(" Your AI Pair Programmer with Debugging Superpower")

with st.sidebar:
    st.header(" Configuration ")
    selected_model = st.selectbox(
        "Choose Model",
        ["deepseek-r1:1.5b", "deepseek-r1:3b","qwen2.5:1.5b"],
        index=0
    )
    st.divider()
    st.markdown("### Model Capabilities")
    st.markdown('''
    -- Python expert \n
    -- Debugging expert \n
    -- Code Documentation \n
    -- Solution Design \n
    ''')
    st.divider()
    st.markdown("Built with [Ollama] | [LangChain]")

# initiate the chat engine
llm_engine=ChatOllama(
    model=selected_model,
    base_url="http://localhost:11434",
    temperature=0.3
)

#System prompt configuration
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI coding assistant. Provide concise, correct solutions "
    "Your strategic print statements for debugging. Always respond in English."
)

# Session state management
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role":"ai", "content":"Hi! I am DeepSeek. How can I help you code today ? "}]

# chat_container
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"],unsafe_allow_html=True)

# chat input and processing
user_query = st.chat_input("Type your coding question here....")


# def parse_ai_response(response: str) -> Dict[str, str]:
#     """
#     Parse the AI response to extract think and main content sections.
    
#     Args:
#         response (str): Full AI response potentially containing <think> tags
    
#     Returns:
#         Dict with 'think' and 'content' keys
#     """
#     # Use regex to extract think and content sections
#     think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
#     content_match = re.sub(r'<think>.*?</think>', '\n', response, flags=re.DOTALL).strip()
    
#     return {
#         'think': think_match.group(1).strip() if think_match else '',
#         'content': content_match
#     }

# def display_ai_response(parsed_response: Dict[str, str]):
#     """
#     Display AI response with styled think and content sections.
    
#     Args:
#         parsed_response (Dict): Parsed response with 'think' and 'content'
#     """
#     # Display think section with a different style
#     if parsed_response['think']:
#         st.markdown(
#             f"*Reasoning:*", 
#             help="Behind-the-scenes thought process"
#         )
#         st.markdown(
#             f'<div style="background-color: blue; padding: 10px; border-radius: 5px; font-style: italic; color: #666;">{parsed_response["think"]}</div>', 
#             unsafe_allow_html=True
#         )
    
#     # Display main content
#     st.markdown(parsed_response['content'])

def generate_ai_response(prompt_chain):
    processing_pipeline=prompt_chain | llm_engine | StrOutputParser()
    return  processing_pipeline.invoke({})
    # parsed_response = parse_ai_response(full_response)
    # return parsed_response

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    return ChatPromptTemplate.from_messages(prompt_sequence)


def process_think_section(response: str):
    """
    Process the response to style the <think> section.
    
    Args:
        response (str): Full AI response
    
    Returns:
        str: Markdown-formatted response with styled think section
    """
    # Use regex to find <think> content
    think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
    
    if think_match:
        # Extract think content
        think_content = think_match.group(1).strip()
        
        # Create a styled think section
        styled_think = f"""
        <div style="
            background-color: #1a1a1a;
            color: #ffffff;
            border-left: 4px solid #4a90e2; 
            padding: 10px; 
            margin-bottom: 10px; 
            font-style: italic; 
        ">
        <b>🤔 AI Reasoning Process:</b><br>
        {think_content}
        </div>
        """
        
        # Replace the entire <think> tag with the styled version
        processed_response = re.sub(r'<think>.*?</think>', styled_think, response, flags=re.DOTALL)
        
        return processed_response
    
    # If no <think> tag, return original response
    return response


if user_query:
    # add user message to log
    st.session_state.message_log.append({"role":"user", "content":user_query})

    # Generate AI response
    with st.spinner("Processing ......."):
        prompt_chain = build_prompt_chain()
        parsed_ai_response = generate_ai_response(prompt_chain)
        print(parsed_ai_response)

        # Process the response to style <think> section
        styled_response = process_think_section(parsed_ai_response)

    # Add AI response to log
    st.session_state.message_log.append(
        {
            "role":"ai", 
            "content": styled_response
        }
        )

    # display_ai_response(parsed_ai_response)

    # rerun to update chat display
    st.rerun()