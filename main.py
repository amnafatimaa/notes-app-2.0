from fastapi import FastAPI
from endpoints import router as notes_router 

app = FastAPI()

app.include_router(notes_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Notes API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
