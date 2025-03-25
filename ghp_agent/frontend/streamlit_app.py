# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
main streamlit file
"""

# pylint: disable=inconsistent-quotes
# mypy: disable-error-code="arg-type"
import json
import uuid
import os
import base64
from collections.abc import Sequence
from functools import partial
from typing import Any

import streamlit as st
from langchain_core.messages import HumanMessage
from streamlit_feedback import streamlit_feedback

from frontend.side_bar import SideBar
from frontend.style.app_markdown import MARKDOWN_STR
from frontend.utils.local_chat_history import LocalChatMessageHistory
from frontend.utils.message_editing import MessageEditing
from frontend.utils.multimodal_utils import (
    format_content,
    get_parts_from_files,
)
from frontend.utils.stream_handler import (
    Client,
    StreamHandler,
    get_chain_response,
)

USER = "my_user"
EMPTY_CHAT_NAME = "Empty chat"


def setup_page() -> None:
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="Playground",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    # st.title("")
    st.markdown(MARKDOWN_STR, unsafe_allow_html=True)


def initialize_session_state() -> None:
    """Initialize the session state with default values."""
    if "user_chats" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state.uploader_key = 0
        st.session_state.run_id = None
        st.session_state.user_id = USER
        st.session_state["gcs_uris_to_be_sent"] = ""
        st.session_state.modified_prompt = None
        st.session_state.first_prompt = False
        st.session_state.session_db = LocalChatMessageHistory(
            session_id=st.session_state["session_id"],
            user_id=st.session_state["user_id"],
        )
        st.session_state.user_chats = (
            st.session_state.session_db.get_all_conversations()
        )
        st.session_state.user_chats[st.session_state["session_id"]] = {
            "title": EMPTY_CHAT_NAME,
            "messages": [],
        }


def display_messages() -> None:
    """Display all messages in the current chat session."""
    messages = st.session_state.user_chats[st.session_state["session_id"]][
        "messages"
    ]
    tool_calls_map = {}  # Map tool_call_id to tool call input

    for i, message in enumerate(messages):
        if message["type"] in ["ai", "human"] and message["content"]:
            display_chat_message(message, i)
        elif message.get("tool_calls"):
            # Store each tool call input mapped by its ID
            for tool_call in message["tool_calls"]:
                tool_calls_map[tool_call["id"]] = tool_call
        elif message["type"] == "tool":
            # Look up the corresponding tool call input by ID
            tool_call_id = message["tool_call_id"]
            if tool_call_id in tool_calls_map:
                display_tool_output(tool_calls_map[tool_call_id], message)
            else:
                st.error(
                    f"Could not find tool call input for ID: {tool_call_id}"
                )
        else:
            st.error(f"Unexpected message type: {message['type']}")
            st.write("Full messages list:", messages)
            raise ValueError(f"Unexpected message type: {message['type']}")


def display_chat_message(message: dict[str, Any], index: int) -> None:
    """Display a single chat message with edit, refresh, and delete options."""
    chat_message = st.chat_message(message["type"])
    with chat_message:
        st.markdown(format_content(message["content"]), unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 94])
        display_message_buttons(message, index, col1, col2, col3)


def display_message_buttons(
    message: dict[str, Any], index: int, col1: Any, col2: Any, col3: Any
) -> None:
    """Display edit, refresh, and delete buttons for a chat message."""
    edit_button = f"{index}_edit"
    refresh_button = f"{index}_refresh"
    delete_button = f"{index}_delete"
    content = (
        message["content"]
        if isinstance(message["content"], str)
        else message["content"][-1]["text"]
    )

    with col1:
        st.button(label="✎", key=edit_button, type="primary")
    if message["type"] == "human":
        with col2:
            st.button(
                label="⟳",
                key=refresh_button,
                type="primary",
                on_click=partial(
                    MessageEditing.refresh_message, st, index, content
                ),
            )
        with col3:
            st.button(
                label="X",
                key=delete_button,
                type="primary",
                on_click=partial(MessageEditing.delete_message, st, index),
            )

    if st.session_state[edit_button]:
        st.text_area(
            "Edit your message:",
            value=content,
            key=f"edit_box_{index}",
            on_change=partial(
                MessageEditing.edit_message, st, index, message["type"]
            ),
        )


def display_tool_output(
    tool_call_input: dict[str, Any], tool_call_output: dict[str, Any]
) -> None:
    """Display the input and output of a tool call in an expander."""
    tool_expander = st.expander(label="Tool Calls:", expanded=False)
    with tool_expander:
        msg = (
            f"\n\nEnding tool: `{tool_call_input}` with\n **args:**\n"
            f"```\n{json.dumps(tool_call_input, indent=2)}\n```\n"
            f"\n\n**output:**\n "
            f"```\n{json.dumps(tool_call_output, indent=2)}\n```"
        )
        st.markdown(msg, unsafe_allow_html=True)


def handle_user_input(side_bar: SideBar) -> None:
    """Process user input, generate AI response, and update chat history."""
    prompt = st.chat_input() or st.session_state.modified_prompt
    if prompt:
        st.session_state.first_prompt = True
        st.session_state.modified_prompt = None
        parts = get_parts_from_files(
            upload_gcs_checkbox=st.session_state.checkbox_state,
            uploaded_files=side_bar.uploaded_files,
            gcs_uris=side_bar.gcs_uris,
        )
        st.session_state["gcs_uris_to_be_sent"] = ""
        parts.append({"type": "text", "text": prompt})
        st.session_state.user_chats[st.session_state["session_id"]][
            "messages"
        ].append(HumanMessage(content=parts).model_dump())

        display_user_input(parts)
        generate_ai_response(
            remote_agent_engine_id=side_bar.remote_agent_engine_id,
            agent_callable_path=side_bar.agent_callable_path,
            url=side_bar.url_input_field,
            authenticate_request=side_bar.should_authenticate_request,
        )
        update_chat_title()
        if len(parts) > 1:
            st.session_state.uploader_key += 1
        st.rerun()


def display_user_input(parts: Sequence[dict[str, Any]]) -> None:
    """Display the user's input in the chat interface."""
    human_message = st.chat_message("human")
    with human_message:
        existing_user_input = format_content(parts)
        st.markdown(existing_user_input, unsafe_allow_html=True)


