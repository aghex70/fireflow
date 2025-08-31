"""Delete filtering policy use case."""

from src.domain.services.filtering_policy.service import FilteringPolicyService


class DeleteFilteringPolicyUseCase:
    """Use case for deleting a filtering policy."""

    def __init__(self, filtering_policy_service: FilteringPolicyService):
        self.filtering_policy_service = filtering_policy_service

    def execute(self, firewall_id: int, policy_id: int) -> bool:
        """Execute the delete filtering policy use case."""

        # Check if policy attached to firewall exists
        policy = self.filtering_policy_service.get_filtering_policy_by_id(policy_id, firewall_id)
        if not policy:
            raise ValueError(
                f"Filtering policy with firewall id {firewall_id} and policy id {policy_id} not found"
            )

        return self.filtering_policy_service.delete_filtering_policy(policy_id)
