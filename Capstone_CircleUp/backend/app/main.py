from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base

from app.models.user import User
from app.models.activity import Activity
from app.models.participation import Participation

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.activity import router as activity_router
from app.routes.participation import router as participation_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(activity_router)
app.include_router(participation_router)


@app.get("/")
def home():
    return {
        "message": "CircleUp Backend Running"
    }
