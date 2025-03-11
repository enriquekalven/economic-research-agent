#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Main file to run the FastAPI server."""

import os
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types as genai_types

from server.common import types
from server.common.logging import logger
from server.agent.prompts import Prompts
from server.agent.models import MetroMatrixResult, HQRelocationResult, CompanyRelocationResult
from server.agent.functions.company_relocation_functions import find_company_relocation
from server.agent.functions.hq_relocation_functions import find_hq_relocation
from server.agent.functions.metro_matrix_functions import find_metro_matrix
from server.agent.functions.invalid_request_functions import invalid_request

# Initialize Fast API App and Gemini Client.
app = FastAPI()

genai_client = genai.Client(
    vertexai=True, project="ghp-poc", location="us-east4"
)

# Global Gemini Chat Agent
prompts = Prompts()  # Instantiate Prompts
global_gemini_agent_config = genai_types.GenerateContentConfig(
    system_instruction=prompts.initial_routing_prompt(),
    temperature=0.2,
    candidate_count=1,
    seed=42,
    tools=[
        find_metro_matrix,
        find_hq_relocation,
        find_company_relocation,
        invalid_request,
    ],
)
global_gemini_model = "gemini-1.5-flash-002"

@app.get("/")
async def root():
    return 200

@app.post("/generate")
async def send_message(request: types.MessageRequest):
    """API Route for sending chat message."""
    try:
        logger.info("Sending chat message")
        # prompts = Prompts()  # Instantiate Prompts

        # response = genai_client.models.generate_content(
        #     model="gemini-1.5-flash-002",  # Or your model
        #     contents=request.text,  # User's message from the request
        #     config=genai_types.GenerateContentConfig(
        #         system_instruction=prompts.initial_routing_prompt(),
        #         temperature=0.2,
        #         candidate_count=1,
        #         seed=42,
        #         tools=[
        #             find_metro_matrix,
        #             find_hq_relocation,
        #             find_company_relocation,
        #             invalid_request,
        #         ],
        #     ),
        # )

        response = genai_client.models.generate_content(
            model=global_gemini_model,
            contents=request.text,
            config=global_gemini_agent_config,
        )

        gemini_response = response.automatic_function_calling_history + [response.candidates[0].content]
 
        for content in gemini_response:
            logger.info(content)

        agent_response = gemini_response[-1].to_json_dict()["parts"][0]["text"]


        return JSONResponse(
            content={"text": agent_response, "session_id": request.session_id},
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error sending request: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))