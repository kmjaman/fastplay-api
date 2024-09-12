
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Video as VideoModel, get_db
from pydantic import BaseModel
from typing import List, Optional

from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
import shutil
import os


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
        exclude = {"file_path"}

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



UPLOAD_DIRECTORY = "./uploads/"

@router.post("/videos/upload/", response_model=Video)
def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create a new video entry in the database with the file path
    db_video = VideoModel(
        title=title,
        description=description,
        url=f"/videos/play/{file.filename}",
        file_path=file_path
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video



@router.get("/videos/play/{filename}", response_class=FileResponse)
def play_video(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path, media_type="video/mp4")