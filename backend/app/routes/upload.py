from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
from pydantic import BaseModel
import hashlib
import os
from pathlib import Path
import shutil
from ..utils.metadata import add_upload_metadata, remove_upload_metadata, get_all_uploads_metadata, update_objects_metadata

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class DeleteFilesRequest(BaseModel):
    filenames: List[str]

class UpdateObjectsRequest(BaseModel):
    stored_filename: str
    objects: List[dict]

def calculate_md5(content: bytes) -> str:
    """Calculate MD5 hash of file content."""
    return hashlib.md5(content).hexdigest()

def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower()

async def save_file(file: UploadFile, content: bytes) -> dict:
    """
    Save file with MD5 hash as filename and return file info.
    
    Args:
        file: The uploaded file object
        content: File content bytes
    
    Returns:
        dict: File information including saved path and hash
    """
    # Calculate MD5 hash
    file_hash = calculate_md5(content)
    
    # Get file extension
    file_extension = get_file_extension(file.filename)
    
    # Create filename with MD5 hash + extension
    hashed_filename = f"{file_hash}{file_extension}"
    file_path = UPLOAD_DIR / hashed_filename
    
    # Check if file already exists (deduplication)
    file_exists = file_path.exists()
    
    # Save file (will overwrite if exists)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Add metadata for the uploaded file
    add_upload_metadata(
        original_filename=file.filename,
        stored_filename=hashed_filename,
        file_size=len(content)
    )
    
    return {
        "original_filename": file.filename,
        "saved_filename": hashed_filename,
        "file_path": str(file_path),
        "file_hash": file_hash,
        "size": len(content),
        "content_type": file.content_type,
        "was_duplicate": file_exists
    }

@router.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    """
    File upload endpoint that accepts single or multiple files, saves them with MD5 hash filenames,
    and returns file information. Supports both single file and files[] format from multipart/form-data.
    
    Files are saved in the 'uploads' directory with MD5 hash as filename to prevent duplicates.
    If a file with the same content already exists, it will be overwritten.
    
    Args:
        files: The uploaded file(s) (multipart/form-data)
    
    Returns:
        dict: A dictionary containing file information including saved paths and hashes
    
    Raises:
        HTTPException: If no files are provided or there's an error processing them
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    uploaded_files = []
    total_size = 0
    duplicates_count = 0

    try:
        for file in files:
            if not file.filename:
                continue  # Skip files without filenames
            
            # Read the file content
            content = await file.read()
            file_size = len(content)
            total_size += file_size
            
            # Save file with MD5 hash filename
            file_info = await save_file(file, content)
            uploaded_files.append(file_info)
            
            if file_info["was_duplicate"]:
                duplicates_count += 1
            
            # Reset file pointer if needed for further processing
            await file.seek(0)
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No valid files were uploaded")
        
        return {
            "files": uploaded_files,
            "total_files": len(uploaded_files),
            "total_size": total_size,
            "duplicates_count": duplicates_count,
            "upload_directory": str(UPLOAD_DIR),
            "message": f"Successfully uploaded {len(uploaded_files)} file{'s' if len(uploaded_files) > 1 else ''}" +
                      (f" ({duplicates_count} duplicate{'s' if duplicates_count > 1 else ''} overwritten)" if duplicates_count > 0 else "")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@router.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Multiple file upload endpoint that accepts multiple files and saves them with MD5 hash filenames.
    
    This endpoint provides the same functionality as /upload but with a different route name.
    Files are saved with MD5 hash to prevent duplicates and enable deduplication.
    
    Args:
        files: List of uploaded files (multipart/form-data)
    
    Returns:
        dict: A dictionary containing information about all uploaded files
    
    Raises:
        HTTPException: If no files are provided or there's an error processing them
    """
    # Reuse the main upload function logic
    return await upload_file(files)

