# API Endpoints Documentation

## Knowledge & Incident APIs

### 1. Summarize Knowledge Article
- **POST** `/api/v1/ai/summarize-knowledge`
- **Body:**
  ```json
  { "query": "<user question>" }
  ```
- **Response:**
  ```json
  { "summary": "...", "link": "..." }
  ```
- **Description:**
  Returns a summary of the most relevant ServiceNow knowledge article for the user's query. The summary will not contain any links; the article link is provided separately.

### 2. Summarize Incident
- **POST** `/api/v1/ai/summarize-incident`
- **Body:**
  ```json
  {
    "number": "INC0012345",
    "short_description": "...",
    "description": "...",
    "latest_comments": ["..."]
  }
  ```
- **Response:**
  ```json
  { "summary": "...", "key_facts": ["..."] }
  ```
- **Description:**
  Summarizes a ServiceNow incident, extracting key facts if available.

### 3. Work Notes
- **POST** `/api/v1/ai/work-notes`
- **Body:**
  ```json
  {
    "number": "INC0012345",
    "short_description": "...",
    "description": "...",
    "latest_comments": ["..."]
  }
  ```
- **Response:**
  ```json
  { "text": "..." }
  ```
- **Description:**
  Generates work notes for a ServiceNow incident.

### 4. Resolution Note
- **POST** `/api/v1/ai/resolution-note`
- **Body:**
  ```json
  {
    "number": "INC0012345",
    "short_description": "...",
    "description": "...",
    "latest_comments": ["..."]
  }
  ```
- **Response:**
  ```json
  { "text": "..." }
  ```
- **Description:**
  Generates a resolution note for a ServiceNow incident.

---

## Health Check

### 5. Health Check
- **GET** `/healthz`
- **Response:**
  ```json
  { "ok": true }
  ```
- **Description:**
  Returns a simple health check status for the API.
