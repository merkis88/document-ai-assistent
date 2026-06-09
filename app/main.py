from fastapi import FastAPI
from app.db.engine import engine
from app.db.base import Base


app = FastAPI(title="Document AI Assistant")

@app.on_event("startup")
async def startup():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Docs AI started"}