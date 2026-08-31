from pydantic import BaseModel, Field
class ChallengeCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    category: str
    location: str
    severity: str = "MEDIUM"
class ChallengeUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=200
    )
    description: str | None = Field(
        default=None,
        min_length=10
    )
    category: str | None = None
    location: str | None = None
    severity: str | None = None
class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    location: str
    severity: str
    status: str
    created_by: int
class ChallengeStatusUpdate(BaseModel):
    new_status: str