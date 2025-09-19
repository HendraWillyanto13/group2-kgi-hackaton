import os
import httpx
import logging
from pathlib import Path
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)

# Upload directory path (should match upload.py)
UPLOAD_DIR = Path("uploads")

# Azure Computer Vision configuration
VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")
VISION_KEY = os.getenv("VISION_KEY")

def get_vision_api_url() -> str:
    """Construct the Azure Computer Vision API URL for v3.2 analyze."""
    if not VISION_ENDPOINT:
        raise ValueError("VISION_ENDPOINT environment variable is not set")
    
    # Remove trailing slash if present
    endpoint = VISION_ENDPOINT.rstrip('/')
    return f"{endpoint}/vision/v3.2/analyze?visualFeatures=Objects"

async def call_azure_vision_api(image_path: Path) -> Dict[str, Any]:
    """
    Call Azure Computer Vision Object Detection API.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict containing the API response
        
    Raises:
        HTTPException: If API call fails or credentials are missing
    """
    if not VISION_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Azure Vision API key not configured (VISION_KEY environment variable missing)"
        )
    
    if not VISION_ENDPOINT:
        raise HTTPException(
            status_code=500,
            detail="Azure Vision endpoint not configured (VISION_ENDPOINT environment variable missing)"
        )
    
    try:
        api_url = get_vision_api_url()
        headers = {
            "Ocp-Apim-Subscription-Key": VISION_KEY,
            "Content-Type": "application/octet-stream"
        }
        
        # Read image file
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, content=image_data)
            
            if response.status_code != 200:
                logger.error(f"Azure Vision API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Azure Vision API error: {response.status_code}"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Network error calling Azure Vision API: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to Azure Vision API"
        )
    except Exception as e:
        logger.error(f"Unexpected error calling Azure Vision API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal error processing image"
        )

def normalize_detection_response(api_response: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Normalize Azure Computer Vision API response to the expected format.
    
    Expected output format:
    {
        "boxes": [
            {
                "label": str,
                "x": float,  # normalized 0-1
                "y": float,  # normalized 0-1
                "w": float,  # normalized 0-1
                "h": float,  # normalized 0-1
                "score": float  # 0-1 confidence
            }
        ]
    }
    
    Args:
        api_response: Raw response from Azure Computer Vision API
        
    Returns:
        Normalized response with boxes array
    """
    try:
        boxes = []
        
        # Get image dimensions for normalization
        metadata = api_response.get("metadata", {})
        img_width = metadata.get("width", 1)
        img_height = metadata.get("height", 1)
        
        # Extract objects from the API response
        objects = api_response.get("objects", [])
        
        for obj in objects:
            # Extract bounding box rectangle
            rect = obj.get("rectangle", {})
            
            # Normalize coordinates to 0-1 range
            x = rect.get("x", 0) / img_width
            y = rect.get("y", 0) / img_height
            w = rect.get("w", 0) / img_width
            h = rect.get("h", 0) / img_height
            
            box = {
                "label": obj.get("object", "unknown"),
                "x": round(x, 4),
                "y": round(y, 4),
                "w": round(w, 4),
                "h": round(h, 4),
                "score": round(obj.get("confidence", 0.0), 4)
            }
            
            boxes.append(box)
        
        return {"boxes": boxes}
        
    except Exception as e:
        logger.error(f"Error normalizing detection response: {str(e)}")
        return {"boxes": []}

@router.get("/detections/{image_id}")
async def get_detections(image_id: str):
    """
    Get object detections for an uploaded image.
    
    Args:
        image_id: The image identifier (filename without extension or with extension)
        
    Returns:
        JSON response with detected objects in normalized bounding boxes
        Format: { "boxes": [{ "label": str, "x": float, "y": float, "w": float, "h": float, "score": float }] }
        
    Error cases return: { "boxes": [] } with appropriate HTTP status codes
    """
    try:
        # Handle both cases: image_id with or without extension
        image_path = None
        
        # First, try to find the file as-is
        potential_path = UPLOAD_DIR / image_id
        if potential_path.exists() and potential_path.is_file():
            image_path = potential_path
        else:
            # Try to find file with common image extensions
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                potential_path = UPLOAD_DIR / f"{image_id}{ext}"
                if potential_path.exists() and potential_path.is_file():
                    image_path = potential_path
                    break
        
        if not image_path:
            logger.warning(f"Image not found: {image_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Image not found: {image_id}"
            )
        
        # Call Azure Computer Vision API
        api_response = await call_azure_vision_api(image_path)
        
        # Normalize the response
        normalized_response = normalize_detection_response(api_response)
        
        logger.info(f"Successfully processed detections for image: {image_id}")
        return normalized_response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing detections for {image_id}: {str(e)}")
        # Return empty boxes on any failure with error status
        return {"boxes": []}