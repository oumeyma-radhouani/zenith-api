from fastapi import APIRouter
from pydantic import BaseModel
from ..database import supabase

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# --- THE SECURITY CHECKPOINT ---
class TaskCreate(BaseModel):
    title: str
    xp_reward: int = 10

# 1. READ ALL QUESTS
@router.get("/")
def read_tasks():
    response = supabase.table("tasks").select("*").execute()
    return response.data

# 2. CREATE A NEW QUEST
@router.post("/")
def create_task(task: TaskCreate):
    # Insert the new quest into the Supabase vault
    response = supabase.table("tasks").insert([{
        "title": task.title, 
        "xp_reward": task.xp_reward
    }]).execute()
    return response.data[0]

# 3. COMPLETE/DELETE A QUEST
@router.delete("/{task_id}")
def delete_task(task_id: int):
    # Delete the quest where the ID matches
    supabase.table("tasks").delete().eq("id", task_id).execute()
    return {"message": "Quest completed!"}