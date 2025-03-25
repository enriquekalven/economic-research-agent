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
Styling for streamlit UI
"""

MARKDOWN_STR = """
<style>
button[kind="primary"] {
    background: none!important;
    border: 0;
    padding: 20!important;
    color: grey !important;
    text-decoration: none;
    cursor: pointer;
    border: none !important;
    # float: right;
}
button[kind="primary"]:hover {
    text-decoration: none;
    color: white !important;
}
button[kind="primary"]:focus {
    outline: none !important;
    box-shadow: none !important;
    color:  !important;
}

.main-message {
    height: 80vh;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .stChatMessage {
    background-color: transparent;
  }
  .main-message h1 {
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
  }

  .stChatInput button {
    height: 100%
  }

  .stChatInput div, textarea {
    background: transparent;
    border: none;
  }
  .stChatInput .st-emotion-cache-yd4u6l {
    border: 2px solid #ddd; /* Light border */
  }
  .stChatInput textarea, .stChatInput .st-emotion-cache-yd4u6l {
    max-width: 100%; /* Make it responsive */
    padding: 28px 15px;
    border-radius: 25px; /* Rounded corners */
    font-size: 16px;
    box-sizing: border-box; /* Include padding and border in element's total width and height */
    outline: none; /* Remove default focus outline */
  }
  .prompt-boxes {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
    }
   .prompt-box {
        margin: 10px;
        padding: 10px;
        border-radius: 30px;
        border: 1px solid #D3DBE5;
        cursor: pointer;
        font-size: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
   }
    .prompt-box img{
        margin: 10px;
    }
    .header {

    }

    .chat-message.user, .chat-message.assistant {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        width: 80%;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        margin-left: auto;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        margin-right: auto;
    }
    .stChatInput textarea {
        border-radius: 1rem;
        padding: 0.5rem 1rem;
    }
</style>
"""
