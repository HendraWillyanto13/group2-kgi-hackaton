"""
Test script to upload CONMAS.pdf to the new single FAISS index system.
"""

import requests
import json
from pathlib import Path

# API endpoint
API_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/process-pdf-embeddings"

# Path to the PDF file
PDF_PATH = Path("CONMAS.pdf")

def test_pdf_upload():
    """Test uploading CONMAS.pdf to the API."""
    
    if not PDF_PATH.exists():
        print(f"❌ Error: {PDF_PATH} not found!")
        return False
    
    print(f"📄 Testing upload of {PDF_PATH.name} ({PDF_PATH.stat().st_size} bytes)")
    print(f"🔗 Endpoint: {UPLOAD_ENDPOINT}")
    
    try:
        # Open and upload the file
        with open(PDF_PATH, 'rb') as pdf_file:
            files = {'file': (PDF_PATH.name, pdf_file, 'application/pdf')}
            
            print("⏳ Uploading PDF...")
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=300)  # 5 minute timeout
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📋 Response:")
            print(json.dumps(result, indent=2))
            
            # Check if FAISS index was created
            faiss_path = Path("FAISS.index")
            faiss_pkl_path = Path("FAISS.pkl")
            metadata_path = Path("documents-metadata.json")
            
            print(f"\n📁 Files created:")
            print(f"   FAISS.index: {'✅' if faiss_path.exists() else '❌'} ({faiss_path.stat().st_size if faiss_path.exists() else 0} bytes)")
            print(f"   FAISS.pkl: {'✅' if faiss_pkl_path.exists() else '❌'} ({faiss_pkl_path.stat().st_size if faiss_pkl_path.exists() else 0} bytes)")
            print(f"   documents-metadata.json: {'✅' if metadata_path.exists() else '❌'} ({metadata_path.stat().st_size if metadata_path.exists() else 0} bytes)")
            
            # Show metadata content if it exists
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    print(f"\n📝 Metadata summary:")
                    print(f"   Total documents: {len(metadata.get('documents', []))}")
                    if 'embeddings_info' in metadata:
                        print(f"   Total chunks: {metadata['embeddings_info'].get('total_chunks', 0)}")
                        print(f"   Embedding model: {metadata['embeddings_info'].get('embedding_model', 'unknown')}")
                        print(f"   Embedding dimension: {metadata['embeddings_info'].get('embedding_dimension', 0)}")
                except Exception as e:
                    print(f"   ⚠️ Could not read metadata: {e}")
            
            return True
            
        else:
            print("❌ Upload failed!")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Upload timed out (took more than 5 minutes)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on http://localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Upload failed with error: {e}")
        return False

def test_faiss_index_info():
    """Test getting FAISS index information."""
    
    info_endpoint = f"{API_BASE_URL}/api/faiss-index"
    
    try:
        print(f"\n🔍 Getting FAISS index info from {info_endpoint}")
        response = requests.get(info_endpoint)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Index info retrieved!")
            print(f"📋 Index Info:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to get index info: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting index info: {e}")

def test_processed_pdfs_list():
    """Test listing processed PDFs."""
    
    list_endpoint = f"{API_BASE_URL}/api/processed-pdfs"
    
    try:
        print(f"\n📋 Getting processed PDFs list from {list_endpoint}")
        response = requests.get(list_endpoint)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Processed PDFs list retrieved!")
            print(f"📄 Total processed PDFs: {result.get('total_count', 0)}")
            
            for i, pdf in enumerate(result.get('pdfs', []), 1):
                print(f"   {i}. {pdf.get('original_filename', 'Unknown')} (Hash: {pdf.get('file_hash', 'N/A')[:8]}...)")
                print(f"      Chunks: {pdf.get('chunk_count', 0)}, Processed: {pdf.get('processed_time', 'N/A')}")
        else:
            print(f"❌ Failed to get processed PDFs: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting processed PDFs: {e}")

if __name__ == "__main__":
    print("🚀 Starting CONMAS.pdf upload test...\n")
    
    # Test the upload
    success = test_pdf_upload()
    
    if success:
        # Test additional endpoints
        test_faiss_index_info()
        test_processed_pdfs_list()
        
        print("\n🎉 All tests completed!")
    else:
        print("\n💥 Upload test failed!")