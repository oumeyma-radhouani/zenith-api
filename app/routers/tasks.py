from fastapi import APIRouter
from pydantic import BaseModel
from ..database import supabase
from datetime import date
from typing import Optional, List

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# --- THE SECURITY CHECKPOINT ---
class TaskCreate(BaseModel):
    title: str
    difficulty: str = "minion"
    is_daily: bool = False
    due_date: Optional[str] = None
    subtasks: List[str] = [] # <-- NEW: Expect a list of sub-task strings!

# --- 1. PLAYER STATS ROUTE ---
@router.get("/player")
def get_player_stats():
    response = supabase.table("player_stats").select("*").eq("id", 1).execute()
    return response.data[0]

# --- 2. READ ALL QUESTS (NOW WITH SUBTASKS) ---
@router.get("/")
def read_tasks():
    # NEW: Fetch tasks AND their linked subtasks in one single query!
    response = supabase.table("tasks").select("*, subtasks(*)").execute()
    today = str(date.today())
    
    active_tasks = []
    for task in response.data:
        if task.get("is_daily") and task.get("last_completed") == today:
            continue 
        active_tasks.append(task)
        
    return active_tasks

# --- 3. CREATE A NEW QUEST (WITH CHECKLIST) ---
@router.post("/")
def create_task(task: TaskCreate):
    xp_map = {"minion": 10, "elite": 30, "boss": 100}
    calculated_xp = xp_map.get(task.difficulty.lower(), 10)

    # Insert the main task
    task_response = supabase.table("tasks").insert([{
        "title": task.title, 
        "xp_reward": calculated_xp,
        "is_daily": task.is_daily,
        "due_date": task.due_date
    }]).execute()
    
    new_task = task_response.data[0]
    
    # Insert any subtasks and link them to the new task's UUID
    if task.subtasks:
        subtask_payload = [{"task_id": new_task["id"], "title": stitle} for stitle in task.subtasks]
        supabase.table("subtasks").insert(subtask_payload).execute()
        
    return new_task

# --- 4. TOGGLE A SUBTASK ---
@router.put("/subtasks/{subtask_id}")
def toggle_subtask(subtask_id: int):
    sub = supabase.table("subtasks").select("is_completed").eq("id", subtask_id).execute()
    if not sub.data:
        return {"error": "Subtask not found"}
    
    current_status = sub.data[0]["is_completed"]
    # Flip the boolean!
    supabase.table("subtasks").update({"is_completed": not current_status}).eq("id", subtask_id).execute()
    return {"message": "Subtask toggled!"}

# --- 5. COMPLETE QUEST & LEVEL UP ENGINE ---
@router.delete("/{task_id}")
def complete_task(task_id: str):
    # --- NEW GUARDRAIL: Check if subtasks are finished! ---
    subs = supabase.table("subtasks").select("is_completed").eq("task_id", task_id).execute()
    if subs.data:
        for sub in subs.data:
            if not sub["is_completed"]:
                return {"error": "Finish all sub-tasks first!"} # The Bouncer rejects it!

    task_response = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_response.data:
        return {"error": "Quest not found"}
    
    task_data = task_response.data[0]
    reward = int(task_data["xp_reward"])
    is_daily = task_data.get("is_daily", False)
    last_completed = task_data.get("last_completed")
    today = str(date.today())

    if is_daily and last_completed == today:
        return {"message": "Already completed today!"}
    
    if is_daily:
        supabase.table("tasks").update({"last_completed": today}).eq("id", task_id).execute()
        # Reset the checklist for tomorrow!
        supabase.table("subtasks").update({"is_completed": False}).eq("task_id", task_id).execute()
    else:
        # Deleting the task automatically vaporizes the subtasks because of the CASCADE rule
        supabase.table("tasks").delete().eq("id", task_id).execute()

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