@router.get("/uploads")
async def list_uploaded_files():
    """
    List all uploaded files in the uploads directory.
    
    Returns:
        dict: List of uploaded files with their information
    """
    try:
        if not UPLOAD_DIR.exists():
            return {
                "files": [],
                "total_files": 0,
                "upload_directory": str(UPLOAD_DIR),
                "message": "No uploads directory found"
            }
        
        files = []
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime
                })
        
        return {
            "files": files,
            "total_files": len(files),
            "upload_directory": str(UPLOAD_DIR),
            "message": f"Found {len(files)} uploaded file{'s' if len(files) != 1 else ''}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.get("/uploads/metadata")
async def get_uploads_metadata():
    """
    Get metadata for all uploaded files from the uploads-metadata.json file.
    
    Returns:
        dict: List of uploaded files with their metadata including original filename,
              stored filename, upload time, and file size
    """
    try:
        metadata_records = get_all_uploads_metadata()
        
        return {
            "uploads": metadata_records,
            "total_uploads": len(metadata_records),
            "message": f"Found metadata for {len(metadata_records)} uploaded file{'s' if len(metadata_records) != 1 else ''}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving metadata: {str(e)}")

@router.put("/uploads/metadata/objects")
async def update_upload_objects_metadata(request: UpdateObjectsRequest):
    """
    Update the objects detection information for a specific uploaded file.
    
    Args:
        request: Request body containing stored filename and objects list
        
    Returns:
        dict: Success or error message
    """
    try:
        success = update_objects_metadata(request.stored_filename, request.objects)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully updated objects metadata for {request.stored_filename}"
            }
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"File not found in metadata: {request.stored_filename}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating objects metadata: {str(e)}")

@router.delete("/uploads")
async def delete_files(request: DeleteFilesRequest):
    """
    Delete multiple uploaded files from the uploads directory.
    
    Args:
        request: Request body containing list of filenames to delete
    
    Returns:
        dict: Result of deletion operation
    
    Raises:
        HTTPException: If files are not found or there's an error deleting them
    """
    try:
        if not UPLOAD_DIR.exists():
            raise HTTPException(status_code=404, detail="Uploads directory not found")
        
        deleted_files = []
        not_found_files = []
        errors = []
        
        for filename in request.filenames:
            file_path = UPLOAD_DIR / filename
            
            if not file_path.exists():
                not_found_files.append(filename)
                continue
            
            if not file_path.is_file():
                errors.append(f"{filename} is not a file")
                continue
            
            try:
                os.remove(file_path)
                deleted_files.append(filename)
                # Remove metadata for the deleted file
                remove_upload_metadata(filename)
            except Exception as e:
                errors.append(f"Error deleting {filename}: {str(e)}")
        
        # Build response message
        messages = []
        if deleted_files:
            messages.append(f"Successfully deleted {len(deleted_files)} file{'s' if len(deleted_files) != 1 else ''}")
        if not_found_files:
            messages.append(f"{len(not_found_files)} file{'s' if len(not_found_files) != 1 else ''} not found")
        if errors:
            messages.append(f"{len(errors)} error{'s' if len(errors) != 1 else ''} occurred")
        
        # If there were errors but some files were deleted, return 207 (Multi-Status)
        status_code = 200
        if errors and deleted_files:
            status_code = 207  # Multi-Status
        elif errors and not deleted_files:
            status_code = 400  # Bad Request if nothing was deleted
        elif not_found_files and not deleted_files:
            status_code = 404  # Not Found if no files were found
        
        response = {
            "deleted_files": deleted_files,
            "not_found_files": not_found_files,
            "errors": errors,
            "total_requested": len(request.filenames),
            "total_deleted": len(deleted_files),
            "message": "; ".join(messages) if messages else "No files to delete"
        }
        
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=response)
        
        return response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting files: {str(e)}")

# Create documents directory if it doesn't exist
DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)

def is_pdf_file(filename: str) -> bool:
    """Check if the file is a PDF based on file extension."""
    return get_file_extension(filename) == ".pdf"

def validate_pdf_content(content: bytes) -> bool:
    """Validate PDF content by checking PDF signature."""
    # PDF files start with %PDF- signature
    return content.startswith(b'%PDF-')

