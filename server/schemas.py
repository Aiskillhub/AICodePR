from typing import Literal

from pydantic import BaseModel, field_validator


class Finding(BaseModel):
    file_path: str
    line_number: int
    severity: Literal["critical", "high", "medium", "low"]
    title: str
    description: str
    suggestion: str = ""

    @field_validator("line_number")
    @classmethod
    def line_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("line_number must be >= 1")
        return v


class ReviewResult(BaseModel):
    summary: str
    findings: list[Finding] = []
