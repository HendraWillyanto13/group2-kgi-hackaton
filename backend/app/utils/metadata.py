"""
Metadata management for uploaded files.

This module handles the creation and management of uploads-metadata.json file
that stores information about uploaded files including original filename,
stored filename, upload timestamp, and file size.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import HTTPException

# Path to the metadata files
METADATA_FILE_PATH = Path("uploads-metadata.json")
DOCUMENTS_METADATA_FILE_PATH = Path("metadata") / "documents-metadata.json"

# Ensure metadata directory exists
DOCUMENTS_METADATA_FILE_PATH.parent.mkdir(exist_ok=True)

def get_metadata() -> Dict:
    """
    Read and return the current metadata from the JSON file.
    
    Returns:
        dict: The metadata dictionary, or empty dict if file doesn't exist
    """
    try:
        if METADATA_FILE_PATH.exists():
            with open(METADATA_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"uploads": []}
    except (json.JSONDecodeError, IOError) as e:
        # If there's an error reading the file, create a new empty structure
        return {"uploads": []}

def save_metadata(metadata: Dict) -> None:
    """
    Save the metadata dictionary to the JSON file.
    
    Args:
        metadata: The metadata dictionary to save
    
    Raises:
        HTTPException: If there's an error saving the file
    """
    try:
        with open(METADATA_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Error saving metadata: {str(e)}")

def add_upload_metadata(original_filename: str, stored_filename: str, file_size: int, objects: List[Dict] = None, storage_location: str = "uploads") -> None:
    """
    Add metadata for a newly uploaded file.
    
    Args:
        original_filename: The original name of the uploaded file
        stored_filename: The filename used to store the file (MD5 hash + extension)
        file_size: Size of the file in bytes
        objects: List of detected objects from object detection API (optional)
        storage_location: Directory where the file is stored ("uploads" or "documents")
    """
    metadata = get_metadata()
    
    upload_record = {
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "uploaded_time": datetime.now().isoformat(),
        "file_size": file_size,
        "storage_location": storage_location,
        "objects": objects or []
    }
    
    # Check if this file already exists in metadata (by stored_filename)
    existing_index = None
    for i, record in enumerate(metadata["uploads"]):
        if record["stored_filename"] == stored_filename:
            existing_index = i
            break
    
    if existing_index is not None:
        # Update existing record (in case of overwrite)
        metadata["uploads"][existing_index] = upload_record
    else:
        # Add new record
        metadata["uploads"].append(upload_record)
    
    save_metadata(metadata)

def remove_upload_metadata(stored_filename: str) -> bool:
    """
    Remove metadata for a deleted file.
    
    Args:
        stored_filename: The stored filename to remove from metadata
        
    Returns:
        bool: True if the record was found and removed, False otherwise
    """
    metadata = get_metadata()
    
    # Find and remove the record
    for i, record in enumerate(metadata["uploads"]):
        if record["stored_filename"] == stored_filename:
            del metadata["uploads"][i]
            save_metadata(metadata)
            return True
    
    return False

def get_file_metadata(stored_filename: str) -> Optional[Dict]:
    """
    Get metadata for a specific file.
    
    Args:
        stored_filename: The stored filename to look up
        
    Returns:
        dict or None: The file metadata if found, None otherwise
    """
    metadata = get_metadata()
    
    for record in metadata["uploads"]:
        if record["stored_filename"] == stored_filename:
            return record
    
    return None

def update_objects_metadata(stored_filename: str, objects: List[Dict]) -> bool:
    """
    Update the objects information for a specific file.
    
    Args:
        stored_filename: The stored filename to update
        objects: List of detected objects from object detection API
        
    Returns:
        bool: True if the record was found and updated, False otherwise
    """
    metadata = get_metadata()
    
    # Find and update the record
    for record in metadata["uploads"]:
        if record["stored_filename"] == stored_filename:
            record["objects"] = objects
            save_metadata(metadata)
            return True
    
    return False

def get_all_uploads_metadata() -> List[Dict]:
    """
    Get metadata for all uploaded files.
    
    Returns:
        list: List of all upload metadata records
    """
    metadata = get_metadata()
    return metadata.get("uploads", [])

def get_documents_metadata() -> Dict:
    """
    Read and return the current documents metadata from the JSON file.
    
    Returns:
        dict: The documents metadata dictionary, or empty dict if file doesn't exist
    """
    try:
        if DOCUMENTS_METADATA_FILE_PATH.exists():
            with open(DOCUMENTS_METADATA_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"documents": [], "embeddings_info": {}}
    except (json.JSONDecodeError, IOError) as e:
        # If there's an error reading the file, create a new empty structure
        return {"documents": [], "embeddings_info": {}}

def save_documents_metadata(metadata: Dict) -> None:
    """
    Save the documents metadata dictionary to the JSON file.
    
    Args:
        metadata: The documents metadata dictionary to save
    
    Raises:
        HTTPException: If there's an error saving the file
    """
    try:
        with open(DOCUMENTS_METADATA_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Error saving documents metadata: {str(e)}")

def add_document_metadata(file_hash: str, original_filename: str, stored_filename: str, 
                         pdf_metadata: Dict, content: str, chunks: List[str], 
                         embeddings_info: Dict) -> None:
    """
    Add metadata for a newly processed document.
    
    Args:
        file_hash: MD5 hash of the original file
        original_filename: The original name of the uploaded file
        stored_filename: The filename used to store the file (MD5 hash + extension)
        pdf_metadata: Metadata extracted from PDF
        content: Full extracted text content
        chunks: List of text chunks
        embeddings_info: Information about embeddings generation
    """
    metadata = get_documents_metadata()
    
    document_record = {
        "file_hash": file_hash,
        "original_filename": original_filename,
        "stored_filename": stored_filename,
        "processed_time": datetime.now().isoformat(),
        "pdf_metadata": pdf_metadata,
        "content": content,
        "chunks": chunks,
        "chunk_count": len(chunks),
        "embeddings_info": embeddings_info
    }
    
    # Check if this document already exists in metadata (by file_hash)
    existing_index = None
    for i, record in enumerate(metadata["documents"]):
        if record["file_hash"] == file_hash:
            existing_index = i
            break
    
    if existing_index is not None:
        # Update existing record (in case of reprocessing)
        metadata["documents"][existing_index] = document_record
    else:
        # Add new record
        metadata["documents"].append(document_record)
    
    # Update global embeddings info
    metadata["embeddings_info"] = {
        "last_updated": datetime.now().isoformat(),
        "total_documents": len(metadata["documents"]),
        "total_chunks": sum(doc["chunk_count"] for doc in metadata["documents"]),
        "embedding_model": embeddings_info.get("model", "unknown"),
        "embedding_dimension": embeddings_info.get("dimension", 0)
    }
    
    save_documents_metadata(metadata)

def remove_document_metadata(file_hash: str) -> bool:
    """
    Remove metadata for a deleted document.
    
    Args:
        file_hash: The file hash to remove from metadata
        
    Returns:
        bool: True if the record was found and removed, False otherwise
    """
    metadata = get_documents_metadata()
    
    # Find and remove the record
    for i, record in enumerate(metadata["documents"]):
        if record["file_hash"] == file_hash:
            del metadata["documents"][i]
            
            # Update global embeddings info
            metadata["embeddings_info"] = {
                "last_updated": datetime.now().isoformat(),
                "total_documents": len(metadata["documents"]),
                "total_chunks": sum(doc["chunk_count"] for doc in metadata["documents"]),
                "embedding_model": metadata["embeddings_info"].get("embedding_model", "unknown"),
                "embedding_dimension": metadata["embeddings_info"].get("embedding_dimension", 0)
            }
            
            save_documents_metadata(metadata)
            return True
    
    return False

def get_document_metadata(file_hash: str) -> Optional[Dict]:
    """
    Get metadata for a specific document.
    
    Args:
        file_hash: The file hash to look up
        
    Returns:
        dict or None: The document metadata if found, None otherwise
    """
    metadata = get_documents_metadata()
    
    for record in metadata["documents"]:
        if record["file_hash"] == file_hash:
            return record
    
    return None

def get_all_documents_metadata() -> List[Dict]:
    """
    Get metadata for all processed documents.
    
    Returns:
        list: List of all document metadata records
    """
    metadata = get_documents_metadata()
    return metadata.get("documents", [])