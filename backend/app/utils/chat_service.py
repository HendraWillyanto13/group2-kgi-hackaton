"""
Chat completion service using Azure OpenAI and FAISS vector search.

This module handles chat completion requests by:
1. Searching for relevant context from FAISS vector store
2. Loading PDF metadata for additional context
3. Generating chat responses using Azure OpenAI chat models
4. Managing default system prompts
"""

import os
import json
import pickle
import asyncio
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import numpy as np
import faiss
from openai import AzureOpenAI
from fastapi import HTTPException

from .azure_openai_service import AzureOpenAIEmbeddingService
from .faiss_storage import FAISSVectorStore
from .metadata import get_all_documents_metadata, get_documents_metadata


class ChatService:
    """Service for handling chat completion with vector search."""
    
    def __init__(self):
        """Initialize the chat service."""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        
        # Validate required environment variables
        if not all([self.api_key, self.endpoint, self.chat_deployment]):
            raise HTTPException(
                status_code=500,
                detail="Missing required Azure OpenAI chat environment variables. Please check .env file."
            )
        
        # Initialize Azure OpenAI client for chat
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
        
        # Initialize embedding service and FAISS storage
        self.embedding_service = AzureOpenAIEmbeddingService()
        self.faiss_store = FAISSVectorStore()
        
        # Config directory for system prompt
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Load default system prompt
        self.default_prompt_path = self.config_dir / "default_system_prompt.txt"
        self._ensure_default_prompt()
    
    def _ensure_default_prompt(self):
        """Ensure default system prompt exists."""
        if not self.default_prompt_path.exists():
            default_prompt = os.getenv(
                "DEFAULT_SYSTEM_PROMPT",
                "You are a helpful AI assistant that answers questions based on the provided PDF documents. "
                "Use the context from the documents to provide accurate and relevant responses. "
                "If the question cannot be answered from the provided context, say so clearly."
            )
            self.default_prompt_path.write_text(default_prompt, encoding='utf-8')
    
    def get_default_system_prompt(self) -> str:
        """Get the current default system prompt."""
        try:
            return self.default_prompt_path.read_text(encoding='utf-8').strip()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read default system prompt: {str(e)}"
            )
    
    def update_default_system_prompt(self, new_prompt: str) -> bool:
        """Update the default system prompt."""
        try:
            self.default_prompt_path.write_text(new_prompt.strip(), encoding='utf-8')
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update default system prompt: {str(e)}"
            )
    
    async def _search_relevant_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant context from the single FAISS index."""
        try:
            # Check if FAISS index exists
            if not self.faiss_store.index_exists():
                return []
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Search the single FAISS index
            distances, indices = self.faiss_store.search_index(query_embedding, top_k)
            
            # Load the index metadata to get chunk information
            _, faiss_metadata = self.faiss_store.load_index()
            chunks = faiss_metadata.get("chunks", [])
            
            # Get documents metadata for additional context
            documents_metadata = get_documents_metadata()
            documents_list = documents_metadata.get("documents", [])
            
            # Create a lookup for document metadata by file_hash
            doc_lookup = {doc["file_hash"]: doc for doc in documents_list}
            
            results = []
            for i, (distance, chunk_idx) in enumerate(zip(distances, indices)):
                if chunk_idx < len(chunks):
                    chunk_info = chunks[chunk_idx]
                    file_hash = chunk_info.get("file_hash", "")
                    
                    # Get document metadata
                    doc_metadata = doc_lookup.get(file_hash, {})
                    
                    results.append({
                        "rank": i + 1,
                        "distance": distance,
                        "chunk_text": chunk_info.get("chunk_text", ""),
                        "chunk_index": chunk_info.get("chunk_index", 0),
                        "document": {
                            "file_hash": file_hash,
                            "original_filename": chunk_info.get("original_filename", ""),
                            "pdf_metadata": doc_metadata.get("pdf_metadata", {}),
                        }
                    })
            
            return results
            
        except Exception as e:
            print(f"Warning: Failed to search FAISS index: {e}")
            return []
    
    def _build_context_prompt(self, query: str, context_results: List[Dict]) -> str:
        """Build context prompt from search results."""
        if not context_results:
            return "No relevant context found in the uploaded documents."
        
        context_parts = ["Based on the following context from uploaded PDF documents:\n"]
        
        for i, result in enumerate(context_results, 1):
            doc_name = result['document']['original_filename']
            chunk_text = result['chunk_text']
            
            context_parts.append(
                f"[Context {i}] From '{doc_name}':\n{chunk_text}\n"
            )
        
        context_parts.append(f"\nUser Question: {query}")
        
        return "\n".join(context_parts)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate chat completion with vector search context.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            system_prompt: Optional custom system prompt
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0 to 1.0)
            
        Returns:
            Dict with response and metadata
        """
        try:
            # Use provided system prompt or default
            if system_prompt is None:
                system_prompt = self.get_default_system_prompt()
            
            # Get the latest user message for context search
            user_messages = [msg for msg in messages if msg.get('role') == 'user']
            if not user_messages:
                raise HTTPException(
                    status_code=400,
                    detail="No user message found in conversation"
                )
            
            latest_query = user_messages[-1]['content']
            
            # Search for relevant context
            context_results = await self._search_relevant_context(latest_query)
            
            # Build enhanced system prompt with context
            if context_results:
                context_prompt = self._build_context_prompt(latest_query, context_results)
                enhanced_system_prompt = f"{system_prompt}\n\n{context_prompt}"
            else:
                enhanced_system_prompt = system_prompt
            
            # Prepare messages for API call
            api_messages = [
                {"role": "system", "content": enhanced_system_prompt}
            ]
            api_messages.extend(messages)
            
            # Generate chat completion
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.chat_deployment,
                    messages=api_messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            return {
                "response": assistant_message,
                "context_used": len(context_results),
                "context_sources": [
                    {
                        "document": result['document']['original_filename'],
                        "chunk_index": result['chunk_index'],
                        "distance": result['distance']
                    }
                    for result in context_results
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate chat completion: {str(e)}"
            )


def get_chat_service():
    """Get the chat service instance, handling initialization errors gracefully."""
    try:
        return ChatService()
    except HTTPException as e:
        print(f"Warning: Chat service not properly configured: {e.detail}")
        return None
    except Exception as e:
        print(f"Warning: Failed to initialize chat service: {str(e)}")
        return None


# Global instance to be used throughout the application
chat_service = get_chat_service()