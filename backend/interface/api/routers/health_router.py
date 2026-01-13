from fastapi import APIRouter

# Router initialization
router = APIRouter(prefix="", tags=["health"])

# Health check
@router.get("/health")
def health():
    return{"status": "ok"}