from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.scan import router as scan_router
from api.endpoints.status import router as status_router 

app = FastAPI(
    title="Attack Surface Discovery API",
    description="API to discover subdomains, check live hosts, detect technologies, and scan for vulnerabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(scan_router, prefix="/api/scan", tags=["Scan"])
app.include_router(status_router, prefix="/api/status", tags=["Status"])

@app.get("/")
def read_root():
    return FileResponse("templates/index.html")