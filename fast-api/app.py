from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/v1/highlights")
async def return_highlights():
    return {"message": "Hello, World!"}