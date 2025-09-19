"""
Chat completion endpoints.

This module provides endpoints for:
1. Chat completion with vector search
2. Managing default system prompt
3. Getting chat service status
"""

from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.utils.chat_service import chat_service


router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    system_prompt: Optional[str] = Field(None, description="Optional custom system prompt")
    max_tokens: int = Field(1000, ge=1, le=4000, description="Maximum tokens in response")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Response creativity")


class ChatResponse(BaseModel):
    """Chat completion response model."""
    response: str = Field(..., description="Assistant's response")
    context_used: int = Field(..., description="Number of context chunks used")
    context_sources: List[Dict[str, Any]] = Field(..., description="Sources used for context")
    usage: Dict[str, int] = Field(..., description="Token usage information")


class SystemPromptRequest(BaseModel):
    """System prompt update request model."""
    prompt: str = Field(..., min_length=1, description="New system prompt")


class SystemPromptResponse(BaseModel):
    """System prompt response model."""
    prompt: str = Field(..., description="Current system prompt")
    updated: bool = Field(False, description="Whether prompt was updated")


@router.post("/chat/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion with vector search context.
    
    This endpoint:
    1. Searches for relevant context from uploaded PDF documents
    2. Enhances the system prompt with found context
    3. Generates a response using Azure OpenAI chat model
    4. Returns the response with metadata about sources used
    
    Args:
        request: Chat completion request with messages and options
        
    Returns:
        ChatResponse: Generated response with context information
        
    Raises:
        HTTPException: If chat service is not available or request fails
    """
    if chat_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is not available. Please check Azure OpenAI configuration."
        )
    
    try:
        # Convert Pydantic models to dicts
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Generate chat completion
        result = await chat_service.chat_completion(
            messages=messages,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error in chat completion: {str(e)}"
        )


@router.get("/chat/system-prompt", response_model=SystemPromptResponse)
async def get_system_prompt():
    """
    Get the current default system prompt.
    
    Returns:
        SystemPromptResponse: Current system prompt
        
    Raises:
        HTTPException: If chat service is not available
    """
    if chat_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is not available. Please check Azure OpenAI configuration."
        )
    
    try:
        prompt = chat_service.get_default_system_prompt()
        return SystemPromptResponse(prompt=prompt, updated=False)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system prompt: {str(e)}"
        )


@router.put("/chat/system-prompt", response_model=SystemPromptResponse)
async def update_system_prompt(request: SystemPromptRequest):
    """
    Update the default system prompt.
    
    This endpoint allows updating the default system prompt that will be used
    for all future chat completions (unless overridden per request).
    
    Args:
        request: New system prompt
        
    Returns:
        SystemPromptResponse: Updated system prompt
        
    Raises:
        HTTPException: If chat service is not available or update fails
    """
    if chat_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service is not available. Please check Azure OpenAI configuration."
        )
    
    try:
        success = chat_service.update_default_system_prompt(request.prompt)
        
        if success:
            return SystemPromptResponse(prompt=request.prompt, updated=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update system prompt"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system prompt: {str(e)}"
        )


@router.get("/chat/status")
async def get_chat_status():
    """
    Get chat service status and configuration.
    
    Returns:
        Dict: Chat service status and configuration information
    """
    if chat_service is None:
        return {
            "status": "unavailable",
            "message": "Chat service is not available. Please check Azure OpenAI configuration.",
            "configured": False
        }
    
    try:
        # Get basic service information
        prompt = chat_service.get_default_system_prompt()
        
        return {
            "status": "available",
            "message": "Chat service is ready",
            "configured": True,
            "default_prompt_length": len(prompt),
            "chat_deployment": chat_service.chat_deployment,
            "api_version": chat_service.api_version
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Chat service error: {str(e)}",
            "configured": True
        }