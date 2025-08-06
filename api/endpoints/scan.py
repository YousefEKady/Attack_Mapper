from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
import os

from scanner import subdomain, probe, techdetect, vulnscan
from utils.config import load_config
from utils.output import save_results

from api.models.request_models import ScanRequest
from api.models.response_models import (
    ScanResponse,
    SubdomainResult,
    ProbeResult,
    TechDetectResult,
    VulnScanResult,
    ErrorDetail,
    TechnologyDetails
)

router = APIRouter()
config = load_config("config.yaml")

def wrap_errors(errors: List[str]) -> List[ErrorDetail]:
    return [ErrorDetail(message=e) for e in errors]

@router.post("/scan")  # Removed response_model to allow flexible JSON response
def run_scan(request: ScanRequest):
    try:
        domain = request.domain
        scans = request.scans or ["all"]

        # Use the structure that matches your frontend expectations
        response_data = {
            "domain": domain,
            "subdomains": [],
            "subdomain_errors": [],
            "live_hosts": [],
            "probe_errors": [],
            "technologies": {},
            "techdetect_errors": [],
            "vulnerabilities": {},
            "vulnscan_errors": []
        }
        
        results_for_file = {"domain": domain}
        output_dir = config.get("output_dir", "reports")
        os.makedirs(output_dir, exist_ok=True)

        subs = []
        if "subdomain" in scans or "all" in scans:
            subs, sub_errors = subdomain.discover(
                domain, config.get("wordlist", "wordlists/subdomains.txt")
            )
            # Direct assignment to match frontend expectations
            response_data["subdomains"] = subs
            response_data["subdomain_errors"] = sub_errors or []
            
            results_for_file["subdomains"] = subs
            results_for_file["subdomain_errors"] = sub_errors

        live = []
        if "probe" in scans or "all" in scans:
            live, probe_errors = probe.check_live(
                subs, config.get("max_threads", 20)
            )
            # Direct assignment to match frontend expectations
            response_data["live_hosts"] = live
            response_data["probe_errors"] = probe_errors or []
            
            results_for_file["live_hosts"] = live
            results_for_file["probe_errors"] = probe_errors

        if not live:
            note = "No live hosts found. Skipping technology and vulnerability scans."
            response_data["note"] = note
            results_for_file["note"] = note
        else:
            live_urls = [host["url"] for host in live]

            if "techdetect" in scans or "all" in scans:
                techs_raw, tech_errors = techdetect.detect(live_urls)
                
                # Keep the raw structure that matches your JSON sample
                response_data["technologies"] = techs_raw
                response_data["techdetect_errors"] = tech_errors or []
                
                results_for_file["technologies"] = techs_raw
                results_for_file["techdetect_errors"] = tech_errors

            if "vulnscan" in scans or "all" in scans:
                https_only = [url for url in live_urls if url.startswith("https://")]
                if https_only:
                    vulns, vuln_errors = vulnscan.scan_with_nuclei(
                        https_only, config_path="config.yaml"
                    )

                    # Keep the nested structure that matches your JSON sample
                    response_data["vulnerabilities"] = vulns
                    response_data["vulnscan_errors"] = vuln_errors or []
                    
                    results_for_file["vulnerabilities"] = vulns
                    results_for_file["vulnscan_errors"] = vuln_errors
                else:
                    note = "No HTTPS targets found to scan."
                    response_data["vulnscan_note"] = note
                    results_for_file["vulnscan_note"] = note

        # Save results to file
        save_results(results_for_file, output_dir=output_dir)

        # Return JSON response directly to match frontend expectations
        return JSONResponse(
            content=response_data,
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        print(f"[!] Unhandled exception during scan: {e}")
        return JSONResponse(
            content={"error": f"Scan failed: {str(e)}"},
            status_code=500,
            headers={"Content-Type": "application/json"}
        )