# Backend

This backend is a FastAPI-based API for the nurse rostering prototype.

It does two main jobs:

1. store and manage rostering data in Postgres
2. run optimization jobs and return solutions

## What it contains

The main backend code is inside `app/`.

### `api_main.py`

This is the FastAPI entry point.

It exposes:

- job endpoints for submitting optimization runs and checking status
- CRUD endpoints for projects
- CRUD endpoints for shift types
- CRUD endpoints for shifts
- CRUD endpoints for nurses

The API prefix used for the CRUD part is `nurse_rostering_solver/v0`.

### `api_tasks.py`

This file handles background optimization jobs.

The code routes a job to one of several solver options that exist in the repo:

- Gurobi
- Hexaly
- CP-SAT
- greedy heuristic

It also supports sending a webhook when a job finishes.

### `postgres/`

This folder contains the database layer:

- SQLAlchemy models
- Pydantic schemas
- DB session setup

The database models cover the core planning objects like projects, nurses, shift types, and shifts.


### `nurse_rostering/`

This is where the actual rostering logic lives.

The folder is broader than just one solver file. It also has:

- heuristics
- utilities
- examples
- benchmarks
- solver-specific subfolders
- a large shared data schema

So this part is the the research / modeling core of the project.

## Infrastructure setup

The backend is set up to run through Docker Compose.

From the current config, the stack includes:

- the FastAPI app
- Redis
- RQ worker processes
- Postgres
- a Hexaly-related service/setup

The API is exposed on port `8080`.

## Environment and licenses

There is a `.env.example` file for Postgres credentials.

The current setup also expects:

- a Gurobi license at `~/gurobi.lic`
- a Hexaly license at `backend/hexaly_installation/license.dat`

Without those, not every solver path will work.

## Dependencies

The requirements file shows that this backend mixes web/API tooling and optimization tooling.

Examples:

- FastAPI / Uvicorn
- SQLAlchemy
- Redis / RQ
- OR-Tools
- Gurobi
- Hexaly

The backend is not just a thin web wrapper, but also the place where the optimization stack lives.

INSERT OLD README 

# Setup

## Prequisites
Make sure you have Docker installed on your machine.

### Licenses

#### Gurobi License
Ensure that the gurobi license is stored at `~/gurobi.lic`.

#### Hexaly License
The Hexaly license needs to be stored inside the project folder at `backend/hexaly_installation/license.dat`. A git ignore rule is in place to prevent it from being committed to version control.

Usually the license file can be found in `/opt/hexaly_14_0/license.dat` on  the local machine.

You can check whether the license is read correctly by checking the result on `http://127.0.0.1:8080/nurse_rostering_solver/v0/test_hx`.

#### Environment Configuration
To connect with the postgres database, you have to provide a user, password and database name in an environment file. To do so, follow these steps:
1. In this folder (backend/), create a .env file (touch .env)
2. copy the contents from the .env.example file.
3. Replace the fields `your_user` etc., with your values. Right now, the database will run locally on your machine, so the actual values do not matter. Still, do not try to commit your .env file.
When first running the container, the user will be created and saved on the volume. Changing these values later without adjusting the volume will lead to an authentication error.


## Instructions

To run the backend Docker container, follow these steps:
1. Make sure you have Docker installed on your machine. You can download it from [here](https://www.docker.com/get-started).
2. Open your terminal or command prompt.
3. Navigate to the `backend` folder.
4. Run the following command to build the Docker image:
   ```
   docker compose build
   ```
5. After the image is built, run the following command to start the Docker container:
   ```
   docker compose up
   ```
6. The backend server should now be running inside the Docker container. You can access it at `http://localhost:8080`.
7. To stop running the container, do:
  ```
  docker compose down
  ```