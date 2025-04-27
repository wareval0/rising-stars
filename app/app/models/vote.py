from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base

Base = declarative_base()

class Vote(Base):
    __tablename__ = "votos"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    root = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
