"""
PDF processing routes with Azure OpenAI embeddings.

This module provides endpoints for uploading and processing PDF files
to generate embeddings using Azure OpenAI and store them in FAISS indexes.
"""

import hashlib
import os
from pathlib import Path
from typing import List, Dict
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..utils.pdf_processor import extract_text_from_pdf, chunk_text, get_pdf_metadata
from ..utils.azure_openai_service import embedding_service
from ..utils.faiss_storage import vector_store
from ..utils.metadata import (
    add_document_metadata, 
    get_document_metadata, 
    get_all_documents_metadata, 
    remove_document_metadata
)


router = APIRouter()

# Create documents directory if it doesn't exist
DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)


class ProcessPDFResponse(BaseModel):
    """Response model for PDF processing."""
    message: str
    file_info: Dict
    processing_info: Dict
    faiss_info: Dict
    metadata_info: Dict


class ListProcessedPDFsResponse(BaseModel):
    """Response model for listing processed PDFs."""
    pdfs: List[Dict]
    total_count: int


def calculate_file_hash(content: bytes) -> str:
    """Calculate MD5 hash of file content."""
    return hashlib.md5(content).hexdigest()


def save_pdf_file(file: UploadFile, content: bytes) -> Dict:
    """
    Save PDF file with hash as filename to documents directory.
    
    Args:
        file: The uploaded file object
        content: File content bytes
        
    Returns:
        Dict: File information including hash and path
    """
    # Calculate MD5 hash
    file_hash = calculate_file_hash(content)
    
    # Create filename with hash + .pdf extension
    hashed_filename = f"{file_hash}.pdf"
    file_path = DOCUMENTS_DIR / hashed_filename
    
    # Check if file already exists
    already_exists = file_path.exists()
    
    if not already_exists:
        # Save the file
        with open(file_path, "wb") as f:
            f.write(content)
    
    return {
        "file_hash": file_hash,
        "saved_filename": hashed_filename,
        "file_path": str(file_path),
        "file_content": content,
        "already_exists": already_exists
    }


async def process_pdf_embeddings(file_info: Dict, original_filename: str) -> Dict:
    """
    Process PDF file to generate embeddings and store in single FAISS index.
    
    Args:
        file_info: Information about the PDF file
        original_filename: Original name of the uploaded file
        
    Returns:
        Dict: Processing results information
        
    Raises:
        HTTPException: If processing fails
    """
    if embedding_service is None:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI service not properly configured. Please check environment variables."
        )
    
    file_hash = file_info["file_hash"]
    file_path = Path(file_info["file_path"])
    
    try:
        # Extract text content from PDF file
        content = extract_text_from_pdf(file_path)
        pdf_metadata = get_pdf_metadata(file_path, content)
        
        # Chunk the text for embeddings
        chunks = chunk_text(content, max_tokens=8000, overlap=200)
        
        # Generate embeddings for all chunks
        embeddings = await embedding_service.generate_embeddings_batch(chunks)
        
        # Prepare metadata for FAISS index
        chunk_metadata = []
        for i, chunk in enumerate(chunks):
            chunk_metadata.append({
                "file_hash": file_hash,
                "original_filename": original_filename,
                "chunk_index": i,
                "chunk_text": chunk
            })
        
        faiss_metadata = {
            "chunks": chunk_metadata,
            "total_chunks": len(chunks)
        }
        
        # Add embeddings to the single FAISS index
        vector_store.add_to_index(embeddings, faiss_metadata)
        
        # Get embedding info
        embedding_info = embedding_service.get_embedding_info()
        embedding_info["embedding_count"] = len(embeddings)
        embedding_info["dimension"] = len(embeddings[0]) if embeddings else 0
        
        # Add document metadata
        add_document_metadata(
            file_hash=file_hash,
            original_filename=original_filename,
            stored_filename=file_info["saved_filename"],
            pdf_metadata=pdf_metadata,
            content=content,
            chunks=chunks,
            embeddings_info=embedding_info
        )
        
        return {
            "content_length": len(content),
            "chunk_count": len(chunks),
            "embedding_count": len(embeddings),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
            "faiss_filename": "FAISS.index",
            "faiss_path": str(vector_store.index_file),
            "metadata_saved": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF embeddings: {str(e)}"
        )


