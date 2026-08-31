from pydantic import BaseModel


class StatusUpdate(BaseModel):

    new_status: str