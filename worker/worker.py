from datetime import datetime
from celery import Celery
import os
import logging
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

from core.database import SessionLocal, engine
from models.video import Video
from models.user import User
from interfaces.VideoStatus import VideoStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

# Celery configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery.task(name="example_task")
def update_video_status(video_id: int, user_id: int):
    """
    Task to update video status in database
    """
    try:
        db = SessionLocal()
        video = db.query(Video).filter(Video.video_id == video_id, Video.user_id == user_id).first()

        if not video:
            raise ValueError(f"Video with id {video_id} for user {user_id} not found")

        # Normalizar la ruta y manejar el almacenamiento NFS
        relative_input_path = video.original_url.replace("\\", "/")

        # Para archivos en el volumen NFS
        if relative_input_path.startswith("nfs-storage"):
            # Ruta donde está montado el NFS en el worker
            input_path = relative_input_path.replace("nfs-storage", "/mnt/nfs-data")
        else:
            # Fallback a la ruta local por si hay archivos viejos
            input_path = os.path.join(relative_input_path)
            input_path = f"/{input_path}"

        # Generar la ruta de salida, manteniendo la estructura de directorios
        relative_output_path = relative_input_path.replace("input_", "output_")

        if relative_input_path.startswith("nfs-storage"):
            output_path = relative_output_path.replace("nfs-storage", "/mnt/nfs-data")
        else:
            output_path = os.path.join(relative_output_path)
            output_path = f"/{output_path}"


        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"Processing video: {input_path} -> {output_path}")

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")


        logo_path = os.path.join(os.getcwd(), "public", "logo.png")
        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo not found: {logo_path}")


        logger.info("Opening original video file")
        original_video = VideoFileClip(input_path)
        duration = original_video.duration
        trimmed_duration = min(28, duration)

        logger.info("Trimming and removing audio")
        video_clip = original_video.subclip(0, trimmed_duration).without_audio()
        width, height = video_clip.size
        target_aspect = 16 / 9
        current_aspect = width / height

        logger.info("Adjusting aspect ratio")
        if current_aspect > target_aspect:
            new_height = int(width / target_aspect)
            video_clip = video_clip.resize(height=new_height).crop(y_center=height // 2, height=height)
        elif current_aspect < target_aspect:
            new_width = int(height * target_aspect)
            video_clip = video_clip.resize(width=new_width).crop(x_center=width // 2, width=width)

        video_clip = video_clip.resize(height=720, width=1280)

        logger.info("Adding watermark")
        watermark = (
            ImageClip(logo_path)
            .set_duration(video_clip.duration)
            .resize(height=60)
            .set_pos(("right", "bottom"))
            .set_opacity(0.6)
        )
        watermarked_clip = CompositeVideoClip([video_clip, watermark])

        logger.info("Creating intro and outro")
        logo_intro_outro = (
            ImageClip(logo_path, duration=1)
            .set_fps(video_clip.fps)
            .resize((1280, 720))
        )

        logger.info("Concatenating clips")
        final_clip = concatenate_videoclips(
            [logo_intro_outro, watermarked_clip, logo_intro_outro], method="compose"
        )

        logger.info(f"Writing processed video to {output_path}")
        final_clip.write_videofile(
            output_path, codec="libx264", fps=video_clip.fps, audio=False
        )

        logger.info("Updating database")
        # Actualizar la base de datos con la ruta relativa para mantener consistencia
        video.processed_url = relative_output_path
        video.status = VideoStatus.PROCESADO
        video.processed_at = datetime.now()
        db.commit()

        logger.info(f"Successfully processed video {video_id}")
        return {"status": "success", "video_id": video_id}

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        if 'video' in locals() and video:
            video.status = VideoStatus.ERROR
            db.commit()
        return {"status": "error", "message": str(e)}

    finally:
        if 'db' in locals():
            db.close()
        if 'original_video' in locals():
            original_video.close()
        if 'final_clip' in locals():
            final_clip.close()
