"""Polyfactory factories for filtering policy entities."""

from polyfactory.factories import DataclassFactory

from src.domain.entities.filtering_policy.filtering_policy import (
    FilteringPolicy,
    PolicyActionEnum,
)


class FilteringPolicyFactory(DataclassFactory[FilteringPolicy]):
    """Factory for creating FilteringPolicy instances."""

    __model__ = FilteringPolicy
    __check_model__ = False  

    @classmethod
    def allow_policy(cls, firewall_id: int | None = None) -> FilteringPolicy:
        """Create an allow filtering policy."""
        kwargs = {"action": PolicyActionEnum.ALLOW}
        if firewall_id is not None:
            kwargs["firewall_id"] = firewall_id
        return cls.build(**kwargs)

    @classmethod
    def deny_policy(cls, firewall_id: int | None = None) -> FilteringPolicy:
        """Create a deny filtering policy."""
        kwargs = {"action": PolicyActionEnum.DENY}
        if firewall_id is not None:
            kwargs["firewall_id"] = firewall_id
        return cls.build(**kwargs)

    @classmethod
    def log_policy(cls, firewall_id: int | None = None) -> FilteringPolicy:
        """Create a log filtering policy."""
        kwargs = {"action": PolicyActionEnum.LOG}
        if firewall_id is not None:
            kwargs["firewall_id"] = firewall_id
        return cls.build(**kwargs)

    @classmethod
    def high_priority_policy(cls, firewall_id: int | None = None) -> FilteringPolicy:
        """Create a high priority filtering policy."""
        import random
        kwargs = {"priority": random.randint(900, 1000)}
        if firewall_id is not None:
            kwargs["firewall_id"] = firewall_id
        return cls.build(**kwargs)

    @classmethod
    def low_priority_policy(cls, firewall_id: int | None = None) -> FilteringPolicy:
        """Create a low priority filtering policy."""
        import random
        kwargs = {"priority": random.randint(1, 100)}
        if firewall_id is not None:
            kwargs["firewall_id"] = firewall_id
        return cls.build(**kwargs)
