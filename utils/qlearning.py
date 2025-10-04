import datetime
import numpy as np
from database import qtable_col, users_col
from config import ACTIONS, ROLE_SEQUENCE, ALPHA, GAMMA, REWARD_MAP, CHEAT_PUNISHMENT_LEVELS, ATONEMENT_REWARDS
from utils.merit import determine_role_from_merit

states = ROLE_SEQUENCE[:]
n_states = len(states)
n_actions = len(ACTIONS)
Q = np.zeros((n_states, n_actions))

# restore Q-table from DB
q_doc = qtable_col.find_one({})
if q_doc and "q" in q_doc:
    try:
        Q = np.array(q_doc["q"])
    except Exception:
        Q = np.zeros((n_states, n_actions))

def save_q_table():
    # Use timezone-aware datetime (fix for Python 3.12+)
    qtable_col.replace_one({}, {"q": Q.tolist(), "updated_at": datetime.datetime.now(datetime.timezone.utc)}, upsert=True)

def q_learning_step(user_id: str, state: str, action: str, reward: float):
    # Ensure state is valid
    if state not in states:
        state = states[0]  # Default to first state if invalid
    s = states.index(state)
    
    # Ensure action is valid
    if action not in ACTIONS:
        # Handle unknown action gracefully
        return reward, state
    a = ACTIONS.index(action)

    user_doc = users_col.find_one({"user_id": user_id})
    if not user_doc:
        return reward, state

    temp_balances = user_doc["balances"].copy()
    
    # Get the appropriate token for the action
    if action == "cheat":
        # For cheat actions, we'll use DharmaPoints as the token (as defined in CHEAT_PUNISHMENT_LEVELS)
        token = "DharmaPoints"
    else:
        # For regular actions, use the token defined in REWARD_MAP
        token = REWARD_MAP[action]["token"]
    
    # Update the correct token balance
    temp_balances[token] = temp_balances.get(token, 0) + reward

    estimated_merit = temp_balances.get("DharmaPoints", 0) * 1.0 + temp_balances.get("SevaPoints", 0) * 1.2 + temp_balances.get("PunyaTokens", 0) * 3.0
    next_role = determine_role_from_merit(estimated_merit)
    next_state = states.index(next_role)

    Q[s, a] = Q[s, a] + ALPHA * (reward + GAMMA * float(np.max(Q[next_state])) - Q[s, a])
    save_q_table()
    
    # Return the reward and the next role as expected
    return reward, next_role

def atonement_q_learning_step(user_id: str, severity_class: str):
    """
    Apply Q-learning update for atonement completion.
    
    Args:
        user_id (str): The user's ID
        severity_class (str): The severity class of the completed atonement
        
    Returns:
        tuple: (reward_value, next_role)
    """
    # Get user and current state
    user_doc = users_col.find_one({"user_id": user_id})
    if not user_doc:
        return 0, None
    
    state = user_doc.get("role", states[0])
    if state not in states:
        state = states[0]
    
    s = states.index(state)
    
    # Get reward for atonement completion
    if severity_class not in ATONEMENT_REWARDS:
        return 0, state
    
    reward_info = ATONEMENT_REWARDS[severity_class]
    reward_value = reward_info["value"]
    token = reward_info["token"]
    
    # Update user's balances
    temp_balances = user_doc["balances"].copy()
    temp_balances[token] = temp_balances.get(token, 0) + reward_value
    
    # Calculate next state based on updated balances
    estimated_merit = temp_balances.get("DharmaPoints", 0) * 1.0 + temp_balances.get("SevaPoints", 0) * 1.2 + temp_balances.get("PunyaTokens", 0) * 3.0
    next_role = determine_role_from_merit(estimated_merit)
    next_state = states.index(next_role)
    
    # Choose a representative action for atonement (using "helping_peers" as it's a positive action)
    atonement_action = "helping_peers"
    if atonement_action in ACTIONS:
        a = ACTIONS.index(atonement_action)
        
        # Update Q-table with positive reinforcement for atonement
        Q[s, a] = Q[s, a] + ALPHA * (reward_value + GAMMA * float(np.max(Q[next_state])) - Q[s, a])
        save_q_table()
    
    # Update user's balance with the reward
    users_col.update_one(
        {"user_id": user_id},
        {"$inc": {f"balances.{token}": reward_value}}
    )
    
    return reward_value, next_role