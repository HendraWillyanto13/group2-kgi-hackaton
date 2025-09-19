# Day 2 Lab: Object Detection

## Module 1

### Task 2.1.1 — Use Azure AI Vision for Object Detection (Backend)

**What it does:** Calls the **Object Detection API** to analyze uploaded images and returns normalized boxes.

**Prompt:**

> Add/ensure a `/detections/{id}` endpoint. If it doesn't exist, create a minimal version that reads the uploaded image from storage. Call Azure Computer Vision Object Detection (use v3.2 analyze API) using env vars `VISION_ENDPOINT` and `VISION_KEY`. Normalize the response into `{ boxes: [{ label, x, y, w, h, score }] }`. On any failure (missing key, API error), return `{ boxes: [] }` and a non-200 error code with a helpful message.

**Objective**
Provide minimal read APIs the React app can consume.

**Acceptance Criteria**

* [x] Curling the endpoints returns JSON with expected fields.
* [x] Server supports simple search and pagination.
* [x] CORS works for local Vite dev server.
* [x] Endpoint exists and runs for everyone.
* [x] On success, returns real detection results.
* [x] On failure, degrades gracefully with `{ "boxes": [] }` and logs a readable error.

---

### Task 2.1.2 – Wire detections to frontend

**Prompt:**

> In `UploadPage.jsx`, after a successful upload, call GET `/detections/{image_id}`. Render returned `boxes` as overlays on the uploaded image. Create a `DetectionOverlay` React component that takes `{ imageUrl, boxes }` and draws bounding boxes with labels.

**Acceptance Criteria:**

* [x] Upload an image → frontend shows the image.
* [x] Bounding boxes with labels overlay correctly in the right positions.
* [x] Empty result = image shows without overlays.

---

### Task 2.1.2.A – File Handling

**Prompt:**

> Create new pages `UploadList.jsx` to show all uploaded images in folder `backend\uploads` with preview and capability to delete multiple selected uploaded images with confirmation before delete. On success: toast “Delete success”, reset / reload all file. Also make button to navigate from `UploadPages.jsx` to `UploadList.jsx` vice versa.

**Acceptance Criteria:**

* [ ] File list shown in UploadList with preview
* [ ] Can delete multiple files

---

## Module 2

### Task 2.2.1 — Containerize & run locally

**What it does:** Builds Docker images for backend and frontend and runs them with docker-compose.

**Prompt:**

> Create `Dockerfile` for backend (FastAPI + uvicorn) and frontend (Vite build → static server or served by backend). Add `docker-compose.yml` wiring ports and env vars. Commands: `docker compose up --build`. Document environment variables in a root `README.md`.

**Acceptance Criteria:**

* [ ] `docker compose up` starts both services locally.
* [ ] Frontend reachable; backend health endpoint returns OK.
* [ ] Upload → detection → report works locally with env set.

---

### Task 2.2.2 — Deploy to Azure Container Apps

**What it does:** Publishes images to ACR and deploys to **Azure Container Apps** with all env vars.

**Prompt:**

> Generate an az CLI script to: (1) create ACR if needed; (2) build & push both images; (3) deploy backend and frontend container apps; (4) set env vars `VISION_ENDPOINT`, `VISION_KEY`, `AOAI_ENDPOINT`, `AOAI_KEY`, `SEARCH_ENDPOINT`, `SEARCH_KEY`, and frontend `VITE_API_BASE_URL`. Output the public URLs.

**Acceptance Criteria:**

* [ ] Public URL works for frontend.
* [ ] End-to-end upload → detection → report with RAG works on Azure.

---

## Module 3 - AOAI

By the end of this module, participants will have extended the FastAPI app from Day 1 with new endpoints that use Azure OpenAI (AOAI) to evaluate resumes against job roles. This sets up the backend service that we’ll later connect to the Power Platform in Module 4.

---

### Task 2.3.1 — Wire Azure OpenAI client + config in existing app

**Objective**
Add AOAI client + config to the existing FastAPI project (no new app). Use env-based settings, a service API key header, and keep the surface small (one helper to call chat completions).

