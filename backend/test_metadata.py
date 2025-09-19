"""
Test script for the metadata functionality.

This script tests the metadata utility functions to ensure they work correctly.
"""

import sys
import json
import os
from pathlib import Path

# Add the app directory to Python path to import modules
sys.path.append(str(Path(__file__).parent / "app"))

from app.utils.metadata import (
    add_upload_metadata, 
    get_metadata, 
    get_file_metadata, 
    get_all_uploads_metadata,
    remove_upload_metadata,
    METADATA_FILE_PATH
)

def test_metadata_functionality():
    """Test the metadata functionality."""
    print("Testing metadata functionality...")
    
    # Clean up any existing metadata file for testing
    if METADATA_FILE_PATH.exists():
        METADATA_FILE_PATH.unlink()
    
    # Test 1: Add metadata for a test file
    print("\n1. Testing add_upload_metadata...")
    add_upload_metadata("test-image.jpg", "abc123.jpg", 1024)
    
    # Verify metadata was created
    metadata = get_metadata()
    print(f"Metadata after adding first file: {json.dumps(metadata, indent=2)}")
    
    # Test 2: Add another file
    print("\n2. Adding second file...")
    add_upload_metadata("another-image.png", "def456.png", 2048)
    
    metadata = get_metadata()
    print(f"Metadata after adding second file: {json.dumps(metadata, indent=2)}")
    
    # Test 3: Get specific file metadata
    print("\n3. Testing get_file_metadata...")
    file_meta = get_file_metadata("abc123.jpg")
    print(f"Metadata for abc123.jpg: {json.dumps(file_meta, indent=2) if file_meta else 'Not found'}")
    
    # Test 4: Get all uploads metadata
    print("\n4. Testing get_all_uploads_metadata...")
    all_uploads = get_all_uploads_metadata()
    print(f"All uploads metadata: {json.dumps(all_uploads, indent=2)}")
    
    # Test 5: Update existing file (same stored filename)
    print("\n5. Testing update of existing file...")
    add_upload_metadata("test-image-updated.jpg", "abc123.jpg", 1536)
    
    metadata = get_metadata()
    print(f"Metadata after updating existing file: {json.dumps(metadata, indent=2)}")
    
    # Test 6: Remove file metadata
    print("\n6. Testing remove_upload_metadata...")
    result = remove_upload_metadata("abc123.jpg")
    print(f"Remove result for abc123.jpg: {result}")
    
    metadata = get_metadata()
    print(f"Metadata after removing abc123.jpg: {json.dumps(metadata, indent=2)}")
    
    # Test 7: Try to remove non-existent file
    print("\n7. Testing remove non-existent file...")
    result = remove_upload_metadata("nonexistent.jpg")
    print(f"Remove result for nonexistent.jpg: {result}")
    
    # Verify final metadata file exists
    print(f"\n8. Final verification - metadata file exists: {METADATA_FILE_PATH.exists()}")
    if METADATA_FILE_PATH.exists():
        with open(METADATA_FILE_PATH, 'r') as f:
            final_content = f.read()
        print(f"Final metadata file content:\n{final_content}")
    
    print("\nMetadata functionality test completed!")

if __name__ == "__main__":
    test_metadata_functionality()