async def save_pdf_file(file: UploadFile, content: bytes) -> dict:
    """
    Save PDF file with MD5 hash as filename and return file info.
    
    Args:
        file: The uploaded file object
        content: File content bytes
    
    Returns:
        dict: File information including saved path and hash
    
    Raises:
        HTTPException: If file is not a valid PDF
    """
    # Validate file extension
    if not is_pdf_file(file.filename):
        raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF file")
    
    # Validate PDF content
    if not validate_pdf_content(content):
        raise HTTPException(status_code=400, detail=f"File {file.filename} does not contain valid PDF content")
    
    # Calculate MD5 hash
    file_hash = calculate_md5(content)
    
    # Create filename with MD5 hash + .pdf extension
    hashed_filename = f"{file_hash}.pdf"
    file_path = DOCUMENTS_DIR / hashed_filename
    
    # Check if file already exists (duplicate detection)
    file_exists = file_path.exists()
    
    if file_exists:
        # File with same hash already exists, reject the upload
        raise HTTPException(
            status_code=409, 
            detail=f"A PDF file with the same content already exists (hash: {file_hash})"
        )
    
    # Save file to documents directory
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    return {
        "original_filename": file.filename,
        "saved_filename": hashed_filename,
        "file_path": str(file_path),
        "file_hash": file_hash,
        "size": len(content),
        "content_type": file.content_type,
        "storage_location": "documents"
    }

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    PDF file upload endpoint that accepts a single PDF file.
    
    Before accepting the file, computes SHA-256 hash and checks if a file with 
    the same hash already exists. If a duplicate is detected, rejects the upload 
    and notifies the user. Uploaded files are saved in the 'documents' folder.
    
    Args:
        file: The uploaded PDF file (multipart/form-data)
    
    Returns:
        dict: File information including saved path and hash
    
    Raises:
        HTTPException: 
            - 400: If no file provided, file is not PDF, or invalid PDF content
            - 409: If duplicate file detected (same hash exists)
            - 500: If error processing file
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No PDF file provided")
    
    try:
        # Read the file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Save PDF file with duplicate detection
        file_info = await save_pdf_file(file, content)
        
        # Add metadata for the uploaded PDF
        add_upload_metadata(
            original_filename=file.filename,
            stored_filename=file_info["saved_filename"],
            file_size=len(content),
            storage_location="documents"
        )
        
        return {
            "file": file_info,
            "message": f"PDF file '{file.filename}' uploaded successfully",
            "upload_directory": str(DOCUMENTS_DIR)
        }
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

@router.post("/upload-pdfs")
async def upload_multiple_pdfs(files: List[UploadFile] = File(...)):
    """
    Multiple PDF file upload endpoint that accepts multiple PDF files.
    
    Each file is validated and checked for duplicates before being saved.
    If any file is a duplicate, the entire upload is rejected.
    
    Args:
        files: List of uploaded PDF files (multipart/form-data)
    
    Returns:
        dict: Information about all uploaded PDF files
    
    Raises:
        HTTPException: If any file validation fails or duplicates detected
    """
    if not files:
        raise HTTPException(status_code=400, detail="No PDF files provided")
    
    uploaded_files = []
    total_size = 0
    
    try:
        # First pass: validate all files and check for duplicates
        file_contents = []
        for file in files:
            if not file.filename:
                continue
            
            # Read content
            content = await file.read()
            file_contents.append((file, content))
            
            # Validate file extension
            if not is_pdf_file(file.filename):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF file")
            
            # Validate PDF content
            if not validate_pdf_content(content):
                raise HTTPException(status_code=400, detail=f"File {file.filename} does not contain valid PDF content")
            
            # Check for duplicate
            file_hash = calculate_md5(content)
            hashed_filename = f"{file_hash}.pdf"
            file_path = DOCUMENTS_DIR / hashed_filename
            
            if file_path.exists():
                raise HTTPException(
                    status_code=409,
                    detail=f"PDF file '{file.filename}' already exists (hash: {file_hash})"
                )
        
        # Second pass: save all files (only if all validations passed)
        for file, content in file_contents:
            file_info = await save_pdf_file(file, content)
            uploaded_files.append(file_info)
            total_size += len(content)
            
            # Add metadata
            add_upload_metadata(
                original_filename=file.filename,
                stored_filename=file_info["saved_filename"],
                file_size=len(content),
                storage_location="documents"
            )
        
        if not uploaded_files:
            raise HTTPException(status_code=400, detail="No valid PDF files were uploaded")
        
        return {
            "files": uploaded_files,
            "total_files": len(uploaded_files),
            "total_size": total_size,
            "upload_directory": str(DOCUMENTS_DIR),
            "message": f"Successfully uploaded {len(uploaded_files)} PDF file{'s' if len(uploaded_files) > 1 else ''}"
        }
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF files: {str(e)}")

@router.get("/documents")
async def get_documents():
    """
    Get a list of all uploaded PDF documents.
    
    Returns:
        dict: List of PDF documents with their metadata
    """
    try:
        all_uploads = get_all_uploads_metadata()
        
        # Filter only documents (PDFs stored in documents folder)
        documents = [
            upload for upload in all_uploads 
            if upload.get("storage_location") == "documents"
        ]
        
        return {
            "documents": documents,
            "total_documents": len(documents),
            "storage_directory": str(DOCUMENTS_DIR)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")