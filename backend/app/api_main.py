
"""
This file contains the main FastAPI application.
For a larger project, we would move the routes to separate files, but for this example, we keep everything in one file.
"""
from typing import List
from uuid import UUID
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date, timezone

from api_models import NurseRosteringJobRequest, NurseRosteringJobStatus
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel
from nurse_rostering.data_schema import NurseRosteringSolution
from api_config import get_db_connection, get_task_queue
from api_tasks import run_optimization_job

from sqlalchemy.orm import Session
from postgres.database import get_db
from postgres.models_db.project import Project
from postgres.models_db.nurse import Nurse
from postgres.models_db.shift_type import ShiftType
from postgres.models_db.shift import Shift
from postgres.models_db.solution_entry import SolutionEntry

from postgres.schemas_pydantic.project import ProjectCreate, ProjectUpdate, ProjectResponse
from postgres.schemas_pydantic.shift_type import ShiftTypeCreate, ShiftTypeUpdate, ShiftTypeResponse
from postgres.schemas_pydantic.shift import ShiftCreate, ShiftBulkCreate, ShiftUpdate, ShiftBulkDelete, ShiftResponse
from postgres.schemas_pydantic.nurse import NurseCreate, NurseResponse, NurseUpdate
from postgres.schemas_pydantic.solution_entry import SolutionEntryCreate, SolutionEntryResponse, SolutionEntryUpdate
from postgres.database import engine, Base


instance1 = """{"nurses":[{"uid":2689136614758892491,"name":"A","preferred_shifts":[1.3861193355429956e+19,6765788887040412197],"preferred_off_shifts":[],"blocked_shifts":[3657210134181071307],"days_off":["2018-01-01"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{"6765788887040412197":2,"13861193355429955573":2},"preferred_off_shift_weight":{},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":4451612988135722210,"name":"B","preferred_shifts":[8660754316050517150,1.529813655107825e+19,6765788887040412197,3657210134181071307,1.3861193355429956e+19],"preferred_off_shifts":[],"blocked_shifts":[1.4859224508468908e+19],"days_off":["2018-01-06"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{"3657210134181071307":3,"8660754316050517150":3,"6765788887040412197":3,"13861193355429955573":3,"15298136551078249949":3},"preferred_off_shift_weight":{},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":1.2116270340358097e+19,"name":"C","preferred_shifts":[8660754316050517150,1.529813655107825e+19,6765788887040412197,3657210134181071307,1.3861193355429956e+19],"preferred_off_shifts":[6343443131770751616,4779094247707592947],"blocked_shifts":[1.7566417533660905e+19],"days_off":["2018-01-09"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{"3657210134181071307":1,"8660754316050517150":1,"6765788887040412197":1,"13861193355429955573":1,"15298136551078249949":1},"preferred_off_shift_weight":{"6343443131770751616":1,"4779094247707592947":1},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":7235008216942528494,"name":"D","preferred_shifts":[1.7566417533660905e+19,6189569510337693856],"preferred_off_shifts":[],"blocked_shifts":[6765788887040412197],"days_off":["2018-01-03"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{"17566417533660905585":2,"6189569510337693856":2},"preferred_off_shift_weight":{},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":1.7403661535279073e+19,"name":"E","preferred_shifts":[],"preferred_off_shifts":[],"blocked_shifts":[6189569510337693856],"days_off":["2018-01-10"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{},"preferred_off_shift_weight":{},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":2425375194666716412,"name":"F","preferred_shifts":[8660754316050517150,3657210134181071307],"preferred_off_shifts":[1.7566417533660905e+19],"blocked_shifts":[1.4859224508468908e+19],"days_off":["2018-01-06"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{"3657210134181071307":2,"8660754316050517150":2},"preferred_off_shift_weight":{"17566417533660905585":3},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":1.3562147589898322e+19,"name":"G","preferred_shifts":[],"preferred_off_shifts":[],"blocked_shifts":[8660754316050517150],"days_off":["2018-01-02"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{},"preferred_off_shift_weight":{},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}},{"uid":1.140411048921565e+19,"name":"H","preferred_shifts":[6189569510337693856,6343443131770751616,1.5415207710859481e+19,4779094247707592947,1.1725206950407913e+19],"preferred_off_shifts":[1.3861193355429956e+19,6765788887040412197],"blocked_shifts":[4802009500853814269],"days_off":["2018-01-08"],"staff":true,"min_time_between_shifts":"PT0S","preferred_shift_weight":{"6189569510337693856":1,"15415207710859481059":1,"11725206950407914261":1,"6343443131770751616":1,"4779094247707592947":1},"preferred_off_shift_weight":{"6765788887040412197":3,"13861193355429955573":3},"minimum_work_time":3360,"maximum_work_time":4320,"minimum_consecutive_shifts":2,"maximum_consecutive_shifts":5,"minimum_consecutive_days_off":2,"maximum_weekends":1,"maximum_number_of_shifts_per_type":{"D":14}}],"shifts":[{"uid":3657210134181071307,"name":"0_D","start_time":"2018-01-01T00:00:00","end_time":"2018-01-01T08:00:00","demand":5,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":8660754316050517150,"name":"1_D","start_time":"2018-01-02T00:00:00","end_time":"2018-01-02T08:00:00","demand":7,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":6765788887040412197,"name":"2_D","start_time":"2018-01-03T00:00:00","end_time":"2018-01-03T08:00:00","demand":6,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.3861193355429956e+19,"name":"3_D","start_time":"2018-01-04T00:00:00","end_time":"2018-01-04T08:00:00","demand":4,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.529813655107825e+19,"name":"4_D","start_time":"2018-01-05T00:00:00","end_time":"2018-01-05T08:00:00","demand":5,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.4859224508468908e+19,"name":"5_D","start_time":"2018-01-06T00:00:00","end_time":"2018-01-06T08:00:00","demand":5,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.6068697900063803e+19,"name":"6_D","start_time":"2018-01-07T00:00:00","end_time":"2018-01-07T08:00:00","demand":5,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":4802009500853814269,"name":"7_D","start_time":"2018-01-08T00:00:00","end_time":"2018-01-08T08:00:00","demand":6,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.7566417533660905e+19,"name":"8_D","start_time":"2018-01-09T00:00:00","end_time":"2018-01-09T08:00:00","demand":7,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":6189569510337693856,"name":"9_D","start_time":"2018-01-10T00:00:00","end_time":"2018-01-10T08:00:00","demand":4,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.5415207710859481e+19,"name":"10_D","start_time":"2018-01-11T00:00:00","end_time":"2018-01-11T08:00:00","demand":2,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":1.1725206950407913e+19,"name":"11_D","start_time":"2018-01-12T00:00:00","end_time":"2018-01-12T08:00:00","demand":5,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":6343443131770751616,"name":"12_D","start_time":"2018-01-13T00:00:00","end_time":"2018-01-13T08:00:00","demand":6,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1},{"uid":4779094247707592947,"name":"13_D","start_time":"2018-01-14T00:00:00","end_time":"2018-01-14T08:00:00","demand":4,"type":"D","not_followed_by_shift_types":[],"weight_below_demand":100,"weight_above_demand":1}],"staff_weight":1}"""                                     



