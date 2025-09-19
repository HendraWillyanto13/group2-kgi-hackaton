"""
PDF content extraction utilities.

This module handles PDF file processing and text extraction
for embedding generation purposes.
"""

import os
import hashlib
import tiktoken
from typing import List, Dict, Optional
from pathlib import Path
from PyPDF2 import PdfReader
from fastapi import HTTPException


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text content from the PDF
        
    Raises:
        HTTPException: If PDF cannot be read or processed
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
                    text += "\n"
            except Exception as e:
                print(f"Warning: Could not extract text from page {page_num + 1}: {str(e)}")
                continue
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content could be extracted from PDF")
            
        return text.strip()
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")


def chunk_text(text: str, max_tokens: int = 8000, overlap: int = 200) -> List[str]:
    """
    Split text into chunks suitable for embedding generation.
    
    Args:
        text: The input text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    try:
        # Use tiktoken to count tokens (assuming gpt-3.5-turbo encoding)
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        
        if len(tokens) <= max_tokens:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            # Calculate end position
            end = min(start + max_tokens, len(tokens))
            
            # Get chunk tokens
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append(chunk_text.strip())
            
            # Move start position with overlap
            if end >= len(tokens):
                break
            start = end - overlap
            
        return chunks
        
    except Exception as e:
        # Fallback to simple character-based chunking if tiktoken fails
        print(f"Warning: Token-based chunking failed, falling back to character-based: {str(e)}")
        
        # Rough estimation: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        overlap_chars = overlap * 4
        
        if len(text) <= max_chars:
            return [text]
            
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + max_chars, len(text))
            chunks.append(text[start:end].strip())
            
            if end >= len(text):
                break
            start = end - overlap_chars
            
        return chunks


def calculate_content_hash(content: str) -> str:
    """
    Calculate MD5 hash of text content.
    
    Args:
        content: Text content to hash
        
    Returns:
        str: MD5 hash of the content
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def get_pdf_metadata(file_path: Path, content: str) -> Dict:
    """
    Extract metadata from PDF file and content.
    
    Args:
        file_path: Path to the PDF file
        content: Extracted text content
        
    Returns:
        Dict: Metadata information about the PDF
    """
    try:
        reader = PdfReader(file_path)
        file_stat = os.stat(file_path)
        
        # Try to get PDF metadata
        pdf_info = reader.metadata if reader.metadata else {}
        
        metadata = {
            "file_name": file_path.name,
            "file_size": file_stat.st_size,
            "page_count": len(reader.pages),
            "content_hash": calculate_content_hash(content),
            "content_length": len(content),
            "pdf_title": pdf_info.get("/Title", "") if pdf_info else "",
            "pdf_author": pdf_info.get("/Author", "") if pdf_info else "",
            "pdf_subject": pdf_info.get("/Subject", "") if pdf_info else "",
            "pdf_creator": pdf_info.get("/Creator", "") if pdf_info else "",
        }
        
        return metadata
        
    except Exception as e:
        print(f"Warning: Could not extract PDF metadata: {str(e)}")
        return {
            "file_name": file_path.name,
            "file_size": os.stat(file_path).st_size,
            "page_count": 0,
            "content_hash": calculate_content_hash(content),
            "content_length": len(content),
            "pdf_title": "",
            "pdf_author": "",
            "pdf_subject": "",
            "pdf_creator": "",
        }