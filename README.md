# EKITI@30 DIGITAL

> **Our Story. Our People. Our Future.**

EKITI@30 DIGITAL is an independent, collaborative digital knowledge platform documenting Ekiti State's journey from its creation in 1996 to 2026 and beyond.

The project brings together history, people, places, culture, tourism, citizen stories, verified knowledge, and community visions for Ekiti's future in one growing digital platform.

## Vision

To build a living digital record of Ekiti State that preserves its history, makes its knowledge accessible, celebrates its people and places, and gives citizens a space to document their experiences and imagine the next 30 years.

## Project Goals

* Document Ekiti State's history from 1996 to 2026.
* Build a reliable and continuously growing Ekiti knowledge base.
* Preserve cultural heritage, traditions, stories, landmarks, and tourism resources.
* Provide geographical information about all 16 Local Government Areas.
* Give citizens a platform to share authentic Ekiti stories.
* Collect citizen visions for **Ekiti 2056**.
* Develop **Ask Ekiti**, an AI-powered knowledge assistant grounded in a curated knowledge base.
* Create a digital resource that can continue growing beyond the 30th anniversary.

## Core Features

### 1. Ekiti Timeline

An interactive timeline covering important events, milestones, people, institutions, and developments from 1996 to 2026.

### 2. Explore Ekiti

A geographical and cultural exploration of Ekiti State, including its 16 LGAs, headquarters, landmarks, institutions, tourism locations, and other points of interest.

### 3. My Ekiti Story

A citizen contribution space where people can share memories, experiences, historical accounts, community stories, photographs, and other relevant stories about Ekiti.

### 4. Ask Ekiti

An AI-powered assistant designed to answer questions about Ekiti using a curated and reviewed knowledge base rather than relying solely on unrestricted model-generated information.

### 5. Ekiti 2056

A citizen vision space for ideas, hopes, proposals, and aspirations for the next 30 years of Ekiti's development.

### 6. Ekiti Knowledge Base

A structured collection of sourced information covering areas such as:

* History and governance
* Local Government Areas
* Culture and heritage
* Tourism and landmarks
* Education
* Agriculture
* Health
* Economy
* Demographics and statistics
* Notable people and institutions
* Community knowledge

## Information & Verification Principles

Accuracy is central to the project.

Where factual information is published, the team should identify and preserve the source used to establish it. Sources may include official records, reputable publications, academic materials, institutional documents, archival materials, and other credible references.

Citizen-submitted stories and personal accounts are valuable forms of community knowledge, but they should be clearly distinguished from independently verified historical or factual claims.

The project does not treat AI-generated output as a source by itself. AI-assisted content must be grounded in reviewed source material where factual claims are involved.

## Project Structure

The project is being developed collaboratively by an 8-member team:

| Member   | Responsibility                       |
| -------- | ------------------------------------ |
| Member 1 | Project Founder / Technical Lead     |
| Member 2 | Engineering Lead                     |
| Member 3 | AI & Data Lead                       |
| Member 4 | Research & History Lead              |
| Member 5 | Geospatial & LGA Lead                |
| Member 6 | UI/UX & Design Lead                  |
| Member 7 | Culture, Tourism & Content Lead      |
| Member 8 | Community, Media & Verification Lead |

Each member owns a defined project area while collaborating with the rest of the team.

## Development Approach

The first week is an intensive **launch sprint** focused on establishing the foundation, collecting initial content, creating the first working product structure, and validating the workflow.

The project is **not limited to the first week**. EKITI@30 DIGITAL is intended to remain a growing platform beyond the 30th anniversary.

Our working flow is:

**BACKLOG → READY → IN PROGRESS → REVIEW → APPROVED → DONE**

## Repository Structure

The repository will gradually contain:

* Application source code
* Data and knowledge-base structures
* Research documentation
* Content and verification workflows
* UI/UX assets
* Tests
* Project documentation

## Contribution

Contributions should be made within the contributor's assigned area and follow the project's verification and review process.

Before adding factual information, contributors should record the source and relevant context. Significant changes to the application should be reviewed before being merged into the main project.

More detailed contribution guidelines will be provided in `CONTRIBUTING.md`.

## Project Status

**Status:** Initial development and launch sprint.

This repository is the technical home of EKITI@30 DIGITAL.

## Getting Started (Development)

The application has two parts: a FastAPI **backend** (`backend/`) and a Next.js **frontend** (`frontend/`). See `ARCHITECTURE.md` for the full stack rationale and repository layout.

### Backend setup

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API defaults to a local SQLite database (`sqlite:///./dev.db`), so no database setup is required to get started. To use Postgres instead, set `DATABASE_URL` in `.env` (or run `docker compose up` from the repo root, which starts a Postgres service alongside the backend).

**Note:** the Ask Ekiti knowledge base uses a `pgvector` column for embeddings, which requires Postgres with the pgvector extension (the `docker-compose.yml` Postgres image already has it). If you're running locally against the SQLite default, vector search won't be available — that's expected; switch to the Dockerized Postgres for that.

### Frontend setup

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

### Verify it's working

* Backend: visit [http://localhost:8000/api/health](http://localhost:8000/api/health) — should return `{"status": "ok"}`
* Frontend: visit [http://localhost:3000](http://localhost:3000)

---

**EKITI@30 DIGITAL**
*Our Story. Our People. Our Future.*
