from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.interfaces.VideoStatus import VideoStatus


class VideoBase(BaseModel):
    title: str
    status: Optional[VideoStatus] = VideoStatus.SUBIDO

class VideoProcessing(BaseModel):
    message: str
    task_id: str


class VideoCreate(BaseModel):
    title: str
    status: Optional[VideoStatus] = VideoStatus.SUBIDO


class VideoResponse(VideoBase):
    video_id: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    processed_url: Optional[str] = None

    model_config = {"from_attributes": True}

class VideoReponseDetail(VideoBase):
    video_id: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    original_url: str
    processed_url: Optional[str] = None
    votes: int = 0

    model_config = {"from_attributes": True}
    
class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    
class VideoDelete(BaseModel):
    message: str
    video_id: int
