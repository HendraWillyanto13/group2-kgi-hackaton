"""
Test suite for PDF upload functionality.

This module tests the PDF upload endpoint including:
- PDF file validation
- Duplicate detection using MD5 hash
- Successful upload scenarios
- Error handling
"""

import pytest
import httpx
import os
import hashlib
from pathlib import Path
import json
from fastapi.testclient import TestClient
from app.main import app

# Test client for FastAPI app
client = TestClient(app)

# Test directories
DOCUMENTS_DIR = Path("documents")
METADATA_FILE = Path("uploads-metadata.json")

# Sample PDF content (minimal valid PDF)
SAMPLE_PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
190
%%EOF"""

# Another sample PDF with different content
SAMPLE_PDF_CONTENT_2 = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
72 720 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000130 00000 n 
0000000189 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
280
%%EOF"""

# Invalid PDF content (not starting with %PDF-)
INVALID_PDF_CONTENT = b"This is not a PDF file content"

class TestPDFUpload:
    """Test class for PDF upload functionality."""
    
    def setup_method(self):
        """Setup method run before each test."""
        # Ensure documents directory exists
        DOCUMENTS_DIR.mkdir(exist_ok=True)
        
        # Clean up any existing test files
        self.cleanup_test_files()
        
        # Clean up metadata
        if METADATA_FILE.exists():
            METADATA_FILE.unlink()
    
    def teardown_method(self):
        """Cleanup method run after each test."""
        self.cleanup_test_files()
        
        # Clean up metadata
        if METADATA_FILE.exists():
            METADATA_FILE.unlink()
    
    def cleanup_test_files(self):
        """Remove any test PDF files from documents directory."""
        if DOCUMENTS_DIR.exists():
            for file in DOCUMENTS_DIR.glob("*.pdf"):
                try:
                    file.unlink()
                except OSError:
                    pass
    
    def calculate_md5(self, content: bytes) -> str:
        """Calculate MD5 hash of content."""
        return hashlib.md5(content).hexdigest()
    
    def test_successful_pdf_upload(self):
        """Test successful upload of a valid PDF file."""
        files = {"file": ("test.pdf", SAMPLE_PDF_CONTENT, "application/pdf")}
        
        response = client.post("/api/upload-pdf", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "file" in data
        assert "message" in data
        assert "upload_directory" in data
        
        # Check file info
        file_info = data["file"]
        assert file_info["original_filename"] == "test.pdf"
        assert file_info["saved_filename"].endswith(".pdf")
        assert file_info["size"] == len(SAMPLE_PDF_CONTENT)
        assert file_info["storage_location"] == "documents"
        assert "file_hash" in file_info
        
        # Check file was actually saved
        saved_file = DOCUMENTS_DIR / file_info["saved_filename"]
        assert saved_file.exists()
        
        # Verify file content
        with open(saved_file, "rb") as f:
            saved_content = f.read()
        assert saved_content == SAMPLE_PDF_CONTENT
        
        # Check metadata was created
        assert METADATA_FILE.exists()
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
        
        assert len(metadata["uploads"]) == 1
        upload_record = metadata["uploads"][0]
        assert upload_record["original_filename"] == "test.pdf"
        assert upload_record["storage_location"] == "documents"
    
    def test_duplicate_pdf_rejection(self):
        """Test that duplicate PDF files are rejected."""
        files = {"file": ("test.pdf", SAMPLE_PDF_CONTENT, "application/pdf")}
        
        # First upload should succeed
        response1 = client.post("/api/upload-pdf", files=files)
        assert response1.status_code == 200
        
        # Second upload of same content should be rejected
        files2 = {"file": ("different_name.pdf", SAMPLE_PDF_CONTENT, "application/pdf")}
        response2 = client.post("/api/upload-pdf", files=files2)
        
        assert response2.status_code == 409
        data = response2.json()
        assert "same content already exists" in data["detail"].lower()
        
        # Check that only one file exists in documents directory
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        assert len(pdf_files) == 1
    
    def test_different_pdf_files_upload(self):
        """Test that different PDF files can be uploaded successfully."""
        files1 = {"file": ("test1.pdf", SAMPLE_PDF_CONTENT, "application/pdf")}
        files2 = {"file": ("test2.pdf", SAMPLE_PDF_CONTENT_2, "application/pdf")}
        
        # Upload first PDF
        response1 = client.post("/api/upload-pdf", files=files1)
        assert response1.status_code == 200
        
        # Upload second PDF with different content
        response2 = client.post("/api/upload-pdf", files=files2)
        assert response2.status_code == 200
        
        # Check that both files exist
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        assert len(pdf_files) == 2
        
        # Verify different hashes
        hash1 = self.calculate_md5(SAMPLE_PDF_CONTENT)
        hash2 = self.calculate_md5(SAMPLE_PDF_CONTENT_2)
        assert hash1 != hash2
    
    def test_invalid_file_extension(self):
        """Test rejection of files with non-PDF extensions."""
        files = {"file": ("test.txt", SAMPLE_PDF_CONTENT, "text/plain")}
        
        response = client.post("/api/upload-pdf", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "not a pdf file" in data["detail"].lower()
        
        # Check no file was saved
        pdf_files = list(DOCUMENTS_DIR.glob("*.*"))
        assert len(pdf_files) == 0
    
    def test_invalid_pdf_content(self):
        """Test rejection of files with invalid PDF content."""
        files = {"file": ("test.pdf", INVALID_PDF_CONTENT, "application/pdf")}
        
        response = client.post("/api/upload-pdf", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "does not contain valid pdf content" in data["detail"].lower()
        
        # Check no file was saved
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        assert len(pdf_files) == 0
    
    def test_empty_file_rejection(self):
        """Test rejection of empty files."""
        files = {"file": ("test.pdf", b"", "application/pdf")}
        
        response = client.post("/api/upload-pdf", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "empty" in data["detail"].lower()
    
    def test_no_file_provided(self):
        """Test error when no file is provided."""
        response = client.post("/api/upload-pdf")
        
        assert response.status_code == 422  # Unprocessable Entity (missing required field)
    
    def test_multiple_pdf_upload_success(self):
        """Test successful upload of multiple different PDF files."""
        files = [
            ("files", ("test1.pdf", SAMPLE_PDF_CONTENT, "application/pdf")),
            ("files", ("test2.pdf", SAMPLE_PDF_CONTENT_2, "application/pdf"))
        ]
        
        response = client.post("/api/upload-pdfs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "files" in data
        assert "total_files" in data
        assert "total_size" in data
        assert data["total_files"] == 2
        
        # Check both files were saved
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        assert len(pdf_files) == 2
        
        # Check metadata
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
        assert len(metadata["uploads"]) == 2
    
    def test_multiple_pdf_upload_with_duplicate(self):
        """Test that multiple PDF upload is rejected if any file is duplicate."""
        # First upload one PDF
        files1 = {"file": ("existing.pdf", SAMPLE_PDF_CONTENT, "application/pdf")}
        response1 = client.post("/api/upload-pdf", files=files1)
        assert response1.status_code == 200
        
        # Try to upload multiple files including the duplicate
        files = [
            ("files", ("new.pdf", SAMPLE_PDF_CONTENT_2, "application/pdf")),
            ("files", ("duplicate.pdf", SAMPLE_PDF_CONTENT, "application/pdf"))  # This is duplicate
        ]
        
        response = client.post("/api/upload-pdfs", files=files)
        
        assert response.status_code == 409
        data = response.json()
        assert "already exists" in data["detail"].lower()
        
        # Check that only the original file exists (no new files were saved)
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        assert len(pdf_files) == 1
    
    def test_multiple_pdf_upload_invalid_file(self):
        """Test that multiple PDF upload is rejected if any file is invalid."""
        files = [
            ("files", ("valid.pdf", SAMPLE_PDF_CONTENT, "application/pdf")),
            ("files", ("invalid.txt", SAMPLE_PDF_CONTENT_2, "text/plain"))  # Wrong extension
        ]
        
        response = client.post("/api/upload-pdfs", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "not a pdf file" in data["detail"].lower()
        
        # Check that no files were saved
        pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
        assert len(pdf_files) == 0
    
    def test_pdf_hash_calculation(self):
        """Test that PDF files are hashed correctly for duplicate detection."""
        files = {"file": ("test.pdf", SAMPLE_PDF_CONTENT, "application/pdf")}
        
        response = client.post("/api/upload-pdf", files=files)
        assert response.status_code == 200
        
        data = response.json()
        returned_hash = data["file"]["file_hash"]
        expected_hash = self.calculate_md5(SAMPLE_PDF_CONTENT)
        
        assert returned_hash == expected_hash
        
        # Check that file is saved with hash as filename
        expected_filename = f"{expected_hash}.pdf"
        saved_file = DOCUMENTS_DIR / expected_filename
        assert saved_file.exists()
        assert data["file"]["saved_filename"] == expected_filename

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