app = FastAPI(
    title="Nurse Rostering Optimization API",
    description="This is a first test on how to deploy an optimization algorithm based on CP-SAT as an API.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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
    instance = NurseRosteringInstance.model_validate_json(instance1)
    from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as NurseRosteringModelHXLY
    nurse_rostering_model = NurseRosteringModelHXLY(instance)
    solution = nurse_rostering_model.solve(max_time_in_seconds=60)
    return dict(solution.model_dump())


projects_router = APIRouter(tags=["Projects"], prefix="/projects")

@projects_router.post("", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate ,
    db: Session = Depends(get_db),
):
    
    start_str, end_str = project_data.planning_horizon
    planning_start = date.fromisoformat(start_str)
    planning_end = date.fromisoformat(end_str)

    new_project = Project(
        name=project_data.name,
        planning_start=planning_start,
        planning_end=planning_end,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project

@projects_router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@projects_router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@projects_router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = project_update.name
    project.planning_start = project_update.planning_horizon[0]
    project.planning_end = project_update.planning_horizon[1]
    project.last_modified = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)

    return project

@projects_router.delete("/{project_id}")
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return


shift_types_router = APIRouter(tags=["ShiftTypes"], prefix="/projects/{project_id}/shift_types")

@shift_types_router.post("", response_model=ShiftTypeResponse)
def create_shift_type(project_id: UUID, shift_data: ShiftTypeCreate, db: Session = Depends(get_db)):

    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_shift = ShiftType(
        id=shift_data.id,
        project_id=project_id,
        name=shift_data.name,
        duration=shift_data.duration,
        start=shift_data.start,
        end=shift_data.end,
        not_followed_by_shift_types=shift_data.not_followed_by_shift_types or []
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift



@shift_types_router.get("", response_model=List[ShiftTypeResponse])
def get_shift_types(project_id: UUID, db: Session = Depends(get_db)):
    
    shift_types = db.query(ShiftType).filter(ShiftType.project_id == project_id).all()
    return shift_types



@shift_types_router.put("/{shift_id}", response_model=ShiftTypeResponse)
def update_shift_type(project_id: UUID, shift_id: UUID, shift_data: ShiftTypeUpdate, db: Session = Depends(get_db)):
    shift = db.query(ShiftType).filter(
        ShiftType.project_id == project_id,
        ShiftType.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(status_code=404, detail="ShiftType not found")

    shift.name = shift_data.name
    shift.duration = shift_data.duration
    shift.start = shift_data.start
    shift.end = shift_data.end
    shift.not_followed_by_shift_types = shift_data.not_followed_by_shift_types

    db.commit()
    db.refresh(shift)
    return shift



@shift_types_router.delete("/{shift_id}", response_model=dict)
def delete_shift_type(project_id: UUID, shift_id: UUID, db: Session = Depends(get_db)):
    shift = db.query(ShiftType).filter(
        ShiftType.project_id == project_id,
        ShiftType.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(status_code=404, detail="ShiftType not found")

    # remove references in other shift types
    other_shifts = db.query(ShiftType).filter(
        ShiftType.project_id == project_id,
        ShiftType.id != shift_id
    ).all()

    for s in other_shifts:
        if shift.name in s.not_followed_by_shift_types:
            s.not_followed_by_shift_types.remove(shift.name)

    db.delete(shift)
    db.commit()

    return {"detail": "ShiftType deleted successfully"}




shifts_router = APIRouter(tags=["Shifts"], prefix="/projects/{project_id}/shifts")

@shifts_router.get("", response_model=List[ShiftResponse])
def get_shifts(project_id: UUID, db: Session = Depends(get_db)):
    shifts = db.query(Shift).filter(Shift.project_id == project_id).all()
    return shifts



@shifts_router.post("", response_model=ShiftResponse)
def create_shift(project_id: UUID, shift_data: ShiftCreate, db: Session = Depends(get_db)):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_shift = Shift(
        id=shift_data.id,
        uid=shift_data.uid,
        project_id=project_id,
        name=shift_data.name,
        start_time=shift_data.start_time,
        end_time=shift_data.end_time,
        demand=shift_data.demand,
        type=shift_data.type,
        not_followed_by_shift_types=shift_data.not_followed_by_shift_types,
        weight_below_demand=shift_data.weight_below_demand,
        weight_above_demand=shift_data.weight_above_demand
    )

    db.add(new_shift)
    db.commit()
    db.refresh(new_shift)
    return new_shift


@shifts_router.post("/bulk-create", response_model=List[ShiftResponse])
def create_multiple_shifts(
    project_id: UUID,
    data: ShiftBulkCreate,
    db: Session = Depends(get_db)
):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_shifts = []

    for shift_data in data.shifts:
        shift = Shift(
            id=shift_data.id,
            uid=shift_data.uid,
            project_id=project_id,
            name=shift_data.name,
            start_time=shift_data.start_time,
            end_time=shift_data.end_time,
            demand=shift_data.demand,
            type=shift_data.type,
            not_followed_by_shift_types=shift_data.not_followed_by_shift_types,
            weight_below_demand=shift_data.weight_below_demand,
            weight_above_demand=shift_data.weight_above_demand
        )
        new_shifts.append(shift)

    db.add_all(new_shifts)
    db.commit()

    for shift in new_shifts:
        db.refresh(shift)

    return new_shifts


@shifts_router.put("/{shift_id}", response_model=ShiftResponse)
def update_shift(project_id: UUID, shift_id: UUID, shift_data: ShiftUpdate, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(
        Shift.project_id == project_id,
        Shift.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    shift.name = shift_data.name
    shift.start_time = shift_data.start_time
    shift.end_time = shift_data.end_time
    shift.demand = shift_data.demand
    shift.type = shift_data.type
    shift.not_followed_by_shift_types = shift_data.not_followed_by_shift_types
    shift.weight_below_demand = shift_data.weight_below_demand
    shift.weight_above_demand = shift_data.weight_above_demand

    db.commit()
    db.refresh(shift)
    return shift


@shifts_router.delete("/{shift_id}", response_model=dict)
def delete_shift(project_id: UUID, shift_id: UUID, db: Session = Depends(get_db)):
    shift = db.query(Shift).filter(
        Shift.project_id == project_id,
        Shift.id == shift_id
    ).first()

    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")


    db.delete(shift)
    db.commit()

    return {"detail": "Shift deleted successfully"}


@shifts_router.post("/bulk-delete", response_model=dict)
def delete_multiple_shifts(
    project_id: UUID,
    data: ShiftBulkDelete,
    db: Session = Depends(get_db)
):
    shifts = db.query(Shift).filter(
        Shift.project_id == project_id,
        Shift.id.in_(data.shift_ids)
    ).all()

    for shift in shifts:
        db.delete(shift)

    db.commit()

    return {"detail": f"{len(shifts)} shifts deleted successfully"}


nurses_router = APIRouter(tags=["Nurses"], prefix="/projects/{project_id}/nurses")

@nurses_router.post("", response_model=NurseResponse)
def create_nurse(
    project_id: UUID,
    nurse_data: NurseCreate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    nurse = Nurse(
        **nurse_data.model_dump(),
        project_id=project_id,
    )

    db.add(nurse)
    db.commit()
    db.refresh(nurse)

    return nurse


@nurses_router.get("", response_model=list[NurseResponse])
def list_project_nurses(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    return db.query(Nurse).filter(Nurse.project_id == project_id).all()



@nurses_router.get("/{nurse_id}", response_model=NurseResponse)
def get_nurse(
    project_id: UUID,
    nurse_id: UUID,
    db: Session = Depends(get_db),
):
    nurse = (
        db.query(Nurse)
        .filter(Nurse.id == nurse_id, Nurse.project_id == project_id)
        .first()
    )

    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found")

    return nurse


@nurses_router.delete("/{nurse_id}")
def delete_nurse(
    project_id: UUID,
    nurse_id: UUID,
    db: Session = Depends(get_db),
):
    nurse = (
        db.query(Nurse)
        .filter(Nurse.id == nurse_id, Nurse.project_id == project_id)
        .first()
    )

    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found in this project")

    db.delete(nurse)
    db.commit()


@nurses_router.put("/{nurse_id}", response_model=NurseResponse)
def update_nurse(
    project_id: UUID,
    nurse_id: UUID,
    nurse_update: NurseUpdate,
    db: Session = Depends(get_db),
):

    nurse = (
        db.query(Nurse)
        .filter(Nurse.id == nurse_id, Nurse.project_id == project_id)
        .first()
    )

    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse not found in this project")


    for key, value in nurse_update.model_dump().items():
        setattr(nurse, key, value)

    db.commit()
    db.refresh(nurse)

    return nurse


solutions_router = APIRouter(tags=["Solutions"], prefix="/projects/{project_id}/solutions")

@solutions_router.get("", response_model=List[SolutionEntryResponse])
def get_solutions(project_id: UUID, db: Session = Depends(get_db)):
    solutions = db.query(SolutionEntry).filter(
        SolutionEntry.project_id == project_id
    ).all()

    return solutions

@solutions_router.get("/{solution_id}", response_model=SolutionEntryResponse)
def get_solution(project_id: UUID, solution_id: UUID, db: Session = Depends(get_db)):
    solution = db.query(SolutionEntry).filter(
        SolutionEntry.project_id == project_id,
        SolutionEntry.solutionId == solution_id
    ).first()

    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")

    return solution

@solutions_router.post("", response_model=SolutionEntryResponse)
def create_solution(
    project_id: UUID,
    data: SolutionEntryCreate,
    db: Session = Depends(get_db)
):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_solution = SolutionEntry(
        project_id=project_id,
        solutionId=data.solutionId,
        solution_name=data.solution_name,
        solution=data.solution,
        solver=data.solver,
        return_status=data.return_status
    )

    db.add(new_solution)
    db.commit()
    db.refresh(new_solution)

    return new_solution

@solutions_router.put("/{solution_id}", response_model=SolutionEntryResponse)
def update_solution(
    project_id: UUID,
    solution_id: UUID,
    data: SolutionEntryUpdate,
    db: Session = Depends(get_db)
):
    solution = db.query(SolutionEntry).filter(
        SolutionEntry.project_id == project_id,
        SolutionEntry.solutionId == solution_id
    ).first()

    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")

    solution.solution_name = data.solution_name
    solution.solution = data.solution
    solution.solver = data.solver
    solution.return_status = data.return_status

    db.commit()
    db.refresh(solution)

    return solution

@solutions_router.delete("/{solution_id}", response_model=dict)
def delete_solution(project_id: UUID, solution_id: UUID, db: Session = Depends(get_db)):
    solution = db.query(SolutionEntry).filter(
        SolutionEntry.project_id == project_id,
        SolutionEntry.solutionId == solution_id
    ).first()

    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")

    db.delete(solution)
    db.commit()

    return {"detail": "Solution deleted successfully"}


Base.metadata.create_all(bind=engine) # for dev-purposes, change this later
app.include_router(nurse_rostering_solver_v0_router, prefix="/nurse_rostering_solver/v0")
app.include_router(projects_router, prefix="/nurse_rostering_solver/v0")
app.include_router(shift_types_router, prefix="/nurse_rostering_solver/v0")
app.include_router(shifts_router, prefix="/nurse_rostering_solver/v0")
app.include_router(nurses_router, prefix="/nurse_rostering_solver/v0")
app.include_router(solutions_router, prefix="/nurse_rostering_solver/v0")