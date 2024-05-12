from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.chats import chats_router
from backend.routers.users import users_router
from backend.auth import auth_router
from backend.database import EntityNotFoundException, DuplicateEntityException

from contextlib import asynccontextmanager
from backend.database import create_db_and_tables

tags_metadata = [
    {
        "name": "Chats",
        "description": "Routes related to Chats",
    },
    {   
        "name": "Users",
        "description": "Routes related to Users",
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="Pony Express", 
    description="CS4550 - Spring 2024, the University of Utah. By Riley Kraabel.",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # change this as appropriate for your setup
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(EntityNotFoundException)
def handle_entity_not_found(
    _request: Request,
    exception: EntityNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": {
                "type": "entity_not_found",
                "entity_name": exception.entity_name,
                "entity_id": exception.entity_id,
            },
        },
    )

@app.exception_handler(DuplicateEntityException)
def handle_duplicate_entity(
    _request: Request,
    exception: DuplicateEntityException,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "type": "duplicate_entity",
                "entity_name": exception.entity_name,
                "entity_field": exception.entity_field,
                "entity_value": exception.entity_value
            },
        },
    )


@app.get("/", include_in_schema=False)
def default() -> str:
    return HTMLResponse(
        content=f"""
        <html>
            <body>
                <h1>{app.title}</h1>
                <p>{app.description}</p>
                <h2>API docs</h2>
                <ul>
                    <li><a href="/docs">Swagger</a></li>
                    <li><a href="/redoc">ReDoc</a></li>
                </ul>
            </body>
        </html>
        """,
    )