
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Video as VideoModel, get_db
from pydantic import BaseModel
from typing import List, Optional


router = APIRouter()

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    url: str

class Video(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    url: str
    views: int
    likes: int

    class Config:
        orm_mode = True

@router.post("/videos/", response_model=Video)
def create_video(video: VideoCreate, db: Session = Depends(get_db)):
    db_video = VideoModel(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.get("/videos/", response_model=List[Video])
def list_videos(db: Session = Depends(get_db)):
    return db.query(VideoModel).all()

@router.get("/videos/{video_id}", response_model=Video)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.put("/videos/{video_id}", response_model=Video)
def update_video(video_id: int, video: VideoCreate, db: Session = Depends(get_db)):
    db_video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    for key, value in video.model_dump().items():
        setattr(db_video, key, value)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.delete("/videos/{video_id}", response_model=dict)
def delete_video(video_id: int, db: Session = Depends(get_db)):
    db_video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(db_video)
    db.commit()
    return {"message": "Video deleted successfully"}

