import logging

from flask import Response, jsonify
from flask_openapi3 import APIBlueprint, Tag
from pydantic import ValidationError

from src.domain.use_cases.filtering_policy.factory import (
    build_filtering_policy_use_case,
)
from src.infrastructure.auth.middleware import (
    require_admin,
    require_admin_or_operator,
    require_auth,
)
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.web.schemas.common.openapi_schemas import (
    ErrorResponseSchema,
    FirewallIdPathSchema,
    FirewallPolicyPathSchema,
)
from src.infrastructure.web.schemas.filtering_policy.filtering_policy_schemas import (
    FilteringPolicyCreateSchema,
    FilteringPolicyResponseSchema,
    FilteringPolicyUseCaseEnum,
    PaginatedFilteringPolicyResponseSchema,
)
from src.infrastructure.web.utils.pagination import PaginationRequest
from src.infrastructure.web.utils.response import build_error_500_response


logger = logging.getLogger(__name__)

# Create blueprint with OpenAPI tags
tag = Tag(name="policies", description="Filtering policies management")
security = [{"bearerAuth": []}]

# Define the blueprint
policy_bp = APIBlueprint(
    "policies",
    __name__,
    url_prefix="/api/v1/firewalls",
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": {"description": "Unauthorized"}},
    doc_ui=True,
)


@policy_bp.post(
    "/<firewall_id>/policies",
    responses={
        201: FilteringPolicyResponseSchema,
        400: ErrorResponseSchema,
        403: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_admin_or_operator
def create_policy(path: FirewallIdPathSchema, body: FilteringPolicyCreateSchema):
    """Create a new filtering policy."""
    try:
        with get_db_session() as session:
            use_case = build_filtering_policy_use_case(
                FilteringPolicyUseCaseEnum.CREATE_FILTERING_POLICY, session
            )
            policy = use_case.execute(path.firewall_id, body)
            response = FilteringPolicyResponseSchema.model_validate(
                policy, from_attributes=True
            )
            return (
                jsonify(response.model_dump()),
                201,
            )

    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        logger.exception("Exception occurred during policy creation")
        return build_error_500_response()


@policy_bp.get(
    "/<firewall_id>/policies",
    responses={
        200: PaginatedFilteringPolicyResponseSchema,
        400: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_auth
def get_all_policies(path: FirewallIdPathSchema, query: PaginationRequest):
    """Get all filtering policies associated with a firewall with pagination."""
    try:
        with get_db_session() as session:
            use_case = build_filtering_policy_use_case(
                FilteringPolicyUseCaseEnum.GET_ALL_FILTERING_POLICIES, session
            )
            paginated_result = use_case.execute(path.firewall_id, query)

            items = [
                FilteringPolicyResponseSchema.model_validate(
                    policy, from_attributes=True
                )
                for policy in paginated_result.items
            ]

            page = PaginatedFilteringPolicyResponseSchema(
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
        logger.exception("Exception occurred during all policies retrieval")
        return build_error_500_response()


@policy_bp.delete(
    "/<firewall_id>/policies/<policy_id>",
    responses={
        204: None,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_admin
def delete_policy(path: FirewallPolicyPathSchema):
    """Delete a filtering policy associated with a firewall."""
    try:
        with get_db_session() as session:
            use_case = build_filtering_policy_use_case(
                FilteringPolicyUseCaseEnum.DELETE_FILTERING_POLICY, session
            )
            use_case.execute(firewall_id=path.firewall_id, policy_id=path.policy_id)
            return Response(status=204)

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        logger.exception("Exception occurred during policy deletion")
        return build_error_500_response()
