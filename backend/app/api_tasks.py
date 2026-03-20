"""
This file is responsible for running the optimization job in a separate worker.
"""

from api_config import get_db_connection
from api_models import NurseRosteringJobRequest, NurseRosteringJobStatus
from nurse_rostering.solvers.cp_sat.model.solver import NurseRosteringModel as NurseRosteringModelCPSAT
from nurse_rostering.solvers.gurobi.model.solver import NurseRosteringModel as NurseRosteringModelGRB
from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel as NurseRosteringModelHXLY
from nurse_rostering.heuristics.greedy import NurseRosteringGreedyHeuristic
from nurse_rostering.data_schema import SolverFormulation
from datetime import datetime
from uuid import UUID
from api_db import NurseRosteringJobDbConnection
import httpx
import logging


def send_webhook(job_request: NurseRosteringJobRequest, job_status: NurseRosteringJobStatus) -> None:
    if job_request.webhook_url:
        try:
            # Send a POST request to the webhook URL
            response = httpx.post(
                url=f"{job_request.webhook_url}", json=job_status.model_dump_json()
            )
            response.raise_for_status()  # Raise an error for bad responses
        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logging.error(f"An error occurred: {e}")

def run_optimization_job(
    job_id: UUID, db_connection: NurseRosteringJobDbConnection | None = None
) -> None:
    """
    Will fetch the job request from the database, run the optimization algorithm,
    and store the solution back in the database. Finally, it will send a webhook
    to the URL specified in the job. This function may be run on a separate worker,
    which is why we do not pass or return data directly, but rather use the database.
    """
    if db_connection is None:
        db_connection = get_db_connection()

    job_status = db_connection.get_status(job_id)
    job_request = db_connection.get_request(job_id)

    if job_status is None or job_request is None:
        return  # job got deleted
    
    job_status.status = "Running"
    job_status.started_at = datetime.now()
    db_connection.update_job_status(job_status)


    match job_request.solver:
        
        case "gurobi":
            solver = NurseRosteringModelGRB(job_request.nurse_rostering_instance, None) 
        case "hexaly-ip":
            solver = NurseRosteringModelHXLY(job_request.nurse_rostering_instance, None, formulation=SolverFormulation.IP) 
        case "hexaly-set":
            solver = NurseRosteringModelHXLY(job_request.nurse_rostering_instance, None, formulation=SolverFormulation.SET) 
        case "hexaly-table":
            solver = NurseRosteringModelHXLY(job_request.nurse_rostering_instance, None, formulation=SolverFormulation.TABLE) 
        case "cpsat-ip":
            solver = NurseRosteringModelCPSAT(job_request.nurse_rostering_instance, None, formulation=SolverFormulation.IP)
        case "cpsat-automaton":
            solver = NurseRosteringModelCPSAT(job_request.nurse_rostering_instance, None, formulation=SolverFormulation.AUTOMATON)
        case "greedy-heuristic":
            solver = NurseRosteringGreedyHeuristic(job_request.nurse_rostering_instance)
            

    
    solution = solver.solve(
        max_time_in_seconds=job_request.optimization_parameters.timeout,
        meta_param_nurses_at_shifts_forced=job_request.optimization_parameters.nurses_at_shifts_forced
    )

    db_connection.set_solution(job_id, solution)

    job_status.status = "Completed"
    job_status.completed_at = datetime.now()
    db_connection.update_job_status(job_status)

    send_webhook(job_request, job_status)

