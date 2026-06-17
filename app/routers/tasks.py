from fastapi import APIRouter
from pydantic import BaseModel
from ..database import supabase
from datetime import date # <-- NEW: We need this to get today's date!

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# --- THE SECURITY CHECKPOINT ---
class TaskCreate(BaseModel):
    title: str
    difficulty: str = "minion"
    is_daily: bool = False # <-- NEW: Expect the checkbox!

# --- 1. PLAYER STATS ROUTE ---
@router.get("/player")
def get_player_stats():
    response = supabase.table("player_stats").select("*").eq("id", 1).execute()
    return response.data[0]

# --- 2. READ ALL QUESTS (THE MIDNIGHT FILTER) ---
@router.get("/")
def read_tasks():
    response = supabase.table("tasks").select("*").execute()
    
    # Get today's date as a string (e.g., '2026-06-17')
    today = str(date.today())
    
    active_tasks = []
    for task in response.data:
        # If it's a daily task AND it was already completed today, hide it!
        if task.get("is_daily") and task.get("last_completed") == today:
            continue 
            
        active_tasks.append(task)
        
    return active_tasks

# --- 3. CREATE A NEW QUEST ---
@router.post("/")
def create_task(task: TaskCreate):
    xp_map = {
        "minion": 10,
        "elite": 30,
        "boss": 100
    }
    calculated_xp = xp_map.get(task.difficulty.lower(), 10)

    response = supabase.table("tasks").insert([{
        "title": task.title, 
        "xp_reward": calculated_xp,
        "is_daily": task.is_daily # <-- Save the habit status!
    }]).execute()
    
    return response.data[0]

# --- 4. COMPLETE QUEST & LEVEL UP ENGINE ---
@router.delete("/{task_id}")
def complete_task(task_id: str):
    task_response = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_response.data:
        return {"error": "Quest not found"}
    
    task_data = task_response.data[0]
    reward = int(task_data["xp_reward"])
    is_daily = task_data.get("is_daily", False)
    last_completed = task_data.get("last_completed")
    today = str(date.today())

    # --- ANTI-SPAM SHIELD ---
    if is_daily and last_completed == today:
        return {"message": "Already completed today!"}
    
    # --- DELETE OR UPDATE ---
    if is_daily:
        # It's a habit! Stamp it with today's date to hide it.
        supabase.table("tasks").update({"last_completed": today}).eq("id", task_id).execute()
    else:
        # It's a normal quest! Vaporize it.
        supabase.table("tasks").delete().eq("id", task_id).execute()

    # Get stats and do RPG Math
    player_response = supabase.table("player_stats").select("*").eq("id", 1).execute()
    current_xp = int(player_response.data[0]["xp"])
    current_level = int(player_response.data[0]["level"])

    new_xp = current_xp + reward
    new_level = (new_xp // 100) + 1 

    supabase.table("player_stats").update({
        "xp": new_xp,
        "level": new_level
    }).eq("id", 1).execute()

    return {
        "message": "Quest completed!", 
        "xp_gained": reward, 
        "new_total_xp": new_xp, 
        "new_level": new_level
    }