**Prompt**

> You are editing our existing FastAPI app.
>
> * Add configuration using pydantic-settings with: `API_TOKEN`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`.
> * Add a lightweight AOAI chat helper using the OpenAI 1.x SDK configured for Azure (base\_url: `{endpoint}/openai/deployments/{deployment}`).
> * Add a dependency that enforces header `x-api-key == API_TOKEN`, returning 401 otherwise.
> * Keep code clean, testable, and importable (e.g., `from app.ai import aoai_chat`).
> * Don’t create a new FastAPI app—extend the current one.

**Acceptance Criteria**

* [ ] Running server with correct envs succeeds; missing/wrong `x-api-key` → **401**.
* [ ] `aoai_chat(messages, response_format=None)` is importable and calls Azure OpenAI.
* [ ] No duplicate FastAPI instances; reuses the Day-1 app object.

---

### Task 2.3.2 — Rubric synthesizer (internal function, no endpoint)

**Objective / Description**
Create a pure function that **derives a role rubric** when none is supplied. This is internal (called by the scoring endpoint). Keep text concise and structured.

**Prompt**

> Add a function `synthesize_rubric(role_title: str | None, category: str | None, seniority: str | None, must: list[str] | None, nice: list[str] | None) -> str`.
>
> * Use a system prompt: “You create concise, unambiguous hiring rubrics…” (mission, must-haves, nice-to-haves, anti-requirements, 5–7 evaluation axes with 1/3/5 anchors).
> * User prompt should insert role\_title/category, optional seniority, must/nice lists; target \~350 words.
> * Temperature 0.2.
> * Return the rubric string.
> * Ready to be imported by the endpoint.

**Acceptance Criteria**

* [ ] Calling `synthesize_rubric("Data Engineer", None, "Mid", ["SQL","ETL"], ["Airflow"])` returns a non-empty rubric containing labeled sections and bullet points.
* [ ] Handles `role_title=None` and uses `category` fallback.

---

### Task 2.3.3 — Implement `POST /score_candidate` endpoint

**Objective**
Add a single endpoint that (a) validates inputs, (b) derives rubric if missing, (c) calls scorer prompt, (d) returns strict JSON:
`{ score_0_100, strengths[], risks[], explanation, role_profile_used }`.

**Prompt**

> In our existing FastAPI app, add `POST /score_candidate`.
>
> * Request model fields: `resume_text` (required, min 50 chars), optional `role_profile`, `role_title`, `category`, `seniority`, `must_have[]`, `nice_to_have[]`.
> * If neither `role_profile` nor (`role_title` or `category`) is provided → return 400.
> * If `role_profile` missing, call `synthesize_rubric(...)` to generate it.
> * Scoring call: system prompt “You are a rigorous hiring panel…”; user prompt includes the rubric and **verbatim resume**.
> * Ask the model for **JSON** using response\_format `{"type":"json_object"}` with keys: `score_0_100` (int), `strengths` (3–6 strings, cite evidence), `risks` (3–6 strings, cite evidence), `explanation` (string).
> * Clamp score to \[0,100].
> * Return a pydantic `ScoreResponse` including the final rubric in `role_profile_used`.
> * Protect with the `x-api-key` dependency.

**Acceptance Criteria**

* [ ] `curl` happy path (auto-derive rubric):

  ```bash
  curl -s -X POST http://localhost:8000/score_candidate \
    -H "Content-Type: application/json" -H "x-api-key: $API_TOKEN" \
    -d '{
      "role_title":"Data Engineer",
      "seniority":"Mid",
      "resume_text":"<paste Resume_str here>",
      "must_have":["SQL","ETL","Data modeling"],
      "nice_to_have":["Airflow","Spark"]
    }'
  ```

  Returns HTTP **200** with **valid JSON** and keys: `score_0_100` (0–100), `strengths` (>=3), `risks` (>=3), `explanation` (non-empty), `role_profile_used` (non-empty).
* [ ] Error path: missing role context returns HTTP **400** with clear message.
* [ ] Wrong API key returns **401**.

---

### Task 2.3.4 — Tiny in-memory rubric cache (performance/cost) (OPTIONAL)

**Objective / Description**
Add a simple LRU cache keyed by `(role_title|category, seniority, must[], nice[])` to avoid re-prompting rubric synthesis during the lab/demo.

**Prompt**

> Add a tiny in-memory LRU cache (e.g., `functools.lru_cache` or a bounded dict) for `synthesize_rubric(...)`.
>
> * Build a stable key from normalized inputs (lowercased strings; sorted lists for must/nice).
> * On cache hit, skip the AOAI rubric call.
> * Add minimal logging: “rubric cache hit/miss”.

**Acceptance Criteria**

* Repeating the same request twice shows a **cache hit** log on the second call.
* Second response is materially identical and faster (observable locally).
* Code path is transparent to the endpoint (no behavior change).

---

### Task 2.3.5 — Minimal observability & safety rails (OPTIONAL)

**Objective / Description**
Add pragmatic logging and basic safeguards without bloating the code: input length checks, hashed candidate token for correlation, and prompt/response size guards.

**Prompt**

> Enhance the endpoint with:
>
> * Truncate `resume_text` to a max token/char budget (log truncation).
> * Compute a stable, non-PII correlation id: `sha256(first 512 chars of resume_text)`; log it with every request.
> * Log timing for (rubric, scoring) calls, and whether cache was used.
> * If model returns malformed JSON, retry once; if still bad, return 502 with a clear error.
> * Ensure we never log the full resume—only lengths and the hash.

**Acceptance Criteria**

* Logs include: correlation id, input lengths, cache hit/miss, AOAI call durations.
* Malformed model output path returns **502** with message “Upstream parsing error” (or similar) after one retry.

---

### Task 2.3.6 — Smoke-test scripts + Power Apps readiness (OPTIONAL)

**Objective / Description**
Provide ready-to-use cURL scripts and confirm CORS & response shape are **Power Apps Custom Connector** friendly.

**Prompt**

> Add:
>
> * `scripts/example_score.sh` with two cURL examples (auto-derive rubric by role\_title; and explicit role\_profile).
> * Enable permissive CORS for the lab origin (we’ll replace later).
> * Add a brief README section documenting request/response JSON for the **Custom Connector** (keys, types).
> * Confirm response time target (< 3s with cached rubric; < 7s cold) in README troubleshooting.

**Acceptance Criteria**

* `scripts/example_score.sh` runs successfully (200) with valid JSON output.
* CORS preflight succeeds for `POST /score_candidate`.
* README shows the exact request/response schema that matches the connector definition you’ll create in Module 4.

---

### Task 2.3.7 — Add SQLite persistence to the backend

**Objective**
Create a local SQLite database and models for `roles` and `candidates`, including columns to store scoring outputs.

**Prompt**

> “In `backend/` FastAPI app, add SQLite persistence using SQLModel or SQLAlchemy.
>
> * DB file: `app.db` under `backend/`.
> * Models:
>
>   * Role(id PK, title, department, role\_profile TEXT).
>   * Candidate(id PK, name, raw\_category, resume\_text TEXT, applied\_role\_id FK→Role, fit\_score INT NULL, strengths TEXT NULL, risks TEXT NULL, explanation TEXT NULL, updated\_at).
> * Create `database.py` with engine, SessionLocal, and `init_db()` that creates tables.
> * Wire dependency `get_db()` into FastAPI.
> * Call `init_db()` at startup.”

**Acceptance Criteria**

* [ ] `app.db` is created on first run.
* [ ] Tables `role` and `candidate` exist.
* [ ] Server boots with no migration errors.

**Implementation Summary:**
- Added `sqlmodel>=0.0.14` dependency to `pyproject.toml` for type-safe database operations
- Created database models in `app/models/database.py`:
  - **Role**: `id` (PK), `title`, `department`, `role_profile` (TEXT) with relationship to candidates
  - **Candidate**: `id` (PK), `name`, `raw_category`, `resume_text` (TEXT), `applied_role_id` (FK→Role), `fit_score` (INT NULL), `strengths` (TEXT NULL), `risks` (TEXT NULL), `explanation` (TEXT NULL), `updated_at` (DATETIME)
- Created `app/database.py` with SQLite engine, `init_db()` function, and `get_db()` FastAPI dependency
- Added startup event handler in `app/main.py` to automatically call `init_db()` on server start
- Database file `app.db` (12KB) created successfully with proper table schemas and foreign key relationships
- All components tested: imports successful, server boots without errors, health endpoint responsive

---

### Task 2.3.8 — Seed SQLite from a tiny CSV (10–50 resumes)

**Objective**
Quickly load a small subset of the open-resume dataset into SQLite. Keep it fast and deterministic.

**Prompt**

> “Add a `scripts/seed.py` that:
>
> * Reads `data/candidates.csv` with columns: id,name,Resume\_str,Category.
> * Inserts/upsserts into Candidate: `name`, `resume_text=Resume_str`, `raw_category=Category`.
> * Also insert 3 sample Roles with realistic `role_profile` JDs (e.g., Information-Technology, ‘Accountant’, ‘HR Generalist’, ‘Sales’).
> * Provide a `make seed` or `uv run scripts/seed.py` command in README.
> * If rows already exist, skip duplicates.”

**Acceptance Criteria**

* [ ] Running `uv run scripts/seed.py` completes without error.
* [ ] `SELECT COUNT(*) FROM candidate` returns expected row count.
* [ ] At least 3 roles present.

---

### Task 2.3.9 — AOAI scoring endpoint that also persists results

**Objective**
Expose `POST /score/{candidate_id}` that takes either `role_id` or raw `role_profile`, calls AOAI (from Module 3), saves results into SQLite, and returns the payload.

**Prompt**

> “In FastAPI, implement:
>
> * `POST /score/{candidate_id}` request body: `{ role_id?: number, role_profile?: string }`.
> * Resolve `role_profile` (if `role_id` given, load from DB; else use provided string).
> * Call existing AOAI scoring helper (model name, endpoint, key from env `.env`), returning `{ score_0_100, strengths[], risks[], explanation }`.
> * Persist to Candidate: `fit_score`, `strengths` (join lines), `risks` (join lines), `explanation`, `updated_at`.
> * Return the saved result.
> * Add basic error handling if candidate/role not found.”

**Acceptance Criteria**

* [ ] `POST /score/{id}` with a valid role updates the candidate row.
* [ ] Response JSON includes `fit_score` and `explanation`.
* [ ] Refreshing candidate shows persisted values.

**Implementation Summary:**
- Implemented `POST /score/{candidate_id}` in `app/api/scoring.py`.
- Accepts `{ role_id?: number, role_profile?: string }` in request body, validates mutual exclusivity.
- Resolves `role_profile` from DB if `role_id` is given, or uses provided string.
- Calls AOAI scoring helper, receives `{ score_0_100, strengths[], risks[], explanation }`.
- Persists results to Candidate: `fit_score`, `strengths` (joined), `risks` (joined), `explanation`, `updated_at`.
- Returns saved result in response.
- Handles errors for missing candidate/role, invalid input, and AOAI failures.
- Fully tested: valid/invalid candidate/role, both/neither fields, API key, and persistence.

---

### Task 2.3.10 — Read endpoints for UI (roles, candidates, detail)

**Objective**
Provide minimal read APIs the React app can consume.

**Prompt**

> “Add REST endpoints:
>
> * `GET /roles` → list `{id,title,department}`.
> * `GET /candidates?search=&category=&role_id=&page=&page_size=` → returns a paginated list with fields `{id,name,raw_category,fit_score}`; filter by `search in name OR resume_text`, `raw_category`, and optional `applied_role_id`.
> * `GET /candidates/{id}` → returns full record including `resume_text`, scoring fields.
>   Return JSON only, no ORM objects. Include CORS for `http://localhost:5173`.”

