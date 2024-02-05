from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.task_scheduler as scheduler
from src.api.v1 import register_routes
from src.config import config
from src.database import database
from src.dex import data_manager
from src.middlewares import register_middlewares
from src.utils.logger import init_logger

init_logger()

app = FastAPI()


def init_repeated_tasks():
    scheduler.add_interval_task(data_manager.update_assets, 60 * 10)
    scheduler.add_interval_task(data_manager.update_pools, 60 * 10)
    scheduler.add_interval_task(data_manager.update_swap_transactions, 60 * 2)


async def startup():
    await database.init_database()
    init_repeated_tasks()


app.add_event_handler("startup", startup)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.server.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
register_middlewares(app)

register_routes(app)
