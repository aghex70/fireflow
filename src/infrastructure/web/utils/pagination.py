"""Pagination utilities for Flask APIs."""

from dataclasses import dataclass
from typing import Any, TypeVar

from flask import request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Query


T = TypeVar("T")


class PaginationRequest(BaseModel):
    """Pagination request parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page ")
    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_dir: str = Field(default="asc", description="Sort direction")

    @field_validator("sort_dir")
    @classmethod
    def validate_sort_dir(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_dir must be 'asc' or 'desc'")
        return v

    @classmethod
    def from_request(cls, default_sort_by: str = "id") -> "PaginationRequest":
        """Create pagination request from Flask request args."""
        return cls(
            page=int(request.args.get("page", 1)),
            size=int(request.args.get("size", 20)),
            sort_by=request.args.get("sort_by", default_sort_by),
            sort_dir=request.args.get("sort_dir", "asc").lower(),
        )


@dataclass
class PaginationResponse:
    """Pagination response metadata."""

    page: int
    size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
    items: list[Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "page": self.page,
            "size": self.size,
            "total": self.total,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_previous": self.has_previous,
            "items": self.items,
        }


def paginate_query(
    query: Query,
    pagination: PaginationRequest,
    sort_columns: dict[str, Any] | None = None,
) -> PaginationResponse:
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query to paginate
        pagination: Pagination parameters
        sort_columns: Dict mapping sort field names to SQLAlchemy columns

    Returns:
        PaginationResponse with paginated results
    """
    # Apply sorting if specified
    if pagination.sort_by and sort_columns:
        sort_column = sort_columns.get(pagination.sort_by)
        if sort_column is not None:
            if pagination.sort_dir == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

    # Get total count before applying pagination
    total = query.count()

    # Calculate pagination metadata
    total_pages = (total + pagination.size - 1) // pagination.size
    has_next = pagination.page < total_pages
    has_previous = pagination.page > 1

    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    items = query.offset(offset).limit(pagination.size).all()

    return PaginationResponse(
        page=pagination.page,
        size=pagination.size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
        items=items,
    )


class PaginatedResponseSchema(BaseModel):
    """Base schema for paginated responses."""

    page: int = Field(description="Current page number")
    size: int = Field(description="Items per page")
    total: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")
    items: list[Any] = Field(description="Items for current page")
    model_config = ConfigDict(from_attributes=True)
