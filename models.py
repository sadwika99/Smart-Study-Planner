from db import users_collection, subjects_collection
from bson.objectid import ObjectId
from flask_bcrypt import generate_password_hash, check_password_hash

class User:
    @staticmethod
    def create_user(name, email, password):
        # First user becomes admin
        role = "admin" if users_collection.count_documents({}) == 0 else "user"
        hashed_password = generate_password_hash(password).decode('utf-8')
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": role
        }
        return users_collection.insert_one(user_data)

    @staticmethod
    def find_user_by_email(email):
        return users_collection.find_one({"email": email})

    @staticmethod
    def find_user_by_id(user_id):
        return users_collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_all_users():
        return list(users_collection.find())

    @staticmethod
    def delete_user(user_id):
        # Also delete user's subjects
        subjects_collection.delete_many({"user_id": ObjectId(user_id)})
        return users_collection.delete_one({"_id": ObjectId(user_id)})

class Subject:
    @staticmethod
    def add_subject(user_id, name, study_time, importance):
        subject_data = {
            "user_id": ObjectId(user_id),
            "name": name,
            "study_time": int(study_time),
            "importance": int(importance)
        }
        return subjects_collection.insert_one(subject_data)

    @staticmethod
    def get_subjects_by_user(user_id):
        return list(subjects_collection.find({"user_id": ObjectId(user_id)}))

    @staticmethod
    def delete_subject(subject_id):
        return subjects_collection.delete_one({"_id": ObjectId(subject_id)})

    @staticmethod
    def get_all_subjects():
        return list(subjects_collection.find())