**Acceptance Criteria**

* [ ] Curling the endpoints returns JSON with expected fields.
* [ ] Server supports simple search and pagination.
* [ ] CORS works for local Vite dev server.

**Implementation Summary:**
- Added response models: `RoleResponse`, `CandidateListItem`, `CandidatesResponse`, `CandidateDetailResponse`
- Implemented `GET /roles` returning all roles with id, title, department
- Implemented `GET /candidates` with full filtering and pagination:
  - Search filter: name OR resume_text contains search term
  - Category filter: exact match on raw_category
  - Role ID filter: exact match on applied_role_id
  - Pagination: page, page_size with total count and metadata
- Implemented `GET /candidates/{id}` returning full candidate details including resume and scoring
- All endpoints return clean JSON (no ORM objects)
- CORS already configured for `http://localhost:5173`
- Comprehensive testing: all filters, pagination, error cases, and CORS preflight verified

### Task 2.3.11 — Minimal React UI to score a candidate

**Objective**
Create a single page that lists roles and candidates, lets a user score one, and shows results.

**Prompt**

> “In `frontend/` (Vite React):
>
> * Add `.env` with `VITE_API_BASE=http://localhost:8000`.
> * Create components:
>
>   * `RoleSelect` → dropdown fetching `/roles`.
>   * `CandidateList` → list from `/candidates`, with search box.
>   * `ScorePanel` → shows selected candidate’s latest `fit_score`, strengths/risks, explanation.
> * ‘Score Candidate’ button: calls `POST /score/{id}` with selected `role_id`, then refreshes candidate detail.
> * Show loading states, disable button while scoring.
> * Keep styling minimal (plain CSS/Tailwind optional).
> * Use `fetch` or `axios` with base URL from env.”

