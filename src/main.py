"""
FastAPI application entrypoint for the Cis-lunar Fuel Depot planning system.
Includes CORS middleware, Russian localized exception handlers, and API router mounting.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.routes import router as api_router

app = FastAPI(
    title="Цислунарный топливный космоконтур 2035 — API",
    description=(
        "Автономное расчётное ядро и сценарный симулятор поставок топлива на цислунарный "
        "орбитальный топливный узел (ОТУ) на 2035–2040 годы. КосмоХакатон 2026."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. CORS configuration for localhost web dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8501",  # Streamlit default port
        "http://127.0.0.1:8501",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 2. Localized exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Translates raw Pydantic validation errors into clear Russian explanations.
    """
    errors_translated = []
    for err in exc.errors():
        field_path = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "")
        
        # Russian translations for typical validation traps
        if "greater than or equal to" in msg:
            msg_ru = f"Значение поля '{field_path}' должно быть больше или равно допустимому минимуму."
        elif "less than or equal to" in msg:
            msg_ru = f"Значение поля '{field_path}' превышает максимально допустимый предел."
        elif "cannot exceed" in msg or "не может превышать" in msg:
            msg_ru = msg
        elif "Input should be" in msg:
            msg_ru = f"Некорректный формат данных в поле '{field_path}': {msg}"
        else:
            msg_ru = f"Ошибка в поле '{field_path}': {msg}"

        errors_translated.append({
            "field": field_path,
            "message": msg_ru,
            "type": err.get("type", "value_error"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error_type": "ValidationError",
            "message": "Обнаружены ошибки в параметрах запроса оператора.",
            "details": errors_translated,
        },
    )


# 3. Mount API endpoints
app.include_router(api_router)


@app.get("/", tags=["System"])
def root():
    return {
        "system": "Топливный космоконтур 2035",
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "documentation": "/docs",
        "api_v1_prefix": "/api/v1",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "engine": "READY"}


# 4. Mount frontend static files if built
import os
from fastapi.staticfiles import StaticFiles

frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    # Mount static assets under /assets and fallback to index.html
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    from fastapi.responses import FileResponse
    @app.get("/app", tags=["Frontend"])
    def get_frontend_app():
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
