from sqlalchemy.orm import Session

from src.domain.services.auth.service import UserService
from src.domain.use_cases.auth.get_current_user_use_case import GetCurrentUserUseCase
from src.domain.use_cases.auth.login_use_case import LoginUseCase
from src.domain.use_cases.auth.refresh_token_use_case import RefreshTokenUseCase
from src.domain.use_cases.auth.register_user_use_case import RegisterUserUseCase
from src.infrastructure.auth.jwt_service import JWTService
from src.infrastructure.repositories.auth.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.infrastructure.web.schemas.auth.auth_schemas import AuthUseCaseEnum


def build_auth_use_case(
    use_case_string: AuthUseCaseEnum,
    session: Session,
):
    use_case_mapper = {
        AuthUseCaseEnum.GET_CURRENT_USER: GetCurrentUserUseCase,
        AuthUseCaseEnum.LOGIN: LoginUseCase,
        AuthUseCaseEnum.REFRESH_TOKEN: RefreshTokenUseCase,
        AuthUseCaseEnum.REGISTER_USER: RegisterUserUseCase,
    }

    mapped_use_case = use_case_mapper.get(use_case_string)
    if not mapped_use_case:
        raise ValueError(f"Use case {use_case_string} not found")

    user_repository = SQLAlchemyUserRepository(session)
    user_service = UserService(user_repository)

    if mapped_use_case in [RegisterUserUseCase, GetCurrentUserUseCase]:
        return mapped_use_case(user_service)

    jwt_service = JWTService()
    if mapped_use_case == RefreshTokenUseCase:
        return mapped_use_case(user_service, jwt_service)
    return mapped_use_case(user_service, jwt_service)
