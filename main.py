import logging
import datetime as dt
from flask import jsonify, Response, Request
import functions_framework
from typing import Any, Dict, List, Tuple, Union
from src.errors.verification_error import VerificationError

from src.services.user_services import AdminUserService
from src.services.campaign_service import CampaignService
from src.utils.get_secret_payload import get_secret_payload
from src.utils.token_extractor import extract_token_from_header
from src.utils.get_env_vars import get_env_vars
from supacrud import Supabase, ResponseType

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get environment variables once and reuse
env_vars = get_env_vars()

# Create a CampaignService instance once and reuse
campaign_service = CampaignService(env_vars)

# get the service key
service_key = get_secret_payload(
    project_id=env_vars["PROJECT_ID"],
    secret_id=env_vars["SUPABASE_SERVICE_ROLE_SECRET_ID"],
    version_id=env_vars["VERSION_ID"],
)
if not service_key:
    raise Exception("Service key not found")

# Create an AdminUserService instance once and reuse
admin_user_service = AdminUserService(
    base_url=env_vars["SUPABASE_URL"],
    anon_key=env_vars["SUPABASE_ANON_KEY"],
    service_key=service_key,
)

supabase_client = Supabase(
    base_url=env_vars["SUPABASE_URL"],
    anon_key=env_vars["SUPABASE_ANON_KEY"],
    service_role_key=service_key,
)


def verify_request(request: Request) -> Tuple[str, str, Dict[str, Any]]:
    """
    Validate the request and extract queue name, action type, and payload.

    Parameters:
    request (request): The incoming request from the client.

    Returns:
    Tuple[str, str, Dict[str, Any]]: Returns a tuple containing the queue
        name, action type, and payload if the request is valid.

    Raises:
    VerificationError: If the request is invalid.
    """
    data = request.get_json()
    if not data:
        raise VerificationError("Invalid request body")

    jwt_token = extract_token_from_header(request.headers)
    if not jwt_token:
        raise VerificationError("No token provided")

    # verify user token
    token_verification = admin_user_service.verify_user(jwt_token)
    if "error" in token_verification:
        raise VerificationError(token_verification["error"])

    queue_name = data.get("queue_name")
    action_type = data.get("action_type")
    payload = data.get("payload")
    logger.info("Received request with payload: %s", payload)
    if not all([queue_name, action_type, payload]):
        raise VerificationError(
            "Missing queue_name, action_type, or payload in request data"
        )

    if action_type not in ["create_campaign", "edit_campaign", "delete_campaign"]:
        raise VerificationError("Invalid action_type provided in payload")

    return queue_name, action_type, payload


@functions_framework.http
def main(request: Request) -> Union[Response, Tuple[Response, int]]:
    """
    The main entry point for the cloud function. Handles the incoming
    request, verifies it, and dispatches it to the correct function
    based on the action type in the payload. Additionally, this function
    handles CORS headers for both preflight and main requests.

    Parameters:
    request (request): The incoming request from the client.

    Returns:
    Union[Response, Tuple[Response, int]]: The response to be returned to the client.
    """
    
    # Set default CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
    
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        return ("", 204, headers)

    # Handle main requests
    try:
        queue_name, action_type, payload = verify_request(request)
        response_action = campaign_service.action_dispatcher(
            action_type=action_type,
        )
        response_data = response_action(
            supabase=supabase_client,
            payload=payload,
        )
        return (jsonify(response_data), 200, headers)

    except VerificationError as error:
        logger.error("Error processing request: %s", error.message)
        return (jsonify({"message": error.message}), 400, headers)
    except Exception as error:
        logger.error("Error processing request: %s", error)
        return (jsonify({"message": "Internal server error"}), 500, headers)
