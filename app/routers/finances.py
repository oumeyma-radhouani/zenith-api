from fastapi import APIRouter
from pydantic import BaseModel
from ..database import supabase

router = APIRouter(prefix="/finances", tags=["Finances"])

class TransactionCreate(BaseModel):
    title: str
    amount: float
    is_income: bool

@router.get("/")
def get_transactions():
    # Fetch all transactions, newest first
    response = supabase.table("finances").select("*").order("id", desc=True).execute()
    
    # Let the Python brain calculate the total balance!
    total = sum([t["amount"] if t["is_income"] else -t["amount"] for t in response.data])
    
    return {"transactions": response.data, "balance": total}

@router.post("/")
def add_transaction(transaction: TransactionCreate):
    response = supabase.table("finances").insert([{
        "title": transaction.title,
        "amount": transaction.amount,
        "is_income": transaction.is_income
    }]).execute()
    return response.data[0]

@router.delete("/{t_id}")
def delete_transaction(t_id: int):
    supabase.table("finances").delete().eq("id", t_id).execute()
    return {"message": "Transaction deleted"}