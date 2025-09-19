"""
FAISS vector storage utilities.

This module handles FAISS index creation, management, and storage
for PDF document embeddings.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import faiss
from fastapi import HTTPException


class FAISSVectorStore:
    """FAISS vector storage manager for PDF embeddings with single index."""
    
    def __init__(self, storage_dir: str = "faiss"):
        """
        Initialize FAISS vector store with single index files in faiss directory.
        
        Args:
            storage_dir: Directory to store FAISS index files (default: faiss)
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.index_file = self.storage_dir / "FAISS.index"
        self.metadata_file = self.storage_dir / "FAISS.pkl"
        
    def create_index(self, embeddings: List[List[float]], dimension: int = None) -> faiss.IndexFlatL2:
        """
        Create a new FAISS index from embeddings.
        
        Args:
            embeddings: List of embedding vectors
            dimension: Dimension of embeddings (auto-detected if None)
            
        Returns:
            faiss.IndexFlatL2: The created FAISS index
            
        Raises:
            HTTPException: If index creation fails
        """
        try:
            if not embeddings:
                raise ValueError("No embeddings provided")
            
            # Convert to numpy array
            embedding_array = np.array(embeddings, dtype=np.float32)
            
            # Auto-detect dimension if not provided
            if dimension is None:
                dimension = embedding_array.shape[1]
            
            # Validate dimensions
            if embedding_array.shape[1] != dimension:
                raise ValueError(f"Embedding dimension mismatch: expected {dimension}, got {embedding_array.shape[1]}")
            
            # Create FAISS index (L2 distance)
            index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            index.add(embedding_array)
            
            return index
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create FAISS index: {str(e)}"
            )
    
    def save_index(self, index: faiss.IndexFlatL2, metadata: Dict = None) -> Path:
        """
        Save FAISS index to the single index file with optional metadata.
        
        Args:
            index: FAISS index to save
            metadata: Optional metadata to save alongside the index
            
        Returns:
            Path: Path to the saved index file
            
        Raises:
            HTTPException: If saving fails
        """
        try:
            # Save FAISS index
            faiss.write_index(index, str(self.index_file))
            
            # Save metadata if provided
            if metadata:
                with open(self.metadata_file, 'wb') as f:
                    pickle.dump(metadata, f)
            
            return self.index_file
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save FAISS index: {str(e)}"
            )
    
    def load_index(self) -> Tuple[faiss.IndexFlatL2, Dict]:
        """
        Load FAISS index from the single index file with metadata.
            
        Returns:
            Tuple[faiss.IndexFlatL2, Dict]: The loaded index and metadata
            
        Raises:
            HTTPException: If loading fails
        """
        try:
            # Check if index file exists
            if not self.index_file.exists():
                raise FileNotFoundError(f"FAISS index file not found: {self.index_file}")
            
            # Load FAISS index
            index = faiss.read_index(str(self.index_file))
            
            # Load metadata if available
            metadata = {}
            if self.metadata_file.exists():
                with open(self.metadata_file, 'rb') as f:
                    metadata = pickle.load(f)
            
            return index, metadata
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load FAISS index: {str(e)}"
            )
    
    def add_to_index(self, new_embeddings: List[List[float]], new_metadata: Dict = None) -> faiss.IndexFlatL2:
        """
        Add new embeddings to the existing index or create a new one if none exists.
        
        Args:
            new_embeddings: List of new embedding vectors to add
            new_metadata: New metadata to add or merge with existing
            
        Returns:
            faiss.IndexFlatL2: The updated FAISS index
            
        Raises:
            HTTPException: If adding embeddings fails
        """
        try:
            if not new_embeddings:
                raise ValueError("No new embeddings provided")
            
            new_embedding_array = np.array(new_embeddings, dtype=np.float32)
            dimension = new_embedding_array.shape[1]
            
            # Try to load existing index
            try:
                existing_index, existing_metadata = self.load_index()
                
                # Validate dimensions match
                if existing_index.d != dimension:
                    raise ValueError(f"Embedding dimension mismatch: existing {existing_index.d}, new {dimension}")
                
                # Add new embeddings to existing index
                existing_index.add(new_embedding_array)
                
                # Merge metadata
                if new_metadata:
                    if existing_metadata:
                        # Merge the metadata - you can customize this logic based on your needs
                        for key, value in new_metadata.items():
                            if key in existing_metadata:
                                if isinstance(existing_metadata[key], list) and isinstance(value, list):
                                    existing_metadata[key].extend(value)
                                else:
                                    existing_metadata[key] = value
                            else:
                                existing_metadata[key] = value
                    else:
                        existing_metadata = new_metadata
                
                # Save the updated index
                self.save_index(existing_index, existing_metadata)
                return existing_index
                
            except (FileNotFoundError, HTTPException):
                # No existing index, create a new one
                new_index = self.create_index(new_embeddings, dimension)
                self.save_index(new_index, new_metadata)
                return new_index
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add embeddings to index: {str(e)}"
            )
    
    def search_index(self, query_embedding: List[float], k: int = 5) -> Tuple[List[float], List[int]]:
        """
        Search the FAISS index for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple[List[float], List[int]]: Distances and indices of nearest neighbors
            
        Raises:
            HTTPException: If search fails
        """
        try:
            # Load the index
            index, _ = self.load_index()
            
            # Convert query to numpy array
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search index
            distances, indices = index.search(query_array, k)
            
            return distances[0].tolist(), indices[0].tolist()
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search FAISS index: {str(e)}"
            )
    
    def index_exists(self) -> bool:
        """
        Check if the FAISS index file exists.
        
        Returns:
            bool: True if index exists, False otherwise
        """
        return self.index_file.exists()
    
    def delete_index(self) -> bool:
        """
        Delete the FAISS index and associated metadata.
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            deleted = False
            if self.index_file.exists():
                self.index_file.unlink()
                deleted = True
            
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            
            return deleted
            
        except Exception as e:
            print(f"Warning: Failed to delete FAISS index: {str(e)}")
            return False
    
    def remove_document_embeddings(self, file_hash: str) -> bool:
        """
        Remove embeddings for a specific document by rebuilding the index without that document.
        
        Args:
            file_hash: The file hash of the document to remove
            
        Returns:
            bool: True if removal was successful, False if document not found
        """
        try:
            # Load existing index and metadata
            index, metadata = self.load_index()
            
            if not metadata or "chunks" not in metadata:
                return False
            
            # Find indices of chunks belonging to the document to remove
            chunks_to_keep = []
            indices_to_keep = []
            
            for i, chunk_info in enumerate(metadata["chunks"]):
                if chunk_info.get("file_hash") != file_hash:
                    chunks_to_keep.append(chunk_info)
                    indices_to_keep.append(i)
            
            # If no chunks were found for this document, return False
            if len(chunks_to_keep) == len(metadata["chunks"]):
                return False
            
            # If all chunks belong to the document being deleted, delete the entire index
            if len(chunks_to_keep) == 0:
                self.delete_index()
                return True
            
            # Rebuild the index with remaining embeddings
            # Get all embeddings from the current index
            all_embeddings = np.zeros((index.ntotal, index.d), dtype=np.float32)
            for i in range(index.ntotal):
                all_embeddings[i] = index.reconstruct(i)
            
            # Keep only embeddings for documents we're not deleting
            remaining_embeddings = all_embeddings[indices_to_keep]
            
            # Create new index with remaining embeddings
            new_index = self.create_index(remaining_embeddings.tolist(), index.d)
            
            # Update metadata
            new_metadata = {
                "chunks": chunks_to_keep,
                "total_chunks": len(chunks_to_keep)
            }
            
            # Save the updated index and metadata
            self.save_index(new_index, new_metadata)
            
            return True
            
        except Exception as e:
            print(f"Error removing document embeddings: {str(e)}")
            return False

    def get_index_info(self) -> Dict:
        """
        Get information about the FAISS index.
            
        Returns:
            Dict: Information about the index
        """
        try:
            if not self.index_file.exists():
                return {"error": "Index file does not exist"}
                
            index, metadata = self.load_index()
            
            return {
                "filename": "FAISS.index",
                "dimension": index.d,
                "total_vectors": index.ntotal,
                "index_type": type(index).__name__,
                "metadata": metadata,
                "file_size": os.path.getsize(self.index_file)
            }
            
        except Exception as e:
            return {
                "filename": "FAISS.index",
                "error": str(e)
            }


# Global instance to be used throughout the application
vector_store = FAISSVectorStore()