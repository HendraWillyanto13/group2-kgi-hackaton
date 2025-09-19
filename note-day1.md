# Day 1 Lab: Object Detection

## Module 1

Total time about 30 mins

Prompt:
```
Scaffold a monorepo project with backend and frontend directories.

* [X] Clicking "Upload" triggers backend call and animates progress.
* [X] Success toast shown; files/progress reset.
* [X] Failure toast shown; UI re-enabled for retry.
* [X] Duplicate submissions prevented during in-flight uploads.h backend and frontend directories.

Requirements:
- Backend should be a FastAPI service (latest version).
- Use "uv" as the dependency manager and package installer for Python.
- Include two endpoints:
  - GET /health → returns {"status": "ok"}
  - POST /upload → accepts a file upload (e.g., multipart/form-data) and returns filename + size.
- Place the FastAPI service inside the `backend` directory with proper project structure:
  - backend/
    - app/
      - main.py
      - routes/
    - pyproject.toml (configured for uv)
    - README.md
- Frontend directory can remain empty for now (placeholder).
- Add clear instructions in the README.md for installing dependencies with uv and running the FastAPI app.
- Use context7 to fetch the latest FastAPI documentation and best practices.
```

## Module 2

Total time about 20 mins

### Task 1.2.1 — Frontend scaffolding & dependencies

**What it does:** Sets up a Vite React (JS) app in `frontend/` with Tailwind and shadcn/ui so we have a modern UI foundation.

**Prompt:**

> Scaffold a React app in `frontend/` using Vite (JavaScript template). Configure Tailwind (`tailwind.config.js` content for `index.html` and `src/**/*.{js,jsx}`, add `@tailwind base; @tailwind components; @tailwind utilities;` to `src/index.css`). Install **tailwindcss@^3.4.0**, `postcss`, and `autoprefixer`. Install shadcn/ui prerequisites (`clsx`, `tailwind-merge`, `lucide-react`), add Button, Input, Progress, Toaster under `src/components/ui/`, and mount `<Toaster />` at app root. Verify `npm run dev` renders a styled sample.

**Acceptance Criteria:**

* [X] Project runs from `frontend/` with `dev`, `build`, `preview` scripts.
* [X] Tailwind utilities render correctly in a sample component.
* [X] shadcn/ui `Button`, `Progress`, `Toaster` are available via `src/components/ui/*`.
* [X] `<Toaster />` mounted once at root; no console errors.

---

### Task 1.2.2 — Routing & Upload

**What it does:** Adds React Router and a dedicated `/upload` page to host the image uploader.

**Prompt:**

> Add `react-router-dom`. Wrap the app in `<BrowserRouter>`. Create a route `/upload` that renders `src/pages/UploadPage.jsx`. In `UploadPage.jsx`, show a heading “Image Upload” and placeholder text. Keep `<Toaster />` global.

**Acceptance Criteria:**

* [X] Navigating to `/upload` renders `UploadPage.jsx`.
* [X] No hydration/console warnings.
* [X] Toaster still visible globally across routes.

---

## Module 3

Total time about 10 mins

### Task 1.3.1 — File selection UI

**What it does:** Lets users choose one or more images and shows the chosen files in the UI.

**Prompt:**

> In `UploadPage.jsx`, implement a hidden `<input type="file" accept="image/*" multiple />` triggered by a shadcn `Button` (“Select Images”). Store selected files in state and render a list (filename + human-readable size). Show an empty state when none selected. Reject or warn for non-image files.

**Acceptance Criteria:**

* [x] Users can select multiple images and see filenames + sizes.
* [x] Non-image files are blocked or clearly warned.
* [x] Empty state visible when no files selected.
* [x] Button/input accessible via keyboard with proper label/aria-label.

---

## Module 4

Total time about 30 mins

### Task 1.4.1 — API integration

**What it does:** Provides an upload helper that posts `multipart/form-data` to the backend and reports progress.

**Prompt:**

> Create `src/lib/api.js` exporting `uploadImages(files, onProgress)`. Use `axios` to POST `FormData` to `${import.meta.env.VITE_API_BASE_URL ?? ""}/api/upload`. Append each file as `files[]`. Use `onUploadProgress` to emit integer percent (0–100) to the callback. Add a top-of-file comment documenting the request contract (multipart, `files[]`) and support both single/multi files.

**Acceptance Criteria:**

* [X] `uploadImages(files, onProgress)` exists and returns parsed response data.
* [X] Progress callback receives 0–100 during upload.
* [X] Uses `VITE_API_BASE_URL` when present; otherwise relative `/api/upload`.
* [X] Body is `multipart/form-data` with `files[]`.

---

### Task 1.4.2 — Upload workflow & progress feedback

**What it does:** Wires the UI to call the API helper, shows a progress bar, and notifies success/failure.

**Prompt:**

> In `UploadPage.jsx`, add a shadcn `Button` “Upload” that calls `uploadImages(selectedFiles, setProgress)`. Disable if no files or while uploading. Show a shadcn `Progress` component bound to progress state. On success: toast “Upload complete”, reset selected files and progress to 0. On error: toast a short failure message and restore UI to idle.

**Acceptance Criteria:**

* [ ] Clicking “Upload” triggers backend call and animates progress.
* [ ] Success toast shown; files/progress reset.
* [ ] Failure toast shown; UI re-enabled for retry.
* [ ] Duplicate submissions prevented during in-flight uploads.

---

### Task 1.4.3 — Styling, accessibility & README

**What it does:** Polishes the page’s look, ensures accessibility, and documents how to run/integrate.

**Prompt:**

> Style `/upload` with a centered card layout (max-w, padding, rounded corners, subtle shadow) using Tailwind + shadcn/ui. Ensure visible focus states and proper labels/aria-labels for all interactive elements. Add `frontend/README.md` with environment setup (`VITE_API_BASE_URL=http://localhost:8000`), quick-start commands, and a final acceptance checklist. *(Optional)* Add drag-and-drop with previews if time allows.

**Acceptance Criteria:**

* [X] Modern, clean page consistent with Tailwind + shadcn/ui.
* [X] Keyboard navigation and focus states verified; inputs labeled.
* [X] `frontend/README.md` includes env config and acceptance checklist.
* [X] (Optional) Drag-and-drop with previews works without breaking basic flow.

---

### Overall Acceptance (cross-task)

* [X] `/upload` page exists and is reachable.
* [X] Users can select and upload one or multiple images.
* [X] Uploads hit backend and show progress + success/failure feedback.
* [X] Page uses shadcn/ui components and app is bootstrapped with Vite under `frontend/`.

---
