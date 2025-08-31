from sqlalchemy.orm import Session

from src.domain.services.firewall.service import FirewallService
from src.domain.use_cases.firewall.create_firewall_use_case import CreateFirewallUseCase
from src.domain.use_cases.firewall.delete_firewall_use_case import DeleteFirewallUseCase
from src.domain.use_cases.firewall.get_all_firewalls_use_case import (
    GetAllFirewallsUseCase,
)
from src.domain.use_cases.firewall.get_firewall_use_case import GetFirewallUseCase
from src.infrastructure.repositories.firewall.sqlalchemy_firewall_repository import (
    SQLAlchemyFirewallRepository,
)
from src.infrastructure.web.schemas.firewall.firewall_schemas import FirewallUseCaseEnum


def build_firewall_use_case(
    use_case_string: FirewallUseCaseEnum,
    session: Session,
):
    use_case_mapper = {
        FirewallUseCaseEnum.GET_ALL_FIREWALLS: GetAllFirewallsUseCase,
        FirewallUseCaseEnum.GET_FIREWALL_BY_ID: GetFirewallUseCase,
        FirewallUseCaseEnum.CREATE_FIREWALL: CreateFirewallUseCase,
        FirewallUseCaseEnum.DELETE_FIREWALL: DeleteFirewallUseCase,
    }

    mapped_use_case = use_case_mapper.get(use_case_string)
    if not mapped_use_case:
        raise ValueError(f"Use case {use_case_string} not found")

    firewall_repository = SQLAlchemyFirewallRepository(session)
    firewall_service = FirewallService(firewall_repository)
    return mapped_use_case(firewall_service)
