from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Define separate collections for each data type
users_col = db["users"]
transactions_col = db["transactions"]
qtable_col = db["q_table"]
appeals_col = db["appeals"]
atonements_col = db["atonements"]
death_events_col = db["death_events"]
karma_events_col = db["karma_events"]  # New collection for unified events

# Function to get database instance
def get_db():
    return db
