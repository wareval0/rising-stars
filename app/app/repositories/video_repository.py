from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.exceptions.exceptions import InvalidVideoStatusError, VideoNotFoundError, VideoNotOwnedError
from app.interfaces.VideoStatus import VideoStatus
from app.models.video import Video
from app.schemas.video_schema import VideoCreate, VideoUpdate


class VideoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, video_data: dict) -> Video:
        """Create a new video entry in the database"""
        video = Video(**video_data)
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def get_by_id(self, video_id: int, user_id: int) -> Optional[Video]:
        """Get a video by its ID"""
        video = self.db.query(Video).filter(Video.video_id == video_id, Video.user_id == user_id).first()
        if video is None:
            raise VideoNotFoundError()
        if video.user_id != user_id:
            raise VideoNotOwnedError()
        return video

    def get_all(self) -> List[Video]:
        """Get all videos"""
        return self.db.query(Video).all()
    
    def get_all_public(self) -> List[Video]:
        """Get all public videos"""
        return self.db.query(Video).filter(Video.status == VideoStatus.PROCESADO).all()
    
    def get_all_by_user_id(self, user_id: int) -> List[Video]:
        return self.db.query(Video).filter(Video.user_id == user_id).all()

    def update(self, video_id: int,user_id:int, video_data: VideoUpdate) -> Optional[Video]:
        """Update a video's metadata"""
        video = self.get_by_id(video_id, user_id)
        if video is None:
            return None


        for key, value in video_data.items():
            setattr(video, key, value)

        self.db.commit()
        self.db.refresh(video)
        return video

    def delete(self, video_id: int, user_id:int) -> bool:
        """Delete a video"""
        video = self.get_by_id(video_id, user_id)
        if video is None:
            raise VideoNotFoundError()
        if video.user_id != user_id:
            raise VideoNotOwnedError()
        if video.status != VideoStatus.SUBIDO:
            raise InvalidVideoStatusError()
        # Delete the physical file
        if os.path.exists(video.original_url):
            os.remove(video.original_url)

        # Delete the database entry
        self.db.delete(video)
        self.db.commit()
        return "200"