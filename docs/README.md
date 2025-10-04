## To Run this project 
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up MongoDB:
   - Install MongoDB locally or use a cloud service (e.g., MongoDB Atlas).
   - Update the connection string in `config.py`.
4. Run scripts\migrate_to_v2.py
   Run fix_paap_tokens.py
   Run scripts\migrate_collection.py
   Run test_collection.py

  Run the server: `uvicorn main:app --reload`
5. Access the API docs: http://127.0.0.1:8000

6. To check appeals, atonement and death_event database collections are working or not you can :
  Run test_appeals.py

# KarmaChain v2: Dual-Ledger Dharma-Based AI Loyalty & Reward System  

## 🌟 Overview
KarmaChain is an AI-powered loyalty & reward system inspired by Sanatan Dharma principles.  
It rewards users for **learning**, **service**, and **selfless acts** using modular merit tokens.  
The system uses **Reinforcement Learning (Q-learning)** to guide users toward long-term dharmic engagement.

Version 2 introduces a **dual-ledger system** that tracks both positive merit (Punya) and negative actions (Paap), with an atonement mechanism for karmic balance.

---

## ⚙️ Features
- Role progression: **Learner → Volunteer → Seva → Guru**
- Merit tokens:
  - **DharmaPoints** (knowledge actions)
  - **SevaPoints** (community/help actions)
  - **PunyaTokens** (rare, high-tier selfless actions)
- **Paap tokens** (negative actions):
  - **MinorPaap** (minor infractions)
  - **MediumPaap** (moderate violations)
  - **MahaPaap** (serious transgressions)
- **Atonement system** for reducing Paap through prescribed actions
- **Rebirth mechanics** with Loka assignment based on karmic balance
- Decay & expiry: old merits fade over time to promote consistent practice
- Transaction logging for audit/history
- Q-learning logic to recommend best dharmic actions and atonement paths
- REST APIs with FastAPI + MongoDB

---

## 🧩 System Design
**Flow:**  
`Action → Intent → Merit → Reward Tier → Redemption`

**Roles:**  
- Learner (new)  
- Volunteer (helper)  
- Seva (community service)  
- Guru (mentor)

**Actions to Tokens:**
- Completing lessons → DharmaPoints (5)
- Helping peers → SevaPoints (10)
- Solving doubts → SevaPoints (8)
- Selfless service → PunyaTokens (2)
- Cheating → -20 DharmaPoints

---

## 📂 Project Structure
karma-chain/
│── main.py # FastAPI entrypoint
│── database.py # MongoDB connection & collections
│── config.py # Roles, actions, reward maps
│── routes/ # API routes
│ └── actions.py # /log-action endpoint
│── utils/ # Helper modules
│ ├── tokens.py # Decay, expiry, time helpers
│ ├── merit.py # Merit calculation, role determination
│ ├── transactions.py # Log transaction helper
│ ├── qlearning.py # Q-learning step logic
│ └── user_utils.py # create_user_if_missing()
│── models/ # Pydantic schemas
│ └── init.py
│── test_requests.py # API test script
│── requirements.txt
│── README.md