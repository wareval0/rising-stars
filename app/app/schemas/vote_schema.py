from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VoteBase(BaseModel):
    video_id: int
    user_id: int
    root: bool


class VoteCreate(VoteBase):
    pass


class VotoUpdate(BaseModel):
    root: Optional[bool] = None


class VoteResponse(VoteBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
