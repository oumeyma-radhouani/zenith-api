from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import tasks

app = FastAPI(title="Zenith API")

# --- THE VIP GUEST LIST (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Connect the specific routers
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Zenith Vault"}