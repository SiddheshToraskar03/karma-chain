from fastapi import FastAPI
from routes import actions, balance, redeem, policy, user, admin, appeal

app = FastAPI(title="KarmaChain v2 (Dual-Ledger)")

app.include_router(actions.router)
app.include_router(balance.router)
app.include_router(redeem.router)
app.include_router(policy.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(appeal.router)
