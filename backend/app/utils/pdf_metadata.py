"""
PDF metadata management for embeddings.

This module handles the creation, storage, and management of metadata
for PDF documents that have been processed for embeddings.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import HTTPException


class PDFMetadataManager:
    """Manager for PDF metadata storage and retrieval."""
    
    def __init__(self, metadata_dir: str = "metadata"):
        """
        Initialize PDF metadata manager.
        
        Args:
            metadata_dir: Directory to store metadata JSON files
        """
        self.metadata_dir = Path(metadata_dir)
        self.metadata_dir.mkdir(exist_ok=True)
    
    def create_pdf_metadata(self, 
                          file_hash: str,
                          original_filename: str,
                          stored_filename: str,
                          pdf_metadata: Dict,
                          content: str,
                          chunks: List[str],
                          embeddings_info: Dict,
                          faiss_filename: str) -> Dict:
        """
        Create comprehensive metadata for a processed PDF.
        
        Args:
            file_hash: MD5 hash of the original file
            original_filename: Original name of the uploaded file
            stored_filename: Name of the stored file
            pdf_metadata: Metadata extracted from PDF
            content: Full extracted text content
            chunks: List of text chunks
            embeddings_info: Information about embeddings generation
            faiss_filename: Name of the FAISS index file
            
        Returns:
            Dict: Complete metadata dictionary
        """
        metadata = {
            # File information
            "file_info": {
                "file_hash": file_hash,
                "original_filename": original_filename,
                "stored_filename": stored_filename,
                "upload_date": datetime.now().isoformat(),
                "file_size": pdf_metadata.get("file_size", 0),
                "file_path": f"documents/{stored_filename}"
            },
            
            # PDF content information
            "content_info": {
                "page_count": pdf_metadata.get("page_count", 0),
                "content_length": len(content),
                "content_hash": pdf_metadata.get("content_hash", ""),
                "chunk_count": len(chunks),
                "pdf_title": pdf_metadata.get("pdf_title", ""),
                "pdf_author": pdf_metadata.get("pdf_author", ""),
                "pdf_subject": pdf_metadata.get("pdf_subject", ""),
                "pdf_creator": pdf_metadata.get("pdf_creator", "")
            },
            
            # Embedding information
            "embedding_info": {
                "model": embeddings_info.get("model", ""),
                "deployment_name": embeddings_info.get("deployment_name", ""),
                "api_version": embeddings_info.get("api_version", ""),
                "endpoint": embeddings_info.get("endpoint", ""),
                "embedding_dimension": len(chunks) if chunks else 0,
                "processing_date": datetime.now().isoformat()
            },
            
            # FAISS storage information
            "vector_storage": {
                "faiss_filename": faiss_filename,
                "faiss_path": f"faiss/{faiss_filename}.faiss",
                "index_type": "IndexFlatL2",
                "vector_count": len(chunks)
            },
            
            # Processing status
            "processing_status": {
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        return metadata
    
    def save_pdf_metadata(self, file_hash: str, metadata: Dict) -> Path:
        """
        Save PDF metadata to JSON file.
        
        Args:
            file_hash: MD5 hash to use as filename
            metadata: Metadata dictionary to save
            
        Returns:
            Path: Path to the saved metadata file
            
        Raises:
            HTTPException: If saving fails
        """
        try:
            metadata_file = self.metadata_dir / f"{file_hash}_metadata.json"
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return metadata_file
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save PDF metadata: {str(e)}"
            )
    
    def load_pdf_metadata(self, file_hash: str) -> Dict:
        """
        Load PDF metadata from JSON file.
        
        Args:
            file_hash: MD5 hash of the file
            
        Returns:
            Dict: Loaded metadata dictionary
            
        Raises:
            HTTPException: If loading fails
        """
        try:
            metadata_file = self.metadata_dir / f"{file_hash}_metadata.json"
            
            if not metadata_file.exists():
                raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load PDF metadata: {str(e)}"
            )
    
    def list_pdf_metadata(self) -> List[Dict]:
        """
        List all PDF metadata files.
        
        Returns:
            List[Dict]: List of metadata summaries
        """
        try:
            metadata_files = list(self.metadata_dir.glob("*_metadata.json"))
            metadata_list = []
            
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Create summary
                    summary = {
                        "file_hash": metadata.get("file_info", {}).get("file_hash", ""),
                        "original_filename": metadata.get("file_info", {}).get("original_filename", ""),
                        "upload_date": metadata.get("file_info", {}).get("upload_date", ""),
                        "page_count": metadata.get("content_info", {}).get("page_count", 0),
                        "chunk_count": metadata.get("content_info", {}).get("chunk_count", 0),
                        "status": metadata.get("processing_status", {}).get("status", "unknown"),
                        "faiss_filename": metadata.get("vector_storage", {}).get("faiss_filename", "")
                    }
                    
                    metadata_list.append(summary)
                    
                except Exception as e:
                    print(f"Warning: Failed to read metadata file {metadata_file}: {str(e)}")
                    continue
            
            return metadata_list
            
        except Exception as e:
            print(f"Warning: Failed to list PDF metadata: {str(e)}")
            return []
    
    def update_pdf_metadata(self, file_hash: str, updates: Dict) -> Dict:
        """
        Update existing PDF metadata.
        
        Args:
            file_hash: MD5 hash of the file
            updates: Dictionary of updates to apply
            
        Returns:
            Dict: Updated metadata dictionary
            
        Raises:
            HTTPException: If updating fails
        """
        try:
            # Load existing metadata
            metadata = self.load_pdf_metadata(file_hash)
            
            # Apply updates recursively
            def update_nested_dict(original: Dict, updates: Dict) -> Dict:
                for key, value in updates.items():
                    if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                        original[key] = update_nested_dict(original[key], value)
                    else:
                        original[key] = value
                return original
            
            metadata = update_nested_dict(metadata, updates)
            
            # Update timestamp
            metadata["processing_status"]["updated_at"] = datetime.now().isoformat()
            
            # Save updated metadata
            self.save_pdf_metadata(file_hash, metadata)
            
            return metadata
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update PDF metadata: {str(e)}"
            )
    
    def delete_pdf_metadata(self, file_hash: str) -> bool:
        """
        Delete PDF metadata file.
        
        Args:
            file_hash: MD5 hash of the file
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            metadata_file = self.metadata_dir / f"{file_hash}_metadata.json"
            
            if metadata_file.exists():
                metadata_file.unlink()
                return True
            
            return False
            
        except Exception as e:
            print(f"Warning: Failed to delete PDF metadata {file_hash}: {str(e)}")
            return False
    
    def search_metadata(self, query: str, field: str = None) -> List[Dict]:
        """
        Search PDF metadata by content.
        
        Args:
            query: Search query string
            field: Specific field to search in (optional)
            
        Returns:
            List[Dict]: List of matching metadata summaries
        """
        try:
            all_metadata = self.list_pdf_metadata()
            matching_metadata = []
            
            query_lower = query.lower()
            
            for metadata in all_metadata:
                if field:
                    # Search in specific field
                    if field in metadata and query_lower in str(metadata[field]).lower():
                        matching_metadata.append(metadata)
                else:
                    # Search in all fields
                    metadata_str = json.dumps(metadata).lower()
                    if query_lower in metadata_str:
                        matching_metadata.append(metadata)
            
            return matching_metadata
            
        except Exception as e:
            print(f"Warning: Failed to search PDF metadata: {str(e)}")
            return []


# Global instance to be used throughout the application
pdf_metadata_manager = PDFMetadataManager()