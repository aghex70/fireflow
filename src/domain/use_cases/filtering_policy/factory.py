from sqlalchemy.orm import Session

from src.domain.services.filtering_policy.service import FilteringPolicyService
from src.domain.services.firewall.service import FirewallService
from src.domain.use_cases.filtering_policy.create_filtering_policy_use_case import (
    CreateFilteringPolicyUseCase,
)
from src.domain.use_cases.filtering_policy.delete_filtering_policy_use_case import (
    DeleteFilteringPolicyUseCase,
)
from src.domain.use_cases.filtering_policy.get_all_filtering_policies_use_case import (
    GetAllFilteringPoliciesUseCase,
)
from src.infrastructure.repositories.filtering_policy.sqlalchemy_filtering_policy_repository import (
    SQLAlchemyFilteringPolicyRepository,
)
from src.infrastructure.repositories.firewall.sqlalchemy_firewall_repository import (
    SQLAlchemyFirewallRepository,
)
from src.infrastructure.web.schemas.filtering_policy.filtering_policy_schemas import (
    FilteringPolicyUseCaseEnum,
)


def build_filtering_policy_use_case(
    use_case_string: FilteringPolicyUseCaseEnum,
    session: Session,
):
    use_case_mapper = {
        FilteringPolicyUseCaseEnum.CREATE_FILTERING_POLICY: CreateFilteringPolicyUseCase,
        FilteringPolicyUseCaseEnum.DELETE_FILTERING_POLICY: DeleteFilteringPolicyUseCase,
        FilteringPolicyUseCaseEnum.GET_ALL_FILTERING_POLICIES: GetAllFilteringPoliciesUseCase,
    }

    mapped_use_case = use_case_mapper.get(use_case_string)
    if not mapped_use_case:
        raise ValueError(f"Use case {use_case_string} not found")

    filtering_policy_repository = SQLAlchemyFilteringPolicyRepository(session)
    filtering_policy_service = FilteringPolicyService(filtering_policy_repository)

    if mapped_use_case == DeleteFilteringPolicyUseCase:
        return mapped_use_case(filtering_policy_service)

    firewall_repository = SQLAlchemyFirewallRepository(session)
    firewall_service = FirewallService(firewall_repository)
    return mapped_use_case(filtering_policy_service, firewall_service)