def generate_ai_response(
    remote_agent_engine_id: str | None = None,
    agent_callable_path: str | None = None,
    url: str | None = None,
    authenticate_request: bool = False,
) -> None:
    """Generate and display the AI's response to the user's input."""
    ai_message = st.chat_message("ai")
    with ai_message:
        status = st.status("Generating answer🤖")
        stream_handler = StreamHandler(stm=st)
        client = Client(
            remote_agent_engine_id=remote_agent_engine_id,
            agent_callable_path=agent_callable_path,
            url=url,
            authenticate_request=authenticate_request,
        )
        get_chain_response(stm=st, client=client, stream_handler=stream_handler)
        status.update(label="Finished!", state="complete", expanded=False)


def update_chat_title() -> None:
    """Update the chat title if it's currently empty."""
    if (
        st.session_state.user_chats[st.session_state["session_id"]]["title"]
        == EMPTY_CHAT_NAME
    ):
        st.session_state.session_db.set_title(
            st.session_state.user_chats[st.session_state["session_id"]]
        )
    st.session_state.session_db.upsert_session(
        st.session_state.user_chats[st.session_state["session_id"]]
    )


def display_feedback(side_bar: SideBar) -> None:
    """Display a feedback component and log the feedback if provided."""
    if st.session_state.run_id is not None:
        feedback = streamlit_feedback(
            feedback_type="faces",
            optional_text_label="[Optional] Please provide an explanation",
            key=f"feedback-{st.session_state.run_id}",
        )
        if feedback is not None:
            client = Client(
                remote_agent_engine_id=side_bar.remote_agent_engine_id,
                agent_callable_path=side_bar.agent_callable_path,
                url=side_bar.url_input_field,
                authenticate_request=side_bar.should_authenticate_request,
            )
            client.log_feedback(
                feedback_dict=feedback,
                run_id=st.session_state.run_id,
            )

