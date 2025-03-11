#  Copyright 2025 Google LLC. This software is provided as-is, without warranty
#  or representation for any use or purpose. Your use of it is subject to your
#  agreement with Google.
"""Functions when an invalid request is made."""

def invalid_request(
    user_request: str,
) -> str:
    """Respond to customer and help clarify thier question.

    Args:
        user_request (str): The request from the user.

    Returns:
        str: The response to the user
    """
    return """I am only able to generate Metro Matrix, HQ Relocation, and
    Company Relocation reports at the moment. Can I help you create one of those?"""