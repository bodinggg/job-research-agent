"""Data models for job search."""
from typing import Optional
from pydantic import BaseModel, Field


class JobSummary(BaseModel):
    """Summary of a job listing."""

    source: str = Field(description="Source platform (e.g., boss, liepin)")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    salary: Optional[str] = Field(default=None, description="Salary range")
    address: Optional[str] = Field(default=None, description="Work location")
    tags: list[str] = Field(default_factory=list, description="Job tags")
    job_url: Optional[str] = Field(default=None, description="Job detail URL")


class SearchResult(BaseModel):
    """Result of a job search."""

    jobs: list[JobSummary] = Field(default_factory=list)
    total: int = Field(description="Total number of jobs found")
    query: str = Field(description="Search query")
