from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from LegalEaseAPI.routes import router


app = FastAPI(
    title="LegalEase API",
    description=(
        "Backend API powering AI-assisted "
        "legal document generation."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def read_root():

    return {
        "status": "online",
        "service": "LegalEase Backend API",
        "endpoints": [
            "/health",
            "/generate"
        ]
    }


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "LegalEaseAPI.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )