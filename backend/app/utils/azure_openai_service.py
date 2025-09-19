"""
Azure OpenAI embedding service.

This module handles communication with Azure OpenAI API
to generate embeddings from text content.
"""

import os
import asyncio
from typing import List, Dict, Optional
from openai import AzureOpenAI
from fastapi import HTTPException


class AzureOpenAIEmbeddingService:
    """Service for generating embeddings using Azure OpenAI."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        self.embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
        self.max_tokens = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "8191"))
        
        # Validate required environment variables
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            raise HTTPException(
                status_code=500,
                detail="Missing required Azure OpenAI environment variables. Please check .env file."
            )
        
        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Azure OpenAI client: {str(e)}"
            )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text chunk.
        
        Args:
            text: Text content to generate embedding for
            
        Returns:
            List[float]: The embedding vector
            
        Raises:
            HTTPException: If embedding generation fails
        """
        try:
            # Run the synchronous API call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    model=self.deployment_name,
                    input=text.replace("\n", " ")
                )
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embedding: {str(e)}"
            )
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple text chunks.
        
        Args:
            texts: List of text content to generate embeddings for
            
        Returns:
            List[List[float]]: List of embedding vectors
            
        Raises:
            HTTPException: If embedding generation fails
        """
        try:
            embeddings = []
            
            # Process texts in batches to avoid rate limits
            batch_size = 16  # Azure OpenAI recommended batch size
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Run the synchronous API call in a thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.embeddings.create(
                        model=self.deployment_name,
                        input=[text.replace("\n", " ") for text in batch_texts]
                    )
                )
                
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay between batches to avoid rate limiting
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return embeddings
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embeddings batch: {str(e)}"
            )
    
    def get_embedding_info(self) -> Dict:
        """
        Get information about the embedding configuration.
        
        Returns:
            Dict: Information about embedding model and configuration
        """
        return {
            "model": self.embedding_model,
            "deployment_name": self.deployment_name,
            "max_tokens": self.max_tokens,
            "api_version": self.api_version,
            "endpoint": self.endpoint.split("//")[1] if "//" in self.endpoint else self.endpoint
        }


def get_embedding_service():
    """Get the embedding service instance, handling initialization errors gracefully."""
    try:
        return AzureOpenAIEmbeddingService()
    except HTTPException as e:
        print(f"Warning: Azure OpenAI service not properly configured: {e.detail}")
        return None
    except Exception as e:
        print(f"Warning: Failed to initialize Azure OpenAI service: {str(e)}")
        return None


# Global instance to be used throughout the application
embedding_service = get_embedding_service()