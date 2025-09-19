from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint that returns the service status.
    
    Returns:
        dict: A dictionary with status information
    """
    return {"status": "ok"}