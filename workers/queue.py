"""
Job Queue — Redis-backed with in-memory fallback.
Supports enqueue, dequeue, job status tracking.
"""

import json
import uuid
import logging
import threading
from datetime import datetime
from collections import deque
from config.settings import USE_REDIS, REDIS_URL

logger = logging.getLogger(__name__)

# ── In-memory queue ────────────────────────────────────────────────────────

_queue: deque     = deque()
_jobs: dict       = {}
_lock: threading.Lock = threading.Lock()

STATUS_PENDING    = "pending"
STATUS_RUNNING    = "running"
STATUS_DONE       = "done"
STATUS_FAILED     = "failed"


def _redis_client():
    import redis
    return redis.from_url(REDIS_URL, decode_responses=True)


def enqueue(job_type: str, payload: dict) -> str:
    """Add a job to the queue. Returns job_id."""
    job_id = str(uuid.uuid4())
    job    = {
        "id":         job_id,
        "type":       job_type,
        "payload":    payload,
        "status":     STATUS_PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "result":     None,
        "error":      None,
    }

    if USE_REDIS:
        try:
            r = _redis_client()
            r.lpush("bw_queue", json.dumps(job))
            r.hset("bw_jobs", job_id, json.dumps(job))
            logger.debug(f"Enqueued {job_type} → Redis: {job_id}")
            return job_id
        except Exception as e:
            logger.warning(f"Redis enqueue failed, falling back to memory: {e}")

    with _lock:
        _queue.append(job)
        _jobs[job_id] = job

    logger.debug(f"Enqueued {job_type} → memory: {job_id}")
    return job_id


def dequeue() -> dict | None:
    """Pop next pending job from queue."""
    if USE_REDIS:
        try:
            r   = _redis_client()
            raw = r.rpop("bw_queue")
            if raw:
                job = json.loads(raw)
                job["status"] = STATUS_RUNNING
                r.hset("bw_jobs", job["id"], json.dumps(job))
                return job
            return None
        except Exception as e:
            logger.warning(f"Redis dequeue failed: {e}")

    with _lock:
        if _queue:
            job           = _queue.popleft()
            job["status"] = STATUS_RUNNING
            _jobs[job["id"]] = job
            return job
    return None


def complete_job(job_id: str, result: dict = None):
    """Mark a job as completed."""
    _update_job(job_id, status=STATUS_DONE, result=result)


def fail_job(job_id: str, error: str = ""):
    """Mark a job as failed."""
    _update_job(job_id, status=STATUS_FAILED, error=error)


def get_job(job_id: str) -> dict | None:
    if USE_REDIS:
        try:
            r   = _redis_client()
            raw = r.hget("bw_jobs", job_id)
            return json.loads(raw) if raw else None
        except Exception:
            pass
    with _lock:
        return _jobs.get(job_id)


def queue_size() -> int:
    if USE_REDIS:
        try:
            return _redis_client().llen("bw_queue")
        except Exception:
            pass
    with _lock:
        return len(_queue)


def _update_job(job_id: str, **kwargs):
    if USE_REDIS:
        try:
            r   = _redis_client()
            raw = r.hget("bw_jobs", job_id)
            if raw:
                job = json.loads(raw)
                job.update(kwargs)
                job["updated_at"] = datetime.utcnow().isoformat()
                r.hset("bw_jobs", job_id, json.dumps(job))
                return
        except Exception as e:
            logger.warning(f"Redis job update failed: {e}")

    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(kwargs)
            _jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()