@router.post("/process-pdf-embeddings", response_model=ProcessPDFResponse)
async def process_pdf_with_embeddings(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Process PDF file to generate embeddings using Azure OpenAI and store in FAISS.
    
    This endpoint:
    1. Accepts a PDF file upload
    2. Extracts text content from the PDF
    3. Chunks the text for optimal embedding generation
    4. Generates embeddings using Azure OpenAI
    5. Creates and stores a FAISS vector index
    6. Saves comprehensive metadata in JSON format
    
    Args:
        file: The uploaded PDF file
        
    Returns:
        ProcessPDFResponse: Processing results and file information
        
    Raises:
        HTTPException:
            - 400: If no file provided or file is not a PDF
            - 500: If processing fails
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No PDF file provided")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Save PDF file
        file_info = save_pdf_file(file, content)
        
        # Check if already processed
        if file_info["already_exists"]:
            try:
                # Try to load existing metadata
                existing_metadata = get_document_metadata(file_info["file_hash"])
                
                if existing_metadata:
                    return ProcessPDFResponse(
                        message=f"PDF '{file.filename}' already processed",
                        file_info=file_info,
                        processing_info={
                            "status": "already_exists",
                            "chunk_count": existing_metadata.get("chunk_count", 0),
                            "embedding_count": existing_metadata.get("embeddings_info", {}).get("embedding_count", 0)
                        },
                        faiss_info={
                            "filename": "FAISS.index",
                            "path": str(vector_store.index_file)
                        },
                        metadata_info={
                            "status": "exists",
                            "upload_date": existing_metadata.get("processed_time", "")
                        }
                    )
                
            except Exception:
                # If metadata doesn't exist, process as new file
                pass
        
        # Process embeddings
        processing_results = await process_pdf_embeddings(file_info, file.filename)
        
        return ProcessPDFResponse(
            message=f"PDF '{file.filename}' processed successfully with embeddings",
            file_info=file_info,
            processing_info={
                "status": "completed",
                "content_length": processing_results["content_length"],
                "chunk_count": processing_results["chunk_count"],
                "embedding_count": processing_results["embedding_count"],
                "embedding_dimension": processing_results["embedding_dimension"]
            },
            faiss_info={
                "filename": processing_results["faiss_filename"],
                "path": processing_results["faiss_path"]
            },
            metadata_info={
                "status": "created",
                "saved": processing_results["metadata_saved"]
            }
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("/processed-pdfs", response_model=ListProcessedPDFsResponse)
async def list_processed_pdfs():
    """
    List all processed PDF files with their metadata.
    
    Returns:
        ListProcessedPDFsResponse: List of processed PDFs with metadata
    """
    try:
        documents_list = get_all_documents_metadata()
        
        return ListProcessedPDFsResponse(
            pdfs=documents_list,
            total_count=len(documents_list)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing processed PDFs: {str(e)}")


@router.get("/processed-pdfs/{file_hash}")
async def get_processed_pdf_details(file_hash: str):
    """
    Get detailed information about a processed PDF.
    
    Args:
        file_hash: MD5 hash of the PDF file
        
    Returns:
        Dict: Detailed metadata for the PDF
        
    Raises:
        HTTPException:
            - 404: If PDF metadata not found
            - 500: If error retrieving metadata
    """
    try:
        metadata = get_document_metadata(file_hash)
        
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Processed PDF not found: {file_hash}")
        
        # Add FAISS index information
        try:
            faiss_info = vector_store.get_index_info()
            metadata["faiss_index_info"] = faiss_info
        except:
            metadata["faiss_index_info"] = {"error": "Could not load FAISS index info"}
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving PDF details: {str(e)}")


@router.delete("/processed-pdfs/{file_hash}")
async def delete_processed_pdf(file_hash: str):
    """
    Delete a processed PDF and all associated data (removes from FAISS index, metadata, and physical file).
    
    Args:
        file_hash: MD5 hash of the PDF file
        
    Returns:
        Dict: Deletion status information
        
    Raises:
        HTTPException:
            - 404: If PDF not found
            - 500: If error during deletion
    """
    try:
        # Check if metadata exists
        metadata = get_document_metadata(file_hash)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Processed PDF not found: {file_hash}")
        
        stored_filename = metadata.get("stored_filename")
        
        # Remove from FAISS index
        faiss_removed = vector_store.remove_document_embeddings(file_hash)
        
        # Delete document metadata
        metadata_deleted = remove_document_metadata(file_hash)
        
        # Delete physical PDF file from documents directory
        file_deleted = False
        if stored_filename:
            pdf_file_path = DOCUMENTS_DIR / stored_filename
            if pdf_file_path.exists():
                try:
                    pdf_file_path.unlink()
                    file_deleted = True
                except Exception as e:
                    print(f"Warning: Failed to delete physical file {stored_filename}: {str(e)}")
        
        # Prepare response
        deleted_components = {
            "metadata": metadata_deleted,
            "faiss_embeddings": faiss_removed,
            "physical_file": file_deleted
        }
        
        # Determine success level
        if metadata_deleted and faiss_removed:
            message = f"Processed PDF {file_hash} completely deleted successfully"
            if not file_deleted:
                message += " (warning: physical file could not be deleted)"
        elif metadata_deleted:
            message = f"Processed PDF {file_hash} metadata deleted successfully (warning: FAISS embeddings could not be removed)"
        else:
            message = f"Failed to delete processed PDF {file_hash}"
            
        return {
            "message": message,
            "file_hash": file_hash,
            "stored_filename": stored_filename,
            "deleted_components": deleted_components,
            "success": metadata_deleted or faiss_removed or file_deleted
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting processed PDF: {str(e)}")


@router.get("/faiss-index")
async def get_faiss_index_info():
    """
    Get information about the single FAISS index.
    
    Returns:
        Dict: FAISS index information
    """
    try:
        if not vector_store.index_exists():
            return {
                "message": "No FAISS index found",
                "exists": False
            }
        
        index_info = vector_store.get_index_info()
        index_info["exists"] = True
        
        return index_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting FAISS index info: {str(e)}")