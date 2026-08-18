"""Pydantic request/response schemas for the public API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.models import JobStatus


class JobCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    status: JobStatus
    created_at: datetime


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    error_message: str | None

    @computed_field
    @property
    def report_ready(self) -> bool:
        return self.status == JobStatus.COMPLETE
