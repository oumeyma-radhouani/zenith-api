import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Tell Python to read the hidden .env file
load_dotenv()

# Pull the keys into memory
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the connection instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)