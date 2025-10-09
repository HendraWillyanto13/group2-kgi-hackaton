### UserStory 1 Task 1.1 – Add capability to upload excel files
 
**What it does:** Create an UI pages that allows user to upload excel files to server.

**Prompt:**
 
> Create new pages `UploadKnowledge.jsx` in pages folder frontend to build a file upload page. 
Make dropdown list consists of option : 
1. value : `UMS` , display name : `Undercarriage Management System`
2. value : `KOMTRAX`, display name : `KOMTRAX`.
Allow selecting only one file at a time and accept only .xlsx .xls and .csv extensions. Use an <input type="file"> with proper accept attribute and multiple={false}. 
Implement a drag-and-drop UI component for document uploads. Display a progress bar while the file is uploading. Use a toast or alert() to notify the user whether the upload was successful or failed. Do not implement function to call api upload yet.
Also make button to navigate from `App.jsx` to `UploadKnowledge.jsx` vice versa.

 
**Objective**
Implement a conversational interface that preserves context and shows answers above questions.
 
**Acceptance Criteria:**
 
* [ ] User can input questions and get answers.
* [ ] Answers reflect previous conversation context.
* [ ] Each answer is displayed immediately above its question
* [ ] Chat history is scrollable and visually clear.