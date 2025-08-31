"""Polyfactory factories for firewall-related entities."""

from polyfactory.factories import DataclassFactory

from src.domain.entities.firewall.firewall import Firewall, FirewallEnvironmentEnum


class FirewallFactory(DataclassFactory[Firewall]):
    """Factory for creating Firewall instances."""

    __model__ = Firewall
    __check_model__ = False  

    @classmethod
    def production_firewall(cls) -> Firewall:
        """Create a production firewall."""
        return cls.build(environment=FirewallEnvironmentEnum.PRODUCTION)

    @classmethod
    def staging_firewall(cls) -> Firewall:
        """Create a staging firewall."""
        return cls.build(environment=FirewallEnvironmentEnum.STAGING)

    @classmethod
    def development_firewall(cls) -> Firewall:
        """Create a development firewall."""
        return cls.build(environment=FirewallEnvironmentEnum.DEVELOPMENT)
