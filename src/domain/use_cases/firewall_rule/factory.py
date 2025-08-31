from sqlalchemy.orm import Session

from src.domain.services.filtering_policy.service import FilteringPolicyService
from src.domain.services.firewall_rule.service import FirewallRuleService
from src.domain.use_cases.firewall_rule.create_firewall_rule_use_case import (
    CreateFirewallRuleUseCase,
)
from src.domain.use_cases.firewall_rule.delete_firewall_rule_use_case import (
    DeleteFirewallRuleUseCase,
)
from src.domain.use_cases.firewall_rule.get_all_firewall_rules_use_case import (
    GetAllFirewallRulesUseCase,
)
from src.infrastructure.repositories.filtering_policy.sqlalchemy_filtering_policy_repository import (
    SQLAlchemyFilteringPolicyRepository,
)
from src.infrastructure.repositories.firewall_rule.sqlalchemy_firewall_rule_repository import (
    SQLAlchemyFirewallRuleRepository,
)
from src.infrastructure.web.schemas.firewall_rule.firewall_rule_schemas import (
    FirewallRuleUseCaseEnum,
)


def build_firewall_rule_use_case(
    use_case_string: FirewallRuleUseCaseEnum,
    session: Session,
) -> CreateFirewallRuleUseCase | GetAllFirewallRulesUseCase | DeleteFirewallRuleUseCase:
    use_case_mapper = {
        FirewallRuleUseCaseEnum.GET_ALL_FIREWALL_RULES: GetAllFirewallRulesUseCase,
        FirewallRuleUseCaseEnum.CREATE_FIREWALL_RULE: CreateFirewallRuleUseCase,
        FirewallRuleUseCaseEnum.DELETE_FIREWALL_RULE: DeleteFirewallRuleUseCase,
    }

    mapped_use_case = use_case_mapper.get(use_case_string)
    if not mapped_use_case:
        raise ValueError(f"Use case {use_case_string} not found")

    firewall_rule_repository = SQLAlchemyFirewallRuleRepository(session)
    firewall_rule_service = FirewallRuleService(firewall_rule_repository)
    if mapped_use_case in [GetAllFirewallRulesUseCase, DeleteFirewallRuleUseCase]:
        return mapped_use_case(firewall_rule_service)

    filtering_policy_repository = SQLAlchemyFilteringPolicyRepository(session)
    filtering_policy_service = FilteringPolicyService(filtering_policy_repository)
    return mapped_use_case(filtering_policy_service, firewall_rule_service)