def get_image_url_from_path(image_path):
    """Gets a data URL from a local image path."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/jpg;base64,{encoded_string}" #or png, etc.
    else:
        return None


css_string = """
    <style>
        iframe {
            height: 80vh;
        }

        .stChatInput {
            width: 65%;
            margin: auto;
        }

        .stChatInput button {
            height: 100%;
        }

        .stChatInput div,
        .stChatInput textarea {
            background: transparent;
            border: none;
        }

        .stChatInput .st-emotion-cache-yd4u6l {
            border: 2px solid #ddd; /* Light border */
        }

        .stChatInput textarea,
        .stChatInput .st-emotion-cache-yd4u6l {
            max-width: 100%;
            padding: 28px 15px;
            border-radius: 25px;
            font-size: 16px;
            box-sizing: border-box; /* Include padding and border in element's total width and height */
            outline: none; /* Remove default focus outline */
        }

        .stChatMessage {
            background-color: white;
        }
    </style>
    """

html_string = f"""
<head>
<script>
function myFunction(arg) {{
    alert(arg);
}}
</script>
<style>
    body {{
        font-family: sans-serif;
    }}
  .main-message {{
    height: 80vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }}

  .main-message h1 {{
    font-family: sans-serif;
    font-size: 3em;
    font-weight: bold;
    text-align: center;
    color: #333;
    background: linear-gradient(to right, #71CC98, #00A0DD,#0076BB, #003B5C);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
    padding: 20px;
    border-radius: 10px;
  }}

  .prompt-boxes {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }}
   .prompt-box {{
        margin: 10px;
        padding: 10px;
        border-radius: 30px;
        border: 1px solid #D3DBE5;
        cursor: pointer;
        font-size: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
   }}
    .prompt-box img{{
        margin: 10px;
    }}
    .header {{
        background-color: white;
    }}

    .chat-message.user, .chat-message.assistant {{
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        width: 80%;
    }}
    .chat-message.user {{
        background-color: #e6f7ff;
        margin-left: auto;
    }}
    .chat-message.assistant {{
        background-color: #f0f0f0;
        margin-right: auto;
    }}
    .stChatInput textarea {{
        border-radius: 1rem;
        padding: 0.5rem 1rem;
    }}
    .main-content{{
        width: 60%;
        margin: auto;
    }}
</style>
</head>
<body>
  <div class="header">
    <img style="width: 500px" src="{get_image_url_from_path("frontend/assets/logo.png")}" alt="logo"/>
  </div>
  <div class="main-content"> 
    <div class="main-message">
        <h1>Which data report can I help you with?</h1>
    </div>
    <div class="prompt-boxes">
        <div class="prompt-box" onclick="myFunction('I want to gather data on Metro Matrix.')">
            <img src="{get_image_url_from_path("frontend/assets/home.png")}" alt="home"/>
            <div>I want to gather data on <b>Metro Matrix.</b></div>
        </div>
        <div class="prompt-box" onclick="myFunction('Hello2')">
            <img src="{get_image_url_from_path("frontend/assets/location.png")}" alt="location"/>
            <div>I want to gather data on <b>Headquarters Relocation.</b></div>
        </div>
        <div class="prompt-box" onclick="myFunction('Hello3')">
            <img style="width: 23px" src="{get_image_url_from_path("frontend/assets/company.png")}" alt="company"/>
            <div>I want to gather data on <b>Company Relocation.</b></div>
        </div>
    </div>
  </div>

</body>
"""

def main() -> None:
    """Main function to set up and run the Streamlit app."""
    setup_page()
    initialize_session_state()
    print("::::::::")
    print(st.session_state.first_prompt)
    if st.session_state.first_prompt is False:
        st.markdown(css_string, unsafe_allow_html=True) # Syntax error here
        st.components.v1.html(html_string)
    side_bar = SideBar(st=st)
    side_bar.init_side_bar()
    display_messages()
    handle_user_input(side_bar=side_bar)
    display_feedback(side_bar=side_bar)


if __name__ == "__main__":
    main()
