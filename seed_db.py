from models import User, Subject
from db import users_collection, subjects_collection

def seed():
    # 1. Clear existing data for a fresh start
    print("Clearing existing data...")
    users_collection.delete_many({})
    subjects_collection.delete_many({})

    # 2. Create Fixed Admin
    print("Creating Fixed Admin...")
    admin_email = "admin@study.com"
    admin_pass = "admin123"
    User.create_user("System Admin", admin_email, admin_pass)
    
    # 3. Create Sample Users
    users_data = [
        ("Alice Johnson", "alice@test.com", "pass123"),
        ("Bob Smith", "bob@test.com", "pass123"),
        ("Charlie Brown", "charlie@test.com", "pass123")
    ]
    
    for name, email, pw in users_data:
        print(f"Creating user: {name}...")
        User.create_user(name, email, pw)
        
        # Get the user to add subjects
        user = User.find_user_by_email(email)
        uid = user['_id']
        
        # Add sample subjects
        Subject.add_subject(uid, "Data Structures", 5, 9)
        Subject.add_subject(uid, "Operating Systems", 8, 7)
        Subject.add_subject(uid, "Machine Learning", 10, 10)
        Subject.add_subject(uid, "Economics", 3, 4)

    print("\n✅ Database Seeded Successfully!")
    print("-" * 30)
    print(f"ADMIN LOGIN: {admin_email}")
    print(f"PASSWORD:    {admin_pass}")
    print("-" * 30)

if __name__ == "__main__":
    seed()
