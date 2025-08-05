from fastapi import FastAPI
from api.endpoints.scan import router as scan_router
from api.endpoints.status import router as status_router 

app = FastAPI(
    title="Attack Surface Discovery API",
    description="API to discover subdomains, check live hosts, detect technologies, and scan for vulnerabilities",
    version="1.0.0"
)

app.include_router(scan_router, prefix="/api/scan", tags=["Scan"])

app.include_router(status_router, prefix="/api/status", tags=["Status"])

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Attack Surface Discovery API is running"}
