# nurse-rostering-teamproject

This repository is a prototype for a nurse rostering project.

It is split into two main parts:

- **backend/** - FastAPI API, database layer, queue worker setup, and the actual solver code
- **frontend/** - Next.js UI for managing project data, starting solver jobs, and looking at solutions

## What is in here

The backend stores and serves the planning data for a project:

- projects
- nurses
- shift types
- shifts

It also has job endpoints for running optimization and returning solutions.

The solver side is not just one model. There are multiple approaches in the repo, including CP-SAT, Gurobi, Hexaly, and a greedy heuristic. So this is less a single polished application and more a working playground around one rostering problem.

The frontend is the part you click through. It has a project list, a project detail view, dialogs for editing rostering data, controls for solver settings, a jobs view, and a solution viewer.


## Folder overview

### `backend/`

Main backend code lives under `backend/app/`.

Important parts:

- `api_main.py` - FastAPI app and CRUD/job endpoints
- `api_tasks.py` - background job execution
- `postgres/` - SQLAlchemy models, DB connection, Pydantic schemas
- `nurse_rostering/` - solver logic, heuristics, utilities, examples, benchmarks
- `docker-compose.yml` - local stack for API, Redis worker, Postgres, and Hexaly setup

### `frontend/`

Main frontend code lives under `frontend/src/`.

Important parts:

- `app/` - routes and frontend-side API files
- `components/` - UI and rostering components
- `store/` - Zustand state stores
- `hooks/` - data loading hooks
- `types/` - shared TS types

## Running the project

The backend is mainly set up around Docker Compose.

The frontend is a normal Next.js app and expects a solver API URL in its environment file.

There are solver-specific license requirements on the backend side for Gurobi and Hexaly, so this is not a completely frictionless setup.

