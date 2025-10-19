from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 👇 this sets the base path
app = FastAPI(
    title="MakingMeHappier API",
    version="0.1.0",
    root_path="/makingmehappier"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to MakingMeHappier!"}

@app.get("/add_task")
def add_task():
    return {"message": "This is the add_task endpoint"}
