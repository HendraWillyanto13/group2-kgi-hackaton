# Issues No 3

### Task 3.1.1 – Implement PDF Processing with Azure OpenAI Embeddings

**Prompt:**

> Develop a backend feature that processes uploaded PDF files to generate embeddings using Azure OpenAI, saves a local FAISS vector index file on folder `backend/faiss`, and creates associated metadata in JSON format save in folder `backend/metadata`. All necessary Azure OpenAI configuration variables should be saved in the .env file.

**Acceptance Criteria:**

* [ ] Accept uploaded PDF files and extract content for embedding.
* [ ] Use Azure OpenAI to generate embeddings from the PDF content.
* [ ] Store the resulting embeddings in a local FAISS file.
* [ ] Create and store metadata for each PDF in a corresponding JSON file.
* [ ] Save all required Azure OpenAI variables (e.g., API key, endpoint, deployment name) in the .env file.
* [ ] Unit tests cover embedding pipeline, FAISS file creation, and metadata export.

**Notes:**

* The solution should be efficient for handling multiple and large PDF files.
* Ensure metadata includes file name, upload date, hash, and embedding details.
* Document the environment variables needed for Azure OpenAI integration.

---