
"""
This file contains the main FastAPI application.
For a larger project, we would move the routes to separate files, but for this example, we keep everything in one file.
"""

from uuid import UUID
from fastapi import FastAPI, APIRouter, HTTPException, Depends

from api_models import NurseRosteringJobRequest, NurseRosteringJobStatus
from solvers.cp_sat.solver import NurseRosteringModel
from solvers.data_schema import NurseRosteringSolution
from api_config import get_db_connection, get_task_queue
from api_tasks import run_optimization_job

app = FastAPI(
    title="Nurse Rostering Optimization API",
    description="This is a first test on how to deploy an optimization algorithm based on CP-SAT as an API.",
)

nurse_rostering_solver_v0_router = APIRouter(tags=["Nurse_Rostering_solver_v0"])

@nurse_rostering_solver_v0_router.post("/jobs", response_model=NurseRosteringJobStatus)
def post_job(
    job_request: NurseRosteringJobRequest,
    db_connection=Depends(get_db_connection),
    task_queue=Depends(get_task_queue),
):
    """
    Submit a new job to solve a Nurse Rostering instance.
    """
    job_status = db_connection.register_job(job_request)
    # enqueue the optimization job in the task queue.
    # Will return immediately, the job will be run in a separate worker.
    task_queue.enqueue(
        run_optimization_job,
        job_status.task_id,
        # adding a 60 second buffer to the job timeout
        job_timeout=job_request.optimization_parameters.timeout + 60,
    )
    return job_status

@nurse_rostering_solver_v0_router.get("/jobs/{task_id}", response_model=NurseRosteringJobStatus)
def get_job(task_id: UUID, db_connection=Depends(get_db_connection)):
    """
    Return the status of a job.
    """
    status = db_connection.get_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@nurse_rostering_solver_v0_router.get("/jobs/{task_id}/solution", response_model=NurseRosteringSolution)
def get_solution(task_id: UUID, db_connection=Depends(get_db_connection)):
    """
    Return the solution of a job, if available.
    """
    solution = db_connection.get_solution(task_id)
    if solution is None:
        raise HTTPException(status_code=404, detail="Solution not found")
    return solution

@nurse_rostering_solver_v0_router.delete("/jobs/{task_id}")
def cancel_job(task_id: UUID, db_connection=Depends(get_db_connection)):
    """
    Deletes/cancels a job. This will *not* immediately stop the job if it is running.
    """
    db_connection.delete_job(task_id)

@nurse_rostering_solver_v0_router.get("/jobs", response_model=list[NurseRosteringJobStatus])
def list_jobs(db_connection=Depends(get_db_connection)):
    """
    List all jobs.
    """
    return db_connection.list_jobs()


app.include_router(nurse_rostering_solver_v0_router, prefix="/nurse_rostering_solver/v0")