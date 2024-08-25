
from fastapi import FastAPI
from api import videos

app = FastAPI()

app.include_router(videos.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastPlay API!"}
