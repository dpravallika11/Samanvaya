import os
from pymongo import MongoClient

# Use local MongoDB by default if NO env variable is provided
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')

try:
    client = MongoClient(MONGO_URI)
    db = client['samanvaya_db']
    
    # Collections
    users_collection = db['users']
    datasets_collection = db['datasets']
    transformations_collection = db['transformations']
    schema_mappings_collection = db['schema_mappings']
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # In a real app we'd handle fallback better, but this suffices for the hackathon
    users_collection = None
    datasets_collection = None
    transformations_collection = None
    schema_mappings_collection = None

def is_connected():
    return users_collection is not None

def get_user(username):
    if users_collection is not None:
        return users_collection.find_one({"username": username})
    return None

def create_user(username, password_hash, email=None):
    if users_collection is not None:
        # Check if exists
        if not get_user(username):
            user_doc = {
                "username": username,
                "password_hash": password_hash,
                "email": email,
                "created_at": __import__('datetime').datetime.utcnow()
            }
            users_collection.insert_one(user_doc)
            return True
    return False

def verify_user(username, password):
    from werkzeug.security import check_password_hash
    user = get_user(username)
    if not user:
        return False
    return check_password_hash(user.get("password_hash", ""), password)

def save_dataset_metadata(dataset_name, filepath, username):
    if datasets_collection is not None:
        from datetime import datetime
        datasets_collection.insert_one({
            "dataset_name": dataset_name,
            "filepath": filepath,
            "username": username,
            "upload_timestamp": datetime.utcnow()
        })

def save_transformation_history(dataset_name, columns_modified):
    if transformations_collection is not None:
        from datetime import datetime
        transformations_collection.insert_one({
            "dataset_name": dataset_name,
            "columns_modified": columns_modified,
            "transformation_date": datetime.utcnow()
        })

def get_recent_history(limit=5):
    if transformations_collection is not None:
        # returns cursor
        try:
            return list(transformations_collection.find().sort("transformation_date", -1).limit(limit))
        except:
            return []
    return []

def save_schema_mapping(mapping_data):
    if schema_mappings_collection is not None:
        from datetime import datetime
        mapping_data["created_at"] = datetime.utcnow()
        schema_mappings_collection.insert_one(mapping_data)
