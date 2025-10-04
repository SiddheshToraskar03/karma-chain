

# KarmaChain v2: Dual-Ledger System Blueprint

## Positive Merit Flow (Punya)
[User Performs Positive Action] 
       ↓
[Action -> Intent]          e.g. completing_lessons -> learn
       ↓
[Merit Change Calculation]  (map action -> token & value)
       ↓
[Q-Learning step]          (update Q-table; recommend best actions)
       ↓
[Apply Reward -> Update DB] (increment balances, update token_meta)
       ↓
[Compute Merit Score]      (weighted sum of tokens)
       ↓
[Determine Role]           (thresholds -> learner/volunteer/seva/guru)
       ↓
[Transaction Logged]       (transactions collection + user.history)
       ↓
[Redemption / UI]         (redeem endpoint / unlocks / prestige)

## Negative Action Flow (Paap)
[User Performs Negative Action]
       ↓
[Action -> Paap Classification]  (minor/medium/maha)
       ↓
[Apply Paap Tokens]        (increment PaapTokens in user balance)
       ↓
[Optional: Auto-Appeal]    (create atonement plan if specified)
       ↓
[Transaction Logged]       (transactions collection + user.history)

## Atonement Flow
[User Appeals Karma]
       ↓
[Create Atonement Plan]    (based on Paap severity)
       ↓
[User Submits Atonement Proof]
       ↓
[Validate Proof]           (verify completion requirements)
       ↓
[Update Atonement Progress]
       ↓
[Check Completion]         (if complete, proceed to next step)
       ↓
[Apply Atonement Rewards]  (reduce Paap tokens)
       ↓
[Q-Learning step]          (positive reinforcement for atonement)
       ↓
[Transaction Logged]       (update appeal status in DB)

## Rebirth Mechanics
[Death Event Triggered]
       ↓
[Calculate Karmic Balance] (Punya vs Paap tokens)
       ↓
[Determine Loka]           (assign realm based on balance)
       ↓
[Apply Rebirth Effects]    (reset/transfer tokens based on Loka)
       ↓
[Transaction Logged]       (record rebirth event)
