from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class ErrorDetail(BaseModel):
    message: str

class SubdomainResult(BaseModel):
    subdomains: List[str]
    errors: Optional[List[ErrorDetail]] = None

class ProbeResult(BaseModel):
    live_hosts: List[Dict[str, Any]]
    errors: Optional[List[ErrorDetail]] = None

class TechnologyDetails(BaseModel):
    status_code: int
    response_headers: List[str]
    detected_technologies: List[str]

    model_config = ConfigDict(extra="ignore")

class TechDetectResult(BaseModel):
    technologies: Dict[str, TechnologyDetails]
    errors: Optional[List[ErrorDetail]] = None

class VulnScanResult(BaseModel):
    vulnerabilities: List[Dict[str, Any]]
    errors: Optional[List[ErrorDetail]] = None

class ScanResponse(BaseModel):
    domain: str
    subdomain_result: Optional[SubdomainResult] = None
    probe_result: Optional[ProbeResult] = None
    techdetect_result: Optional[TechDetectResult] = None
    vulnscan_result: Optional[VulnScanResult] = None
    note: Optional[str] = None
    vulnscan_note: Optional[str] = None
