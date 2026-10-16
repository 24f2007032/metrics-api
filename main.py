
import time
import uuid
from collections import defaultdict
from typing import Any

from fastapi import Body, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

EMAIL = "24f2007032@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-d8aze2.example.com"
API_KEY = "ak_zdphqiiv3dzvbnku6kziq4ww"

# Strictly allow only the assigned origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)



@app.post("/analytics")
async def analytics(
    payload: dict[str, Any] = Body(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    events = payload.get("events")
    if not isinstance(events, list):
        raise HTTPException(
            status_code=400,
            detail="'events' must be a list",
        )

    user_totals = defaultdict(float)
    revenue = 0.0
    unique_users = set()

    for event in events:
        user = event["user"]
        amount = float(event["amount"])

        unique_users.add(user)

        if amount > 0:
            revenue += amount
            user_totals[user] += amount

    top_user = max(user_totals, key=user_totals.get) if user_totals else None

    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(unique_users),
        "revenue": revenue,
        "top_user": top_user,
    }

@app.middleware("http")
async def add_request_headers(request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    elapsed = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"

    return response


@app.get("/stats")
async def stats(values: str = Query(...)):
    try:
        numbers = [int(v.strip()) for v in values.split(",")]
        if not numbers:
            raise ValueError
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="values must be comma-separated integers",
        )

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }


@app.get("/")
async def health():
    return {"status": "ok"}
