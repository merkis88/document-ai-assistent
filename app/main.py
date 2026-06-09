from fastapi import FastAPI

app = FastAPI(title="Document AI Assistant")


@app.get("/")
async def root():
    return {"message": "Docs AI started"}