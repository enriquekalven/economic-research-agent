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
REST endpoints for Economic Research Agent (ERA).
"""

# pylint: disable=broad-except
import logging
import os
from collections.abc import Generator

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, StreamingResponse
from google.cloud import logging as google_cloud_logging
from langchain_core.runnables import RunnableConfig
from traceloop.sdk import Instruments, Traceloop

from economic_research_agent.agent import agent
from economic_research_agent.shared_libraries.helper import access_secret_version
from economic_research_agent.shared_libraries.tracing import CloudTraceLoggingSpanExporter
from economic_research_agent.shared_libraries.typing import (
    Feedback,
    InputChat,
    Request,
    dumps,
    ensure_valid_config,
)

# Standard ADK configuration (Use environment variables)
PROJECT_ID = os.getenv("PROJECT_ID", "economic-research-agent")
BEA_API_SECRET_KEY = os.getenv("BEA_API_SECRET_KEY", "BEA_API_KEY")

# Initialize FastAPI app and logging
app = FastAPI(
    title="Economic Research Agent (ERA)",
    description="Strategic consultancy API for regional economic analysis and site selection.",
)

# Initialize Telemetry
if os.getenv("ENABLE_TELEMETRY", "false").lower() == "true":
    try:
        Traceloop.init(
            app_name=app.title,
            disable_batch=False,
            exporter=CloudTraceLoggingSpanExporter(),
            instruments={Instruments.LANGCHAIN},
        )
    except Exception as e:
        logging.error("Failed to initialize Telemetry: %s", str(e))


def set_tracing_properties(config: RunnableConfig) -> None:
    """Sets tracing association properties for the current request.
    """
    if os.getenv("ENABLE_TELEMETRY", "false").lower() == "true":
        Traceloop.set_association_properties(
            {
                "log_type": "tracing",
                "run_id": str(config.get("run_id", "None")),
                "user_id": config.get("metadata", {}).pop("user_id", "None"),
                "session_id": config.get("metadata", {}).pop("session_id", "None"),
            }
        )


def stream_messages(
    user_input: InputChat,
    config: RunnableConfig | None = None,
) -> Generator[str, None, None]:
    """Stream events in response to an input chat.
    """
    config = ensure_valid_config(config=config)
    set_tracing_properties(config)
    input_dict = user_input.model_dump()

    for data in agent.stream(
        input_dict, config=config, stream_mode="messages"
    ):
        yield dumps(data) + "\n"


# Routes
@app.get("/", response_class=RedirectResponse)
def redirect_root_to_docs() -> RedirectResponse:
    """Redirect the root URL to the API documentation."""
    return RedirectResponse(url="/docs")


@app.post("/stream_messages")
def stream_chat_events(request: Request) -> StreamingResponse:
    """Stream chat events in response to an input request.
    """
    return StreamingResponse(
        stream_messages(user_input=request.input, config=request.config),
        media_type="text/event-stream",
    )


# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
