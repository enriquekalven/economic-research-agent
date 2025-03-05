#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Main file to run the FastAPI server."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from server.common import types
from server.common.logging import logger


app = FastAPI()


@app.get("/")
async def root():
    return 200


@app.post("/generate")
async def send_message(request: types.MessageRequest):
    """API Route for sending chat message."""
    try:
        logger.info("Sending chat message")

        response = {
            "text": request.text,
            "session_id": request.session_id
        }
        return JSONResponse(
            content=response,
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error sending request: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
