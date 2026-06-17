from fastapi import APIRouter
from pydantic import BaseModel
from ..database import supabase

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class TaskCreate(BaseModel):
    title: str
    xp_reward: int = 10

# --- 1. PLAYER STATS ROUTE ---
@router.get("/player")
def get_player_stats():
    # Fetch your master player row (ID 1)
    response = supabase.table("player_stats").select("*").eq("id", 1).execute()
    return response.data[0]

# --- 2. READ ALL QUESTS ---
@router.get("/")
def read_tasks():
    response = supabase.table("tasks").select("*").execute()
    return response.data

# --- 3. CREATE A NEW QUEST ---
@router.post("/")
def create_task(task: TaskCreate):
    response = supabase.table("tasks").insert([{
        "title": task.title, 
        "xp_reward": task.xp_reward
    }]).execute()
    return response.data[0]

# --- 4. COMPLETE QUEST & LEVEL UP ENGINE ---
@router.delete("/{task_id}")
def complete_task(task_id: str):
        # Step A: Find out how much XP the quest is worth
    task_response = supabase.table("tasks").select("xp_reward").eq("id", task_id).execute()
    if not task_response.data:
        return {"error": "Quest not found"}
    
    # FIX: Force the reward into an integer!
    reward = int(task_response.data[0]["xp_reward"])
    
    # Step B: Delete the quest
    supabase.table("tasks").delete().eq("id", task_id).execute()

    # Step C: Get your current player stats
    player_response = supabase.table("player_stats").select("*").eq("id", 1).execute()
    
    # FIX: Force the database stats into integers!
    current_xp = int(player_response.data[0]["xp"])
    current_level = int(player_response.data[0]["level"])

    # Step D: The RPG Math
    new_xp = current_xp + reward
    new_level = (new_xp // 100) + 1 

    # Step E: Save the new stats back to the vault
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