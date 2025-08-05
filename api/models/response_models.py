from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ErrorDetail(BaseModel):
    message: str

class SubdomainResult(BaseModel):
    subdomains: List[str]
    errors: Optional[List[ErrorDetail]]

class ProbeResult(BaseModel):
    live_hosts: List[Dict[str, Any]]
    errors: Optional[List[ErrorDetail]]

class TechDetectResult(BaseModel):
    technologies: Dict[str, List[str]]
    errors: Optional[List[ErrorDetail]]

class VulnScanResult(BaseModel):
    vulnerabilities: List[Dict[str, Any]]
    errors: Optional[List[ErrorDetail]]

class ScanResponse(BaseModel):
    domain: str
    subdomains: Optional[List[str]]
    live_hosts: Optional[List[Dict[str, Any]]]
    technologies: Optional[Dict[str, List[str]]]
    vulnerabilities: Optional[List[Dict[str, Any]]]
    subdomain_errors: Optional[List[str]]
    probe_errors: Optional[List[str]]
    techdetect_errors: Optional[List[str]]
    vulnscan_errors: Optional[List[str]]
    note: Optional[str]
    vulnscan_note: Optional[str]
