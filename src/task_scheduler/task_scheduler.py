import asyncio
import logging
from datetime import datetime
from enum import Enum as StrEnum
from typing import Callable

logger = logging.getLogger("scheduler")


class TaskType(StrEnum):
    INTERVAL = "repeating"
    ON_TIME = "on_time"


async def _periodic_scheduler(
    period: float,
    func: Callable,
    *args,
    **kwargs,
):
    # print("Adding task ", func)
    while True:
        # print("Starting task ", func)
        await func(*args, **kwargs)
        await asyncio.sleep(period)


async def _on_time_scheduler(
    start_time: datetime,
    func: Callable,
    *args,
    **kwargs,
):
    start_time = start_time.time()
    while True:
        current_time = datetime.now().time()
        if (
            current_time.hour * 60 * 60
            + current_time.minute * 60
            + current_time.second
        ) - (
            start_time.hour * 60 * 60
            + start_time.minute * 60
            + start_time.second
        ) < 60:
            logger.info("Starting task: %s", func)
            await func(*args, **kwargs)
        await asyncio.sleep(60)


def _add_task(
    func: Callable,
    period: float,
    *args,
    task_type: TaskType = TaskType.INTERVAL,
    **kwargs,
):
    if task_type == TaskType.INTERVAL:
        task = _periodic_scheduler(
            period=period,
            func=func,
            *args,
            **kwargs,
        )
    else:
        task = _on_time_scheduler(
            time=period,
            func=func,
            *args,
            **kwargs,
        )

    loop = asyncio.get_event_loop()
    loop.create_task(task)


def add_interval_task(
    func: Callable,
    period: float,
    *args,
    **kwargs,
):
    _add_task(
        func=func,
        period=period,
        task_type=TaskType.INTERVAL,
        *args,
        **kwargs,
    )


def add_on_time_task(
    func: Callable,
    start_time: datetime,
    *args,
    **kwargs,
):
    _add_task(
        func=func,
        period=start_time,
        task_type=TaskType.ON_TIME,
        *args,
        **kwargs,
    )
