import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from fastapi.routing import APIRoute

from database import engine, Base # Assuming database.py exists
from routers import users, trades # Assuming routers are created

app = FastAPI()

# Include routes from routers
app.include_router(users.router)
app.include_router(trades.router)

# CORS Configuration
origins = ["*"]  # Replace with your allowed origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Database Initialization
Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get('/health')
def health_check():
    return {"status": "ok"}

# Custom exception handler
@app.exception_handler(Exception)
def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'message': f'Internal Server Error: {str(exc)}'})

# Static file serving
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/{{"file_path:path}}")
    async def serve_frontend(file_path: str):
        if file_path.startswith("api/") or file_path == "":
            return None # Let API routes handle it or serve index.html for root
        static_file = os.path.join("static", file_path)
        if os.path.isfile(static_file):
            return FileResponse(static_file)
        return FileResponse("static/index.html") # SPA routing

# Override default route to use index.html
class SPAStaticRoute(APIRoute):
    async def __call__(self, request: Request):
        if request.url.path.startswith('/api'):
            return await super().__call__(request)
        return FileResponse("static/index.html")

# Start the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
