# Issues Clean Page

### Task 1.1 - Clean Pages

**Prompt:**

> Please remove UI Progress Component, Input Component, and Button Variants. and replace to button Upload Document, Ask, and Manage Source.

**Acceptance Criteria:**
[ ]
[ ] 
[ ] 

---




# Issues No 1

### Task 1.1.1 - Document Handling

**Prompt:**

> Create new pages `ManageSource.jsx` in pages folder frontend to show all uploaded files in folder `backend\documents` as list with header name, datetime, size, and hyperlink to preview document with open new tab and capability to delete multiple selected documents with confirmation before delete and in delete function call `api/processed-pdfs/{document_id}`. On success: toast "Delete Successfully" with green checklist icon and Failed: toast "Delete Failed" with red X icon. Add function filter by datetime, name, size in `ManageSource.jsx` above the list document. Add ascending descending function for each header list. Documentation is updated accordingly and Also navigate button Manage Source from `app.jsx` to `ManageSource.jsx` vice versa. 

**Acceptance Criteria:**
[ ] User can view all documents in a list.
[ ] User can select and delete multiple documents at once.
[ ] Documentation is updated accordingly.

---

### Task 1.1.2 - Show List Document

**Prompt:**

> Implement pages `ManageSource.jsx` call GET `/api/document` and place data based on table header. 

**Acceptance Criteria:**
[ ] 
[ ] 
[ ] 

---

### Task 1.1.3 - Upload Document

**Prompt:**


> Create new pages `UploadDocument.jsx` in pages folder frontend to build a file upload page. Allow selecting only one file at a time and accept only .pdf or .txt extensions. Use an <input type="file"> with proper accept attribute and multiple={false}. Display a progress bar while the file is uploading. Use a toast or alert() to notify the user whether the upload was successful or failed. uploadFile(file, onProgress)  function call `api/upload-pdfs/`, which POSTs the file. Use onUploadProgress to report progress (0–100) via the callback

**Objective**
Create a file upload interface with progress feedback and notification


**Acceptance Criteria**

* [ ] File input only accepts one file with .pdf or .txt.
* [ ] Progress bar updates smoothly during upload.
* [ ] Notification clearly shows success or failure after upload


### Task 1.1.4 – Create a chatbot AI page

**What it does:** Create a chatbot UI that allows users to type any question. The chatbot should generate answers based on the entire previous conversation (historical context). Display each answer immediately above its corresponding question, maintaining chronological order. Differentiate clearly between questions and answers in the UI

**Prompt:**

> Create new pages `ChatAsk.jsx` in pages folder frontend to implement a chatbot UI. Add a text input field and submit button to allow users to type and send questions. Store the conversation history in a reactive array of message objects { role: "user" | "bot", content: string }.

When the user submits a question, append it to the conversation history. Then call generateReply(messages) from src/lib/api.js, passing the full message history including the new question. Append the bot's reply to the history once received.

In the UI, render the messages in chronological order (top to bottom). For each user message, display the corresponding bot reply immediately below it. Use visual styling (e.g., colors or alignment) to clearly differentiate between user questions and bot answers.

Ensure the input is cleared after submission and auto-scrolls to the latest message.

**Objective**
Implement a conversational interface that preserves context and shows answers above questions.

**Acceptance Criteria:**

* [ ] User can input questions and get answers.
* [ ] Answers reflect previous conversation context.
* [ ] Each answer is displayed immediately above its question
* [ ] Chat history is scrollable and visually clear.
