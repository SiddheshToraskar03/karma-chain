from pymongo import MongoClient

# 🔹 Paste your MongoDB connection string here
MONGO_URI = "mongodb+srv://allownote1_db_user:noteallow123@cluster-karma.bv0jxuj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-karma"

# 🔹 Connect to cluster
client = MongoClient(MONGO_URI)

# 🔹 Select database and collections
db = client["karma-chain"]
q_table = db["q_table"]
transactions = db["transactions"]
users = db["user"]

# ---------- TEST INSERT ----------
def test_insert():
    sample_user = {
        "user_id": "U123",
        "name": "Siddhesh",
        "points": 100,
        "level": "beginner"
    }
    result = users.insert_one(sample_user)
    print("✅ Inserted User with _id:", result.inserted_id)

    sample_transaction = {
        "user_id": "U123",
        "action": "purchase",
        "points_earned": 50
    }
    result2 = transactions.insert_one(sample_transaction)
    print("✅ Inserted Transaction with _id:", result2.inserted_id)

    sample_q = {
        "state": "start",
        "action": "purchase",
        "reward": 10,
        "next_state": "loyal"
    }
    result3 = q_table.insert_one(sample_q)
    print("✅ Inserted Q-Table Row with _id:", result3.inserted_id)

# ---------- TEST FETCH ----------
def test_fetch():
    print("\n📌 Users Collection:")
    for doc in users.find():
        print(doc)

    print("\n📌 Transactions Collection:")
    for doc in transactions.find():
        print(doc)

    print("\n📌 Q-Table Collection:")
    for doc in q_table.find():
        print(doc)

if __name__ == "__main__":
    test_insert()
    test_fetch()