**Acceptance Criteria**

* [ ] Roles load into a dropdown.
* [ ] Candidates list renders; search filters it.
* [ ] Clicking **Score Candidate** returns a score and updates the panel.
* [ ] Refreshing the page keeps the score (persisted in SQLite).

**Implementation Summary:**
- Added `.env` configuration with `VITE_API_BASE=http://localhost:8000` (already configured)
- Extended API library in `src/lib/api.js` with scoring endpoints: `getRoles()`, `getCandidates()`, `getCandidate()`, `scoreCandidate()`
- Created `RoleSelect` component: dropdown fetching `/api/roles` with loading states and error handling
- Created `CandidateList` component: paginated list from `/api/candidates` with search functionality and selection
- Created `ScorePanel` component: displays candidate details, fit_score, strengths, risks, and explanation
- Created `ScoringPage` main page combining all components with Score Candidate button
- Implemented loading states: button disabled while scoring, spinner animation, form validation
- Added error handling and success messages throughout the UI
- Updated backend scoring endpoints to use `/api` prefix for consistency with other endpoints
- Added routing in `App.jsx` with navigation button on homepage
- All components use proper React patterns: hooks, callbacks, error boundaries
- Comprehensive testing: roles dropdown loads, candidate search/filtering works, scoring updates persist

---

# Task 6 — Quick run scripts + trainer checklist

**Objective**
Make it zero-friction to start/verify locally for the 30-minute slot.

**Prompt**

> “Update root README with:
>
> * Prereqs: Python 3.12+, `uv`, Node 22+.
> * Backend: `cd backend && uv sync && cp .env.example .env && uv run scripts/seed.py && uv run app.py` (or `uvicorn app:app --reload`).
> * Frontend: `cd frontend && npm i && npm run dev`.
> * Verify endpoints with curl and visit `localhost:5173`.
> * Troubleshooting notes for CORS and missing env vars.”

**Acceptance Criteria**

* [ ] A fresh clone can be run locally end-to-end in <5 minutes.
* [ ] README includes exact commands and expected outputs.
* [ ] Demo path: select role → select candidate → score → see results.

---

## Notes to keep it within 30 minutes

* Pre-prepare `data/candidates.csv` (10–50 rows).
* Keep AOAI creds ready in `.env`.
* Have the Vite app scaffolded; participants mostly paste fetch logic + simple JSX.
* If time is tight: hardcode 3 roles in seeding and skip pagination.

If you want, I can also draft the **exact Copilot-ready code blocks** (models, routers, and a tiny React page) you’ll paste into the repo so the session flows even faster.