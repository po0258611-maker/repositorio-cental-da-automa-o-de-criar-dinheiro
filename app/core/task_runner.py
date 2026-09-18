"""
AME - Durable Task Runner
Database-backed polling worker for the MVP. Tasks survive API restarts because
their state is stored in the Task table.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.core.config import settings
from app.core.database import SyncSessionLocal
from app.models.base import Task
from app.core.observability import logger


class TaskRunner:
    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self.running = False

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._recover_stale_tasks()
        self._task = asyncio.create_task(self._loop())
        logger.info("task_runner_started")

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("task_runner_stopped")

    async def _loop(self) -> None:
        while self.running:
            try:
                processed = await self.run_once()
                if processed == 0:
                    await asyncio.sleep(max(0.25, settings.worker_poll_seconds))
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("task_runner_loop_failed", error=str(exc))
                await asyncio.sleep(max(1.0, settings.worker_poll_seconds))

    async def run_once(self) -> int:
        processed = 0
        for _ in range(max(1, settings.worker_batch_size)):
            task = self._claim_next()
            if not task:
                break
            processed += 1
            await self._execute(task.id)
        return processed

    def _claim_next(self) -> Optional[Task]:
        db = SyncSessionLocal()
        try:
            task = (
                db.query(Task)
                .filter(Task.status == "pending")
                .order_by(Task.priority.asc(), Task.created_at.asc())
                .first()
            )
            if not task:
                return None
            task.status = "running"
            task.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()

    async def _execute(self, task_id: str) -> None:
        db = SyncSessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            agent_name = task.agent_name
            input_data = task.input_data or {}
        finally:
            db.close()

        try:
            from app.agents import AGENTS
            agent = AGENTS.get(agent_name) if agent_name else None
            if agent is None:
                raise RuntimeError(f"Agent not found: {agent_name}")

            result = await agent.run(context=input_data)
            db = SyncSessionLocal()
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.output_data = result
                    task.status = "completed"
                    task.completed_at = datetime.now(timezone.utc)
                    task.updated_at = datetime.now(timezone.utc)
                    db.commit()
            finally:
                db.close()
            logger.info("task_completed", task_id=task_id, agent=agent_name)
        except Exception as exc:
            db = SyncSessionLocal()
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.error = str(exc)[:4000]
                    task.status = "failed"
                    task.updated_at = datetime.now(timezone.utc)
                    db.commit()
            finally:
                db.close()
            logger.error("task_failed", task_id=task_id, error=str(exc))

    def _recover_stale_tasks(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
        db = SyncSessionLocal()
        try:
            stale = (
                db.query(Task)
                .filter(Task.status == "running", Task.updated_at < cutoff)
                .all()
            )
            for task in stale:
                task.status = "pending"
                task.error = "Recovered after stale worker lease"
                task.updated_at = datetime.now(timezone.utc)
            if stale:
                db.commit()
                logger.warning("stale_tasks_recovered", count=len(stale))
        finally:
            db.close()


task_runner = TaskRunner()
