
"""
This file contains the main FastAPI application.
For a larger project, we would move the routes to separate files, but for this example, we keep everything in one file.
"""

from uuid import UUID
from fastapi import FastAPI, APIRouter, HTTPException, Depends

from api_models import NurseRosteringJobRequest, NurseRosteringJobStatus
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel
from nurse_rostering.data_schema import NurseRosteringSolution
from api_config import get_db_connection, get_task_queue
from api_tasks import run_optimization_job
instance1 = """{
    "nurses": [
        {
            "uid": 17923323384421566150,
            "name": "A",
            "preferred_shifts": [
                17418580965168203661,
                996228336922217686
            ],
            "preferred_off_shifts": [],
            "blocked_shifts": [
                874755779498429225
            ],
            "days_off": [
                "2018-01-01"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 2,
            "preferred_off_shift_weight": 1,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 3876108791441737259,
            "name": "B",
            "preferred_shifts": [
                9746610754408104188,
                874755779498429225,
                17418580965168203661,
                996228336922217686,
                17682757349244880081
            ],
            "preferred_off_shifts": [],
            "blocked_shifts": [
                941746042370083164
            ],
            "days_off": [
                "2018-01-06"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 3,
            "preferred_off_shift_weight": 1,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 6723712542405774490,
            "name": "C",
            "preferred_shifts": [
                9746610754408104188,
                874755779498429225,
                17418580965168203661,
                996228336922217686,
                17682757349244880081
            ],
            "preferred_off_shifts": [
                9947529515075322772,
                8254982656376721305
            ],
            "blocked_shifts": [
                12965943452505425069
            ],
            "days_off": [
                "2018-01-09"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 1,
            "preferred_off_shift_weight": 1,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 2046497868671108197,
            "name": "D",
            "preferred_shifts": [
                10760430575324446868,
                12965943452505425069
            ],
            "preferred_off_shifts": [],
            "blocked_shifts": [
                996228336922217686
            ],
            "days_off": [
                "2018-01-03"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 2,
            "preferred_off_shift_weight": 1,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 11195089095296568457,
            "name": "E",
            "preferred_shifts": [],
            "preferred_off_shifts": [],
            "blocked_shifts": [
                10760430575324446868
            ],
            "days_off": [
                "2018-01-10"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 1,
            "preferred_off_shift_weight": 1,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 12940503099449689304,
            "name": "F",
            "preferred_shifts": [
                17682757349244880081,
                874755779498429225
            ],
            "preferred_off_shifts": [
                12965943452505425069
            ],
            "blocked_shifts": [
                941746042370083164
            ],
            "days_off": [
                "2018-01-06"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 2,
            "preferred_off_shift_weight": 3,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 3402887948730060276,
            "name": "G",
            "preferred_shifts": [],
            "preferred_off_shifts": [],
            "blocked_shifts": [
                17682757349244880081
            ],
            "days_off": [
                "2018-01-02"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 1,
            "preferred_off_shift_weight": 1,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        },
        {
            "uid": 15494355024931144469,
            "name": "H",
            "preferred_shifts": [
                6962178779305231662,
                6726947762149606287,
                9947529515075322772,
                10760430575324446868,
                8254982656376721305
            ],
            "preferred_off_shifts": [
                17418580965168203661,
                996228336922217686
            ],
            "blocked_shifts": [
                14414444666611515706
            ],
            "days_off": [
                "2018-01-08"
            ],
            "staff": true,
            "min_time_between_shifts": "PT0S",
            "preferred_shift_weight": 1,
            "preferred_off_shift_weight": 3,
            "minimum_work_time": 3360,
            "maximum_work_time": 4320,
            "minimum_consecutive_shifts": 2,
            "maximum_consecutive_shifts": 5,
            "minimum_consecutive_days_off": 2,
            "maximum_weekends": 1,
            "maximum_number_of_shifts_per_type": {
                "D": 14
            }
        }
    ],
    "shifts": [
        {
            "uid": 874755779498429225,
            "name": "0_D",
            "start_time": "2018-01-01T00:00:00",
            "end_time": "2018-01-01T08:00:00",
            "demand": 5,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 17682757349244880081,
            "name": "1_D",
            "start_time": "2018-01-02T00:00:00",
            "end_time": "2018-01-02T08:00:00",
            "demand": 7,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 996228336922217686,
            "name": "2_D",
            "start_time": "2018-01-03T00:00:00",
            "end_time": "2018-01-03T08:00:00",
            "demand": 6,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 17418580965168203661,
            "name": "3_D",
            "start_time": "2018-01-04T00:00:00",
            "end_time": "2018-01-04T08:00:00",
            "demand": 4,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 9746610754408104188,
            "name": "4_D",
            "start_time": "2018-01-05T00:00:00",
            "end_time": "2018-01-05T08:00:00",
            "demand": 5,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 941746042370083164,
            "name": "5_D",
            "start_time": "2018-01-06T00:00:00",
            "end_time": "2018-01-06T08:00:00",
            "demand": 5,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 2011703436640470940,
            "name": "6_D",
            "start_time": "2018-01-07T00:00:00",
            "end_time": "2018-01-07T08:00:00",
            "demand": 5,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 14414444666611515706,
            "name": "7_D",
            "start_time": "2018-01-08T00:00:00",
            "end_time": "2018-01-08T08:00:00",
            "demand": 6,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 12965943452505425069,
            "name": "8_D",
            "start_time": "2018-01-09T00:00:00",
            "end_time": "2018-01-09T08:00:00",
            "demand": 7,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 10760430575324446868,
            "name": "9_D",
            "start_time": "2018-01-10T00:00:00",
            "end_time": "2018-01-10T08:00:00",
            "demand": 4,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 6962178779305231662,
            "name": "10_D",
            "start_time": "2018-01-11T00:00:00",
            "end_time": "2018-01-11T08:00:00",
            "demand": 2,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 6726947762149606287,
            "name": "11_D",
            "start_time": "2018-01-12T00:00:00",
            "end_time": "2018-01-12T08:00:00",
            "demand": 5,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 8254982656376721305,
            "name": "12_D",
            "start_time": "2018-01-13T00:00:00",
            "end_time": "2018-01-13T08:00:00",
            "demand": 6,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        },
        {
            "uid": 9947529515075322772,
            "name": "13_D",
            "start_time": "2018-01-14T00:00:00",
            "end_time": "2018-01-14T08:00:00",
            "demand": 4,
            "type": "D",
            "not_followed_by_shift_types": [],
            "weight_below_demand": 100,
            "weight_above_demand": 1
        }
    ],
    "staff_weight": 1
}"""
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

@nurse_rostering_solver_v0_router.get("/test_hx")
def test_hx():
    """
    A simple test endpoint to verify that the API is working.
    """
    from nurse_rostering.data_schema import NurseRosteringInstance
    import json
    instance1_json = json.loads(instance1)
    instance = NurseRosteringInstance.model_validate_json(instance1)
    from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as NurseRosteringModelHXLY
    nurse_rostering_model = NurseRosteringModelHXLY(instance)
    solution = nurse_rostering_model.solve(max_time_in_seconds=60)
    return dict(solution.model_dump())

app.include_router(nurse_rostering_solver_v0_router, prefix="/nurse_rostering_solver/v0")