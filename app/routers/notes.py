from fastapi import APIRouter
from pydantic import BaseModel
from ..database import supabase

router = APIRouter(prefix="/notes", tags=["Notes"])

class NoteUpdate(BaseModel):
    content: str

# 1. READ THE SCRATCHPAD
@router.get("/")
def get_note():
    # Fetch your master note row (ID 1)
    response = supabase.table("notes").select("*").eq("id", 1).execute()
    return response.data[0]

# 2. SAVE THE SCRATCHPAD
@router.put("/")
def update_note(note: NoteUpdate):
    # Overwrite the master note with whatever you typed
    response = supabase.table("notes").update({"content": note.content}).eq("id", 1).execute()
    return {"message": "Scratchpad saved successfully!"}