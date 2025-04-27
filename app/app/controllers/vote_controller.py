from fastapi import APIRouter, status

router = APIRouter()

@router.post('/videos/{video_id}/vote', status_code=status.HTTP_201_CREATED)
def post_vote(video_id: int, user_id: int):
    return 'votes'

@router.get('/public/rankings', status_code=status.HTTP_200_OK)
def get_ranking():
    return 'ranking'

@router.get('/public/health', status_code=status.HTTP_200_OK)
def get_health():
    return 'ok'