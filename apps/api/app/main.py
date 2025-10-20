from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import add_task

app = FastAPI(
    title="Making Me Happier",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include router with prefix
app.include_router(add_task.router, prefix="/makingmehappier")

@app.get("/makingmehappier")
def home():
    return {"message": "Welcome to Making Me Happier!"}
