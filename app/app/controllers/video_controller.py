import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST
from app.core.auth import get_current_user
from app.exceptions.exceptions import InvalidVideoStatusError, VideoNotFoundError, VideoNotOwnedError
from app.models.user import User
from app.schemas.video_schema import VideoCreate, VideoReponseDetail, VideoUpdate, VideoResponse, VideoProcessing, VideoDelete
from app.services.video_service import VideoService
from app.repositories.video_repository import VideoRepository
from app.dependencies import get_db

router = APIRouter(prefix="/api", tags=["videos"])


def get_video_service(db: Session = Depends(get_db)) -> VideoService:
    video_repository = VideoRepository(db)
    return VideoService(video_repository)


@router.post("/videos/upload", response_model=VideoProcessing, status_code=status.HTTP_201_CREATED)
async def upload_video(
    title: str = Form(...),
    video_file: UploadFile = File(...),
    video_service: VideoService = Depends(get_video_service),
    current_user: User = Depends(get_current_user)
):
    if not video_file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Archivo inválido (tipo no soportado)")
    if video_file.size and video_file.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Archivo excede los 100MB")

    saved = await video_service.save_video_file(video_file, title, current_user.id)

    return VideoProcessing(
        message="Video subido correctamente. Procesamiento en curso.",
        task_id=str(saved["video_id"])
    )
    
@router.get("/videos/", response_model=List[VideoResponse])
def get_all_videos(
        video_service: VideoService = Depends(get_video_service),
        current_user: User = Depends(get_current_user)
):
    """
    Get all videos uploaded by the current user
    """
    return video_service.get_videos(current_user.id)

@router.get("/videos/{video_id}", response_model=VideoReponseDetail)
def get_video(
        video_id: int,
        video_service: VideoService = Depends(get_video_service),
        current_user: User = Depends(get_current_user)
):
    """
    Get a video's metadata by ID for the current user
    """
    try:
        video = video_service.get_video(video_id, current_user.id)
        return video
    except VideoNotFoundError:
        return Response("Video not found", status_code=HTTP_404_NOT_FOUND)
    except VideoNotOwnedError:
        return Response("forbidden", status_code=HTTP_403_FORBIDDEN)



@router.get("/public/videos/", response_model=List[VideoResponse])
def get_all_public_videos(
        video_service: VideoService = Depends(get_video_service)
):
    """
    Get all videos uploaded by the current user
    """
    return video_service.get_public_videos()

@router.get("/videos/download/{video_id}")
def download_video(
        video_id: int,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Download a video file by ID
    """
    video = video_service.get_video(video_id)
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )

    if not os.path.exists(video.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found on server"
        )

    return FileResponse(
        path=video.file_path,
        filename=video.filename,
        media_type=video.content_type
    )




@router.put("/videos/{video_id}", response_model=VideoResponse)
def update_video(
        video_id: int,
        video_data: VideoUpdate,
        video_service: VideoService = Depends(get_video_service)
):
    """
    Update a video's metadata
    """
    updated_video = video_service.update_video(video_id, video_data)
    if updated_video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return updated_video


@router.delete("/videos/{video_id}", response_model=VideoDelete, status_code=status.HTTP_200_OK)
def delete_video(
        video_id: int,
        video_service: VideoService = Depends(get_video_service),
        current_user: User = Depends(get_current_user)
):
    """
    Delete a video
    """
    try:
        video_service.delete_video(video_id, current_user.id)
        response = VideoDelete(
            message="El video ha sido eliminado exitosamente.",
            video_id=video_id
        )
        return response
    except VideoNotFoundError:
        return Response("Video not found", status_code=HTTP_404_NOT_FOUND)
    except VideoNotOwnedError:
        return Response("forbidden", status_code=HTTP_403_FORBIDDEN)
    except InvalidVideoStatusError:
        return Response("invalid status", status_code=HTTP_400_BAD_REQUEST)
