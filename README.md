# Simple FastAPI portfolio (with Redis + Docker)

This project serves a minimal portfolio page built from a `.docx` resume using FastAPI, cached in Redis, and packaged with Docker.

Quick start (Docker):

```bash
docker compose build
docker compose up
```

Open http://localhost:8000

Notes:
- The app reads `Hassan_Khan_resume.docx` from the project root and caches parsed content in Redis for 5 minutes.
- To change the resume path, set `RESUME_PATH` environment variable for the `web` service.
