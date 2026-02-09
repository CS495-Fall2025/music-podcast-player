from fastapi import FastAPI

from rss_music_db_service.routes import users


app = FastAPI()
app.include_router(users, prefix="/users")
