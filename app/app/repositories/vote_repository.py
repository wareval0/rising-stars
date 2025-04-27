from sqlalchemy.orm import Session
from typing import List, Optional
import os

from models.video import Video
from schemas.video_schema import VideoCreate, VideoUpdate


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

    def get_by_id(self, video_id: int) -> Optional[Video]:
        """Get a video by its ID"""
        return self.db.query(Video).filter(Video.id == video_id).first()

    def get_all(self) -> List[Video]:
        """Get all videos"""
        return self.db.query(Video).all()

    def update(self, video_id: int, video_data: VideoUpdate) -> Optional[Video]:
        """Update a video's metadata"""
        video = self.get_by_id(video_id, video_data.user_id)
        if video is None:
            return None

        update_data = video_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(video, key, value)

        self.db.commit()
        self.db.refresh(video)
        return video

    def delete(self, video_id: int, user_id: int) -> bool:
        """Delete a video"""
        video = self.get_by_id(video_id, user_id)
        if video is None:
            return False

        # Delete the physical file
        if os.path.exists(video.file_path):
            os.remove(video.file_path)

        # Delete the database entry
        self.db.delete(video)
        self.db.commit()
        return True
