from pymongo import MongoClient
from config import Config

# Primary connection
client = MongoClient(Config.MONGO_URI)
db = client["smart_study_planner"]

# Collections as requested
users_col = db["users"]
subjects_col = db["subjects"]

# Aliases for existing app models
users_collection = users_col
subjects_collection = subjects_col

# Connection test
try:
    client.admin.command('ping')
    print("MongoDB Atlas connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
