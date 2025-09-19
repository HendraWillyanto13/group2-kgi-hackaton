# Day 2 Lab: Object Detection

### Task 2.1.2.C – Improve File Handling

**Prompt:**

> Improvement for UI/UX in `UploadList.jsx` : Display them in a user-friendly grid with some metadata (filename, size, uploaded data). Provide pagination or lazy loading if there are many images. Also add number image per page with default 10 images. Ensure responsive design for mobile and desktop. Please change `Detect Objects` button to icon with small button on bottom right of each grid.

**Acceptance Criteria:**

* [ ] All uploaded images are visible in the grid view with metadata
* [ ] Page works across devices and browsers.
* [ ] Code is covered by relevant tests.
---


### Task 2.1.2.D – Improve File Upload

**Prompt:**

> Improvement for UI/UX in `UploadPage.jsx` : Implement a drag-and-drop UI component for image uploads. Ensure the component provides visual feedback when an image is dragged over the drop area. Support uploading multiple images at once. Validate file types (accept only image formats such as JPG, PNG, GIF). Display previews of uploaded images before submission. Provide error handling for unsupported file types and upload failures.

**Acceptance Criteria:**

* [ ] All uploaded images are visible in the grid view with metadata
* [ ] Page works across devices and browsers.
* [ ] Code is covered by relevant tests.
---

### Task 2.1.2.E – Metadata on Json

**Prompt:**

> Create metadata file in JSON format on `backend/uploads-metadata.json` to store following information : Original filename on upload, filename in `backend/uploads`, uploaded time and size. This metadata will be updated when file uploaded.

---


### Task 2.1.2.F – Update metadata on Json

**Prompt:**

> In `UploadPage.jsx`, after a successful upload, call GET `/detections/{image_id}`. Get objects information and store to `backend/uploads-metadata.json`

---

### Task 2.1.2.G – Show metadata in grid

**Prompt:**

> In `UploadList.jsx`, get object information from `uploads-metadata.json` and show on each grid at bottom with badge styles. Also add filter to find image by object metadata.

---
