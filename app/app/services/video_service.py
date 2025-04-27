from datetime import datetime
import os
import uuid
from typing import List, Optional

from celery import Celery
from fastapi import UploadFile

from app.interfaces.VideoStatus import VideoStatus
from app.repositories.video_repository import VideoRepository
from app.schemas.video_schema import VideoCreate, VideoReponseDetail, VideoUpdate, VideoResponse
from PIL import Image

# Arreglo para la constante deprecada
Image.ANTIALIAS = Image.LANCZOS

celery_app = Celery(
    "client",
    broker="redis://10.0.0.188:6379/0",
    backend="redis://10.0.0.188:6379/0"
)

class VideoService:
    def __init__(self, video_repository: VideoRepository):
        self.video_repository = video_repository
        self.NFS_MOUNT_PATH = "/mnt/nfs-data"
        self.LOGO_PATH = os.path.join(os.getcwd(), "app", "public", "logo.png")
        os.makedirs(self.NFS_MOUNT_PATH, exist_ok=True)

    async def save_video_file(self, file: UploadFile, title: str, user_id: int) -> dict:
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"input_{uuid.uuid4()}{file_extension}"

        relative_path = unique_filename
        absolute_path = os.path.join(self.NFS_MOUNT_PATH, relative_path)

        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)

        with open(absolute_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        video_dict = {
            "user_id": user_id,
            "title": title,
            "status": VideoStatus.SUBIDO,
            "uploaded_at": datetime.now(),
            "original_url": relative_path,
            "processed_url": None,
            "processed_at": None
        }

        video = self.video_repository.create(video_dict)

        task = celery_app.send_task(
            "example_task",  # Task name as registered in the worker
            args=[video.video_id, user_id]
        )

        return {
            "video_id": video.video_id,
            "file_path": relative_path,
        }

    def get_video(self, video_id: int, user_id: int) -> Optional[VideoReponseDetail]:
        video = self.video_repository.get_by_id(video_id, user_id)
        if video is None:
            return None
        return VideoReponseDetail.model_validate(video)

    def get_videos(self, user_id: int) -> List[VideoResponse]:
        videos = self.video_repository.get_all_by_user_id(user_id)
        return [VideoResponse.model_validate(video) for video in videos]
    
    def get_public_videos(self) -> List[VideoResponse]:
        videos = self.video_repository.get_all_public()
        return [VideoResponse.model_validate(video) for video in videos]

    def update_video(self, video_id: int, video_data: VideoUpdate) -> Optional[VideoResponse]:
        updated_video = self.video_repository.update(video_id, video_data)
        if updated_video is None:
            return None
        return VideoResponse.model_validate(updated_video)

    def delete_video(self, video_id: int, user_id: int) -> bool:
        return self.video_repository.delete(video_id, user_id)
