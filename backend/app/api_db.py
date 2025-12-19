
"""
This file contains a proxy class to interact with the database.
We are using Redis as the database for this example, but the implementation
can be easily adapted to other databases, as the proxy class abstracts the
database operations.
"""

import json
from api_models import NurseRosteringJobStatus, NurseRosteringJobRequest
from solver.nurserostering.data_schema import NurseRosteringSolution
from uuid import UUID
import redis
from typing import Optional, List
import logging

class NurseRosteringJobDbConnection:
    def __init__(self, redis_client: redis.Redis, expire_time: int = 24 * 60 * 60):
        """Initialize the Redis connection and expiration time."""
        self._redis = redis_client
        self._expire_time = expire_time
        logging.basicConfig(level=logging.INFO)

    def _get_data(self, key: str) -> Optional[dict]:
        """Get data from Redis by key and parse JSON."""
        try:
            data = self._redis.get(key)
            if data is not None:
                return json.loads(data)
        except redis.RedisError as e:
            logging.error(f"Redis error: {e}")
        return None
    
    def get_request(self, task_id: UUID) -> Optional[NurseRosteringJobRequest]:
        """Retrieve a Nurse Rostering job request by task ID."""
        data = self._get_data(f"request:{task_id}")
        return NurseRosteringJobRequest(**data) if data else None


    def get_status(self, task_id: UUID) -> Optional[NurseRosteringJobStatus]:
        """Retrieve a Nurse Rostering job status by task ID."""
        data = self._get_data(f"status:{task_id}")
        return NurseRosteringJobStatus(**data) if data else None


    def get_solution(self, task_id: UUID) -> Optional[NurseRosteringSolution]:
        """Retrieve a Nurse Rostering solution by task ID."""
        data = self._get_data(f"solution:{task_id}")
        return NurseRosteringSolution(**data) if data else None

    def set_solution(self, task_id: UUID, solution: NurseRosteringSolution) -> None:
        """Set a Nurse Rostering solution in Redis with an expiration time."""
        try:
            self._redis.set(
                f"solution:{task_id}", solution.model_dump_json(), ex=self._expire_time
            )
        except redis.RedisError as e:
            logging.error("Redis error: %s", e)


    def register_job(self, request: NurseRosteringJobRequest) -> NurseRosteringJobStatus:
        """Register a new Nurse Rostering job request and status in Redis."""
        job_status = NurseRosteringJobStatus()
        try:
            pipeline = self._redis.pipeline()
            pipeline.set(
                f"status:{job_status.task_id}",
                job_status.model_dump_json(),
                ex=self._expire_time,
            )
            pipeline.set(
                f"request:{job_status.task_id}",
                request.model_dump_json(),
                ex=self._expire_time,
            )
            pipeline.execute()
        except redis.RedisError as e:
            logging.error("Redis error: %s", e)

        return job_status


    def update_job_status(self, job_status: NurseRosteringJobStatus) -> None:
        """Update the status of an existing Nurse Rostering job."""
        try:
            self._redis.set(
                f"status:{job_status.task_id}",
                job_status.model_dump_json(),
                ex=self._expire_time,
            )
        except redis.RedisError as e:
            logging.error("Redis error: %s", e)


    def list_jobs(self) -> List[NurseRosteringJobStatus]:
        """List all Nurse Rostering job statuses."""
        try:
            status_keys = self._redis.keys("status:*")
            data = self._redis.mget(status_keys)
            return [NurseRosteringJobStatus(**json.loads(status)) for status in data if status]
        except redis.RedisError as e:
            logging.error("Redis error: %s", e)

            return []
        
        
    def delete_job(self, task_id: UUID) -> None:
        """Delete a Nurse Rostering job request, status, and solution from Redis."""
        try:
            pipeline = self._redis.pipeline()
            pipeline.delete(f"status:{task_id}")
            pipeline.delete(f"request:{task_id}")
            pipeline.delete(f"solution:{task_id}")
            pipeline.execute()
        except redis.RedisError as e:
            logging.error("Redis error: %s", e)
