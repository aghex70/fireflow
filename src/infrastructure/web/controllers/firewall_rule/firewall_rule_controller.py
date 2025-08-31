import logging

from flask import Response, jsonify
from flask_openapi3 import APIBlueprint, Tag
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.domain.use_cases.firewall_rule.factory import build_firewall_rule_use_case
from src.infrastructure.auth.middleware import (
    require_admin_or_operator,
    require_auth,
)
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.web.controllers.firewall_rule.helpers import map_integrity_error
from src.infrastructure.web.schemas.common.openapi_schemas import (
    ErrorResponseSchema,
    FirewallPolicyPathSchema,
    FirewallPolicyRulePathSchema,
)
from src.infrastructure.web.schemas.firewall_rule.firewall_rule_schemas import (
    FirewallRuleCreateSchema,
    FirewallRuleResponseSchema,
    FirewallRuleUseCaseEnum,
    PaginatedFirewallRuleResponseSchema,
)
from src.infrastructure.web.utils.pagination import PaginationRequest
from src.infrastructure.web.utils.response import build_error_500_response


logger = logging.getLogger(__name__)

# Create blueprint with OpenAPI tags
rule_tag = Tag(name="rules", description="Firewall rules management")
security = [{"bearerAuth": []}]

rule_bp = APIBlueprint(
    "rules",
    __name__,
    url_prefix="/api/v1/firewalls",
    abp_tags=[rule_tag],
    abp_security=security,
    abp_responses={"401": {"description": "Unauthorized"}},
    doc_ui=True,
)


@rule_bp.post(
    "/<firewall_id>/policies/<policy_id>/rules",
    responses={
        201: FirewallRuleResponseSchema,
        400: ErrorResponseSchema,
        403: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_admin_or_operator
def create_rule(path: FirewallPolicyPathSchema, body: FirewallRuleCreateSchema):
    """Create a new firewall rule."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_rule_use_case(
                FirewallRuleUseCaseEnum.CREATE_FIREWALL_RULE, session
            )
            rule = use_case.execute(path.firewall_id, path.policy_id, body)
            response = FirewallRuleResponseSchema.model_validate(
                rule, from_attributes=True
            )
            return (
                jsonify(response.model_dump()),
                201,
            )

    except IntegrityError as e:
        logger.exception("Integrity error during rule creation")
        message, status_code = map_integrity_error(e)
        return jsonify({"error": "Integrity error", "details": message}), status_code
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        logger.exception("Exception occurred during rule creation")
        return build_error_500_response()


@rule_bp.get(
    "/<firewall_id>/policies/<policy_id>/rules",
    responses={
        200: {"description": "List of all firewall rules"},
        500: ErrorResponseSchema,
    },
)
@require_auth
def get_all_rules(path: FirewallPolicyPathSchema, query: PaginationRequest):
    """Get all firewall rules."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_rule_use_case(
                FirewallRuleUseCaseEnum.GET_ALL_FIREWALL_RULES, session
            )

            paginated_result = use_case.execute(path.firewall_id, path.policy_id, query)
            items = [
                FirewallRuleResponseSchema.model_validate(rule, from_attributes=True)
                for rule in paginated_result.items
            ]

            page = PaginatedFirewallRuleResponseSchema(
                page=paginated_result.page,
                size=paginated_result.size,
                total=paginated_result.total,
                total_pages=paginated_result.total_pages,
                has_next=paginated_result.has_next,
                has_previous=paginated_result.has_previous,
                items=items,
            )
            return jsonify(page.model_dump()), 200

    except Exception:
        logger.exception("Exception occurred during all rules retrieval")
        return build_error_500_response()


@rule_bp.delete(
    "/<firewall_id>/policies/<policy_id>/rules/<rule_id>",
    responses={
        204: None,
        404: ErrorResponseSchema,
        500: ErrorResponseSchema,
    },
)
@require_admin_or_operator
def delete_rule(path: FirewallPolicyRulePathSchema):
    """Delete a firewall rule."""
    try:
        with get_db_session() as session:
            use_case = build_firewall_rule_use_case(
                FirewallRuleUseCaseEnum.DELETE_FIREWALL_RULE, session
            )
            use_case.execute(
                firewall_id=path.firewall_id,
                policy_id=path.policy_id,
                rule_id=path.rule_id,
            )
            return Response(status=204)

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        logger.exception("Exception occurred during rule deletion")
        return build_error_500_response()
