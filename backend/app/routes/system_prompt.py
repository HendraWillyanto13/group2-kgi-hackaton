from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Define the path to the system prompt file
SYSTEM_PROMPT_FILE = Path("config/default_system_prompt.txt")

class SystemPromptUpdate(BaseModel):
    """Model for system prompt update request"""
    content: str

@router.get("/system-prompt")
async def get_system_prompt():
    """
    Get the current system prompt content.
    
    Returns:
        dict: A dictionary containing the system prompt content
    """
    try:
        if not SYSTEM_PROMPT_FILE.exists():
            raise HTTPException(status_code=404, detail="System prompt file not found")
        
        with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info("System prompt retrieved successfully")
        return {"content": content}
    
    except Exception as e:
        logger.error(f"Error reading system prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading system prompt: {str(e)}")

@router.put("/system-prompt")
async def update_system_prompt(prompt_update: SystemPromptUpdate):
    """
    Update the system prompt content.
    
    Args:
        prompt_update (SystemPromptUpdate): The new system prompt content
    
    Returns:
        dict: A dictionary with success status and updated content
    """
    try:
        # Ensure the config directory exists
        SYSTEM_PROMPT_FILE.parent.mkdir(exist_ok=True)
        
        # Write the new content to the file
        with open(SYSTEM_PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write(prompt_update.content)
        
        logger.info("System prompt updated successfully")
        return {
            "status": "success",
            "message": "System prompt updated successfully",
            "content": prompt_update.content
        }
    
    except Exception as e:
        logger.error(f"Error updating system prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating system prompt: {str(e)}")