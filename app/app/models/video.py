from sqlalchemy import Enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base
from app.interfaces.VideoStatus import VideoStatus



class Video(Base):
    __tablename__ = "videos"
    video_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True)
    status = Column(Enum(VideoStatus), default=VideoStatus.SUBIDO, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime, nullable=True)
    original_url = Column(String, nullable=False)
    processed_url = Column(String, nullable=True)
    
    def __repr__(self):
        return f'id={self.video_id}, user_id={self.user_id}, title={self.title}, status={self.status}, uploaded_at={self.uploaded_at}, processed_at={self.processed_at}, original_url={self.original_url}, processed_url={self.processed_url}'