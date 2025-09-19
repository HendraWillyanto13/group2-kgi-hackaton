"""
Simple test to create a sample image file for testing upload functionality
"""

from pathlib import Path

def create_test_image():
    """Create a simple test image file"""
    # Create a simple text file as a mock image for testing
    test_content = b"Mock image content for testing metadata functionality"
    
    test_file_path = Path("test_image.jpg")
    with open(test_file_path, "wb") as f:
        f.write(test_content)
    
    print(f"Created test file: {test_file_path}")
    print(f"File size: {len(test_content)} bytes")
    
    return test_file_path

if __name__ == "__main__":
    create_test_image()