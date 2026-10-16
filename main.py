
import time
import uuid

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

app = FastAPI()

EMAIL = "24f2007032@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-d8aze2.example.com"

# Strictly allow only the assigned origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


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
