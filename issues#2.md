# Issues No 2

### Task 2.1.1 – Implement upload Pdf to document folders

**Prompt:**

> Implement a feature in the backend to allow uploading PDF files. Before accepting a file, compute its hash and check if a file with the same hash already exists. If those kind function is already implemented, use that instead. If a duplicate is detected, reject the upload and notify the user. Uploaded files saved on folder `backend/documents`

**Acceptance Criteria:**

* [x] Users can upload PDF files through the backend.
* [x] The backend computes the hash (e.g., SHA-256) of the uploaded PDF.
* [x] If a file with the same hash already exists, the system rejects the upload with a relevant error message.
* [x] If the file is unique, it is saved successfully.
* [x] Add tests to verify the duplicate detection logic.

---
