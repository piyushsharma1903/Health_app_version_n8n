from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.report_routes import router as report_router

app = FastAPI(title="Lab Report API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report_router)
