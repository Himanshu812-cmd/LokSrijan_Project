from pydantic import BaseModel, Field


class ValidationAction(BaseModel):
    decision: str
    comment: str = Field(min_length=5)