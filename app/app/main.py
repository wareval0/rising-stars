from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.user_controller import router as user_router
from app.controllers.video_controller import router as video_router
from app.controllers.vote_controller import router as vote_router
from app.core.database import Base, engine




# Initialize the FastAPI application
app = FastAPI(
    title="FastAPI Monolith App",
    description="A monolithic",
    version="0.1.0"
)
# Initialize the database
# Create the database tables if they don't exist
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router)
app.include_router(video_router)
app.include_router(vote_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Monolith Application"}