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
REST endpoints defined here
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

from app.agent import agent
from app.utils.helper import access_secret_version
from app.utils.tracing import CloudTraceLoggingSpanExporter
from app.utils.typing import (
    Feedback,
    InputChat,
    Request,
    dumps,
    ensure_valid_config,
)

# TODO: Change to a .env file with all constants / variables.
os.environ["PROJECT_ID"] = "ghp-poc"
os.environ["PROJECT_NUMBER"] = "489922131187"
os.environ["BEA_API_SECRET_KEY"] = "BEA_API_KEY"

PROJECT_ID = os.getenv("PROJECT_ID")
BEA_API_SECRET_KEY = os.getenv("BEA_API_SECRET_KEY")


os.getenv(
    "BEA_API_SECRET_KEY", "BEA_API_KEY")


# Ensure env variables are set.
if not PROJECT_ID or not BEA_API_SECRET_KEY:
    raise ValueError(
        "GCP_PROJECT_ID or SECRET_ID environment variables are not set.")


# Get BEA API key from Secret Manager.
bea_api_key = access_secret_version(
    project_id=PROJECT_ID, secret_id=BEA_API_SECRET_KEY)
os.environ["BEA_API_KEY"] = bea_api_key


# Initialize FastAPI app and logging
app = FastAPI(
    title="ghp_agent",
    description="API for interacting with the Agent ghp_agent",
)
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# Initialize Telemetry
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

    Args:
        config: Optional RunnableConfig containing request metadata
    """
    Traceloop.set_association_properties(
        {
            "log_type": "tracing",
            "run_id": str(config.get("run_id", "None")),
            "user_id": config["metadata"].pop("user_id", "None"),
            "session_id": config["metadata"].pop("session_id", "None"),
            "commit_sha": os.environ.get("COMMIT_SHA", "None"),
        }
    )


def stream_messages(
    user_input: InputChat,
    config: RunnableConfig | None = None,
) -> Generator[str, None, None]:
    """Stream events in response to an input chat.

    Args:
        user_input: The input chat messages
        config: Optional configuration for the runnable

    Yields:
        JSON serialized event data
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


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


@app.post("/stream_messages")
def stream_chat_events(request: Request) -> StreamingResponse:
    """Stream chat events in response to an input request.

    Args:
        request: The chat request containing input and config

    Returns:
        Streaming response of chat events
    """
    return StreamingResponse(
        stream_messages(user_input=request.input, config=request.config),
        media_type="text/event-stream",
    )


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
