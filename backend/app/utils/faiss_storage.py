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
    """FAISS vector storage manager for PDF embeddings."""
    
    def __init__(self, storage_dir: str = "faiss"):
        """
        Initialize FAISS vector store.
        
        Args:
            storage_dir: Directory to store FAISS index files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
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
    
    def save_index(self, index: faiss.IndexFlatL2, filename: str, metadata: Dict = None) -> Path:
        """
        Save FAISS index to file with optional metadata.
        
        Args:
            index: FAISS index to save
            filename: Name for the index file (without extension)
            metadata: Optional metadata to save alongside the index
            
        Returns:
            Path: Path to the saved index file
            
        Raises:
            HTTPException: If saving fails
        """
        try:
            # Ensure filename has no extension
            base_filename = Path(filename).stem
            
            # Create file paths
            index_path = self.storage_dir / f"{base_filename}.faiss"
            metadata_path = self.storage_dir / f"{base_filename}_metadata.pkl"
            
            # Save FAISS index
            faiss.write_index(index, str(index_path))
            
            # Save metadata if provided
            if metadata:
                with open(metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)
            
            return index_path
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save FAISS index: {str(e)}"
            )
    
    def load_index(self, filename: str) -> Tuple[faiss.IndexFlatL2, Dict]:
        """
        Load FAISS index from file with metadata.
        
        Args:
            filename: Name of the index file (without extension)
            
        Returns:
            Tuple[faiss.IndexFlatL2, Dict]: The loaded index and metadata
            
        Raises:
            HTTPException: If loading fails
        """
        try:
            # Ensure filename has no extension
            base_filename = Path(filename).stem
            
            # Create file paths
            index_path = self.storage_dir / f"{base_filename}.faiss"
            metadata_path = self.storage_dir / f"{base_filename}_metadata.pkl"
            
            # Check if index file exists
            if not index_path.exists():
                raise FileNotFoundError(f"FAISS index file not found: {index_path}")
            
            # Load FAISS index
            index = faiss.read_index(str(index_path))
            
            # Load metadata if available
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
            
            return index, metadata
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load FAISS index: {str(e)}"
            )
    
    def search_index(self, index: faiss.IndexFlatL2, query_embedding: List[float], k: int = 5) -> Tuple[List[float], List[int]]:
        """
        Search FAISS index for similar embeddings.
        
        Args:
            index: FAISS index to search
            query_embedding: Query embedding vector
            k: Number of nearest neighbors to return
            
        Returns:
            Tuple[List[float], List[int]]: Distances and indices of nearest neighbors
            
        Raises:
            HTTPException: If search fails
        """
        try:
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
    
    def list_indices(self) -> List[str]:
        """
        List all available FAISS index files.
        
        Returns:
            List[str]: List of index filenames (without extension)
        """
        try:
            index_files = list(self.storage_dir.glob("*.faiss"))
            return [f.stem for f in index_files]
            
        except Exception as e:
            print(f"Warning: Failed to list FAISS indices: {str(e)}")
            return []
    
    def delete_index(self, filename: str) -> bool:
        """
        Delete FAISS index and associated metadata.
        
        Args:
            filename: Name of the index file (without extension)
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Ensure filename has no extension
            base_filename = Path(filename).stem
            
            # Create file paths
            index_path = self.storage_dir / f"{base_filename}.faiss"
            metadata_path = self.storage_dir / f"{base_filename}_metadata.pkl"
            
            # Delete files if they exist
            deleted = False
            if index_path.exists():
                index_path.unlink()
                deleted = True
            
            if metadata_path.exists():
                metadata_path.unlink()
            
            return deleted
            
        except Exception as e:
            print(f"Warning: Failed to delete FAISS index {filename}: {str(e)}")
            return False
    
    def get_index_info(self, filename: str) -> Dict:
        """
        Get information about a FAISS index.
        
        Args:
            filename: Name of the index file (without extension)
            
        Returns:
            Dict: Information about the index
        """
        try:
            index, metadata = self.load_index(filename)
            
            return {
                "filename": filename,
                "dimension": index.d,
                "total_vectors": index.ntotal,
                "index_type": type(index).__name__,
                "metadata": metadata,
                "file_size": os.path.getsize(self.storage_dir / f"{filename}.faiss")
            }
            
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e)
            }


# Global instance to be used throughout the application
vector_store = FAISSVectorStore()