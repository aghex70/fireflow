"""Tests for User repository."""

import pytest
from sqlalchemy.exc import IntegrityError

from src.domain.entities.auth.user import User, UserRole, UserStatus
from src.infrastructure.database.models import SQLUser
from src.infrastructure.repositories.auth.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from tests.factories.user_factories import UserFactory


class TestSQLAlchemyUserRepository:
    """Test cases for SQLAlchemy User repository."""

    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        # Arrange
        user = UserFactory.build()
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        created_user = repository.create(user)

        # Assert
        assert created_user.id is not None
        assert created_user.username == user.username
        assert created_user.email == user.email
        assert created_user.role == user.role
        assert created_user.status == user.status

        # Verify in database
        db_user = db_session.query(SQLUser).filter_by(id=created_user.id).first()
        assert db_user is not None
        assert db_user.username == user.username

    def test_create_user_duplicate_username_raises_error(self, db_session):
        """Test creation with duplicate username raises error."""
        # Arrange
        user1 = UserFactory.build()
        user2 = UserFactory.build(username=user1.username)
        repository = SQLAlchemyUserRepository(db_session)

        # Create first user
        repository.create(user1)
        db_session.commit()

        # Act & Assert
        with pytest.raises(ValueError, match=f"Username '{user1.username}' already exists"):
            repository.create(user2)
            db_session.commit()

    def test_create_user_duplicate_email_raises_error(self, db_session):
        """Test creation with duplicate email raises error."""
        # Arrange
        user1 = UserFactory.build()
        # Ensure user2 has same email but different username
        user2 = UserFactory.build(email=user1.email, username=user1.username + "_different")
        repository = SQLAlchemyUserRepository(db_session)

        # Create first user
        repository.create(user1)
        db_session.commit()

        # Act & Assert
        with pytest.raises(ValueError, match=f"Email '{user1.email}' already exists"):
            repository.create(user2)
            db_session.commit()

    def test_get_by_id_existing_user(self, db_session):
        """Test getting user by existing ID."""
        # Arrange
        user = UserFactory.build()
        repository = SQLAlchemyUserRepository(db_session)
        created_user = repository.create(user)
        db_session.commit()

        # Act
        found_user = repository.get_by_id(created_user.id)

        # Assert
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == user.username
        assert found_user.email == user.email

    def test_get_by_id_nonexistent_user_returns_none(self, db_session):
        """Test getting user by non-existent ID returns None."""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        found_user = repository.get_by_id(99999)

        # Assert
        assert found_user is None

    def test_get_by_username_existing_user(self, db_session):
        """Test getting user by existing username."""
        # Arrange
        user = UserFactory.build()
        repository = SQLAlchemyUserRepository(db_session)
        repository.create(user)
        db_session.commit()

        # Act
        found_user = repository.get_by_username(user.username)

        # Assert
        assert found_user is not None
        assert found_user.username == user.username
        assert found_user.email == user.email

    def test_get_by_username_nonexistent_user_returns_none(self, db_session):
        """Test getting user by non-existent username returns None."""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        found_user = repository.get_by_username("nonexistent")

        # Assert
        assert found_user is None

    def test_get_by_email_existing_user(self, db_session):
        """Test getting user by existing email."""
        # Arrange
        user = UserFactory.build()
        repository = SQLAlchemyUserRepository(db_session)
        repository.create(user)
        db_session.commit()

        # Act
        found_user = repository.get_by_email(user.email)

        # Assert
        assert found_user is not None
        assert found_user.username == user.username
        assert found_user.email == user.email

    def test_get_by_email_nonexistent_user_returns_none(self, db_session):
        """Test getting user by non-existent email returns None."""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        found_user = repository.get_by_email("nonexistent@example.com")

        # Assert
        assert found_user is None

    def test_get_all_users_empty(self, db_session):
        """Test getting all users when none exist."""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        users = repository.get_all()

        # Assert
        assert users == []

    def test_get_all_users_multiple(self, db_session):
        """Test getting all users when multiple exist."""
        # Arrange
        users = UserFactory.batch(3)
        repository = SQLAlchemyUserRepository(db_session)
        
        for user in users:
            repository.create(user)
        db_session.commit()

        # Act
        all_users = repository.get_all()

        # Assert
        assert len(all_users) == 3
        usernames = [user.username for user in all_users]
        for user in users:
            assert user.username in usernames

    def test_delete_existing_user_success(self, db_session):
        """Test successful deletion of existing user."""
        # Arrange
        user = UserFactory.build()
        repository = SQLAlchemyUserRepository(db_session)
        created_user = repository.create(user)
        db_session.commit()

        # Act
        result = repository.delete(created_user.id)

        # Assert
        assert result is True
        
        # Verify user is deleted from database
        db_user = db_session.query(SQLUser).filter_by(id=created_user.id).first()
        assert db_user is None

    def test_delete_nonexistent_user_returns_false(self, db_session):
        """Test deletion of non-existent user returns False."""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        result = repository.delete(99999)

        # Assert
        assert result is False

    def test_get_by_role_admin_users(self, db_session):
        """Test getting users by admin role."""
        # Arrange
        admin_users = UserFactory.batch(2, role=UserRole.ADMIN)
        viewer_user = UserFactory.build(role=UserRole.VIEWER)
        repository = SQLAlchemyUserRepository(db_session)

        for user in admin_users + [viewer_user]:
            repository.create(user)
        db_session.commit()

        # Act
        admin_found = repository.get_by_role(UserRole.ADMIN.value)

        # Assert
        assert len(admin_found) == 2
        for user in admin_found:
            assert user.role == UserRole.ADMIN

    def test_get_by_role_no_users_returns_empty_list(self, db_session):
        """Test getting users by role when none exist."""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        users = repository.get_by_role(UserRole.ADMIN.value)

        # Assert
        assert users == []

    def test_to_entity_conversion(self, db_session):
        """Test conversion from database model to domain entity."""
        # Arrange
        user = UserFactory.build()
        repository = SQLAlchemyUserRepository(db_session)
        
        # Create user to get database model
        created_user = repository.create(user)
        db_session.commit()
        
        db_user = db_session.query(SQLUser).filter_by(id=created_user.id).first()

        # Act
        entity = repository._to_entity(db_user)

        # Assert
        assert isinstance(entity, User)
        assert entity.id == db_user.id
        assert entity.username == db_user.username
        assert entity.email == db_user.email
        assert entity.role == UserRole(db_user.role)
        assert entity.status == UserStatus(db_user.status)

    @pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER])
    def test_create_user_with_different_roles(self, db_session, role):
        """Test creating users with different roles."""
        # Arrange
        user = UserFactory.build(role=role)
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        created_user = repository.create(user)

        # Assert
        assert created_user.role == role
        
        # Verify in database
        db_user = db_session.query(SQLUser).filter_by(id=created_user.id).first()
        assert db_user.role == role.value

    @pytest.mark.parametrize("status", [UserStatus.ACTIVE, UserStatus.INACTIVE])
    def test_create_user_with_different_statuses(self, db_session, status):
        """Test creating users with different statuses."""
        # Arrange
        user = UserFactory.build(status=status)
        repository = SQLAlchemyUserRepository(db_session)

        # Act
        created_user = repository.create(user)

        # Assert
        assert created_user.status == status
        
        # Verify in database
        db_user = db_session.query(SQLUser).filter_by(id=created_user.id).first()
        assert db_user.status == status.value