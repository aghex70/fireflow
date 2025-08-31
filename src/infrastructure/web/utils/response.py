from flask import Response, jsonify
from werkzeug.http import HTTP_STATUS_CODES


INTERNAL_SERVER_ERROR_STATUS_CODE = 500
INTERNAL_SERVER_ERROR_MESSAGE = "An unexpected error occurred"


def build_error_500_response() -> tuple[Response, int]:
    return jsonify(
        {
            "error": HTTP_STATUS_CODES[INTERNAL_SERVER_ERROR_STATUS_CODE],
            "message": INTERNAL_SERVER_ERROR_MESSAGE,
        }
    ), INTERNAL_SERVER_ERROR_STATUS_CODE
