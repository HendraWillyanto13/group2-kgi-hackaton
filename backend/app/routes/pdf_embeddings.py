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
from ..utils.pdf_metadata import pdf_metadata_manager


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
    Save PDF file with hash as filename.
    
    Args:
        file: The uploaded file object
        content: File content bytes
        
    Returns:
        Dict: File information including saved path and hash
    """
    # Calculate MD5 hash
    file_hash = calculate_file_hash(content)
    
    # Create filename with hash + .pdf extension
    hashed_filename = f"{file_hash}.pdf"
    file_path = DOCUMENTS_DIR / hashed_filename
    
    # Check if file already exists
    if file_path.exists():
        return {
            "file_hash": file_hash,
            "saved_filename": hashed_filename,
            "file_path": str(file_path),
            "already_exists": True
        }
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "file_hash": file_hash,
        "saved_filename": hashed_filename,
        "file_path": str(file_path),
        "already_exists": False
    }


async def process_pdf_embeddings(file_info: Dict, original_filename: str) -> Dict:
    """
    Process PDF file to generate embeddings and store in FAISS.
    
    Args:
        file_info: Information about the saved PDF file
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
        # Extract text content from PDF
        content = extract_text_from_pdf(file_path)
        
        # Get PDF metadata
        pdf_metadata = get_pdf_metadata(file_path, content)
        
        # Chunk the text for embeddings
        chunks = chunk_text(content, max_tokens=8000, overlap=200)
        
        # Generate embeddings for all chunks
        embeddings = await embedding_service.generate_embeddings_batch(chunks)
        
        # Create FAISS index
        index = vector_store.create_index(embeddings)
        
        # Save FAISS index
        faiss_filename = f"{file_hash}_embeddings"
        faiss_metadata = {
            "file_hash": file_hash,
            "original_filename": original_filename,
            "chunks": chunks,
            "embedding_count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0
        }
        
        faiss_path = vector_store.save_index(index, faiss_filename, faiss_metadata)
        
        # Create comprehensive metadata
        embedding_info = embedding_service.get_embedding_info()
        metadata = pdf_metadata_manager.create_pdf_metadata(
            file_hash=file_hash,
            original_filename=original_filename,
            stored_filename=file_info["saved_filename"],
            pdf_metadata=pdf_metadata,
            content=content,
            chunks=chunks,
            embeddings_info=embedding_info,
            faiss_filename=faiss_filename
        )
        
        # Save metadata
        metadata_path = pdf_metadata_manager.save_pdf_metadata(file_hash, metadata)
        
        return {
            "content_length": len(content),
            "chunk_count": len(chunks),
            "embedding_count": len(embeddings),
            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
            "faiss_filename": faiss_filename,
            "faiss_path": str(faiss_path),
            "metadata_path": str(metadata_path)
        }
        
    except Exception as e:
        # Clean up on failure
        try:
            vector_store.delete_index(f"{file_hash}_embeddings")
            pdf_metadata_manager.delete_pdf_metadata(file_hash)
        except:
            pass  # Ignore cleanup errors
        
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
                existing_metadata = pdf_metadata_manager.load_pdf_metadata(file_info["file_hash"])
                
                return ProcessPDFResponse(
                    message=f"PDF '{file.filename}' already processed",
                    file_info=file_info,
                    processing_info={
                        "status": "already_exists",
                        "chunk_count": existing_metadata.get("content_info", {}).get("chunk_count", 0),
                        "embedding_count": existing_metadata.get("vector_storage", {}).get("vector_count", 0)
                    },
                    faiss_info={
                        "filename": existing_metadata.get("vector_storage", {}).get("faiss_filename", ""),
                        "path": existing_metadata.get("vector_storage", {}).get("faiss_path", "")
                    },
                    metadata_info={
                        "status": "exists",
                        "upload_date": existing_metadata.get("file_info", {}).get("upload_date", "")
                    }
                )
                
            except HTTPException:
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
                "path": processing_results["metadata_path"]
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
        pdf_metadata_list = pdf_metadata_manager.list_pdf_metadata()
        
        return ListProcessedPDFsResponse(
            pdfs=pdf_metadata_list,
            total_count=len(pdf_metadata_list)
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
        metadata = pdf_metadata_manager.load_pdf_metadata(file_hash)
        
        # Add FAISS index information
        faiss_filename = metadata.get("vector_storage", {}).get("faiss_filename", "")
        if faiss_filename:
            try:
                faiss_info = vector_store.get_index_info(faiss_filename)
                metadata["faiss_index_info"] = faiss_info
            except:
                metadata["faiss_index_info"] = {"error": "Could not load FAISS index info"}
        
        return metadata
        
    except HTTPException as e:
        if "not found" in str(e.detail).lower():
            raise HTTPException(status_code=404, detail=f"Processed PDF not found: {file_hash}")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving PDF details: {str(e)}")


@router.delete("/processed-pdfs/{file_hash}")
async def delete_processed_pdf(file_hash: str):
    """
    Delete a processed PDF and all associated data.
    
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
        # Load metadata to get file information
        try:
            metadata = pdf_metadata_manager.load_pdf_metadata(file_hash)
        except HTTPException as e:
            if "not found" in str(e.detail).lower():
                raise HTTPException(status_code=404, detail=f"Processed PDF not found: {file_hash}")
            raise
        
        # Delete FAISS index
        faiss_filename = metadata.get("vector_storage", {}).get("faiss_filename", "")
        faiss_deleted = False
        if faiss_filename:
            faiss_deleted = vector_store.delete_index(faiss_filename)
        
        # Delete metadata
        metadata_deleted = pdf_metadata_manager.delete_pdf_metadata(file_hash)
        
        # Delete PDF file
        pdf_filename = metadata.get("file_info", {}).get("stored_filename", "")
        pdf_deleted = False
        if pdf_filename:
            pdf_path = DOCUMENTS_DIR / pdf_filename
            if pdf_path.exists():
                pdf_path.unlink()
                pdf_deleted = True
        
        return {
            "message": f"Processed PDF {file_hash} deleted successfully",
            "deleted_components": {
                "pdf_file": pdf_deleted,
                "faiss_index": faiss_deleted,
                "metadata": metadata_deleted
            }
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting processed PDF: {str(e)}")


@router.get("/faiss-indices")
async def list_faiss_indices():
    """
    List all available FAISS index files.
    
    Returns:
        Dict: List of FAISS index files with information
    """
    try:
        indices = vector_store.list_indices()
        index_info = []
        
        for index_name in indices:
            try:
                info = vector_store.get_index_info(index_name)
                index_info.append(info)
            except:
                index_info.append({
                    "filename": index_name,
                    "error": "Could not load index info"
                })
        
        return {
            "indices": index_info,
            "total_count": len(indices)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing FAISS indices: {str(e)}")