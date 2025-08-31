import logging

from flask import Response, jsonify
from flask_openapi3 import APIBlueprint, Info, OpenAPI, Tag
from pydantic import BaseModel, Field, ValidationError

from src.domain.use_cases.firewall.factory import build_firewall_use_case
from src.infrastructure.auth.middleware import (
    require_admin,
    require_admin_or_operator,
    require_auth,
)
from src.infrastructure.celery.tasks.notification_tasks import (
    send_webhook_notification_task,
)
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.web.schemas.common.openapi_schemas import (
    ErrorResponseSchema,
    FirewallIdPathSchema,
)
from src.infrastructure.web.schemas.firewall.firewall_schemas import (
    FirewallCreateSchema,
    FirewallResponseSchema,
    FirewallUseCaseEnum,
    PaginatedFirewallResponseSchema,
)
from src.infrastructure.web.utils.pagination import PaginationRequest
from src.infrastructure.web.utils.response import build_error_500_response


logger = logging.getLogger(__name__)

info = Info(title="FireFlow API", version="1.0.0")

jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
security_schemes = {"jwt": jwt}

# Create the OpenAPI app with Swagger UI enabled
app = OpenAPI(
    __name__,
    info=info,
    security_schemes=security_schemes,
    doc_ui=True,
)

tag = Tag(name="firewalls", description="Firewalls endpoints")
security = [{"bearerAuth": []}]


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")


# Define the blueprint
firewall_bp = APIBlueprint(
    "firewalls",
    __name__,
    url_prefix="/api/v1/firewalls",
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
    doc_ui=True,
)


@firewall_bp.post(
    "",
    responses={
        201: FirewallResponseSchema,
        400: ErrorResponseSchema,
        403: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_admin_or_operator
def create_firewall(body: FirewallCreateSchema):
    """Create a new firewall."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_use_case(
                FirewallUseCaseEnum.CREATE_FIREWALL, session
            )
            firewall = use_case.execute(body)
            response = FirewallResponseSchema.model_validate(
                firewall, from_attributes=True
            )

            # Send webhook notification asynchronously
            send_webhook_notification_task.delay(
                webhook_url="http://localhost:8080/webhooks/firewall",
                payload={
                    "event": "firewall_created",
                    "firewall": response.model_dump(),
                },
                event_type="firewall_created",
            )

            return (
                jsonify(response.model_dump()),
                201,
            )

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        logger.exception("Exception occurred during firewall creation")
        return build_error_500_response()


@firewall_bp.get(
    "/<firewall_id>",
    responses={
        200: FirewallResponseSchema,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_auth
def get_firewall(path: FirewallIdPathSchema):
    """Get a firewall by ID."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_use_case(
                FirewallUseCaseEnum.GET_FIREWALL_BY_ID, session
            )
            firewall = use_case.execute(path.firewall_id)
            response = FirewallResponseSchema.model_validate(
                firewall, from_attributes=True
            )
            return jsonify(response.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        logger.exception("Exception occurred during firewall retrieval")
        return build_error_500_response()


@firewall_bp.get(
    "",
    responses={
        200: PaginatedFirewallResponseSchema,
        400: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_auth
def get_all_firewalls(query: PaginationRequest):
    """Get all firewalls with pagination."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_use_case(
                FirewallUseCaseEnum.GET_ALL_FIREWALLS, session
            )
            paginated_result = use_case.execute(
                query,
            )

            items = [
                FirewallResponseSchema.model_validate(fw, from_attributes=True)
                for fw in paginated_result.items
            ]

            page = PaginatedFirewallResponseSchema(
                page=paginated_result.page,
                size=paginated_result.size,
                total=paginated_result.total,
                total_pages=paginated_result.total_pages,
                has_next=paginated_result.has_next,
                has_previous=paginated_result.has_previous,
                items=items,
            )

            return jsonify(page.model_dump()), 200

    except ValidationError as e:
        return jsonify(
            {"error": "Invalid pagination or filter parameters", "details": e.errors()}
        ), 400
    except Exception:
        logger.exception("Exception occurred during all firewalls retrieval")
        return build_error_500_response()


@firewall_bp.delete(
    "/<firewall_id>",
    responses={
        204: None,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_admin
def delete_firewall(path: FirewallIdPathSchema):
    """Delete a firewall."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_use_case(
                FirewallUseCaseEnum.DELETE_FIREWALL, session
            )
            use_case.execute(path.firewall_id)
            return Response(status=204)

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        logger.exception("Exception occurred during firewall deletion")
        return build_error_500_response()
