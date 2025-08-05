from fastapi import APIRouter
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

@router.post("/scan", response_model=ScanResponse)
def run_scan(request: ScanRequest):
    try:
        domain = request.domain
        scans = request.scans or ["all"]

        response_data = {"domain": domain}
        results_for_file = {"domain": domain}
        output_dir = config.get("output_dir", "reports")
        os.makedirs(output_dir, exist_ok=True)

        # ---------- Subdomain Enumeration ----------
        subs = []
        if "subdomain" in scans or "all" in scans:
            subs, sub_errors = subdomain.discover(
                domain, config.get("wordlist", "wordlists/subdomains.txt")
            )
            response_data["subdomain_result"] = SubdomainResult(
                subdomains=subs,
                errors=wrap_errors(sub_errors) if sub_errors else None
            )
            results_for_file["subdomains"] = subs
            results_for_file["subdomain_errors"] = sub_errors

        # ---------- Live Host Probing ----------
        live = []
        if "probe" in scans or "all" in scans:
            live, probe_errors = probe.check_live(
                subs, config.get("max_threads", 20)
            )
            response_data["probe_result"] = ProbeResult(
                live_hosts=live,
                errors=wrap_errors(probe_errors) if probe_errors else None
            )
            results_for_file["live_hosts"] = live
            results_for_file["probe_errors"] = probe_errors

        # ---------- Handle case of no live hosts ----------
        if not live:
            note = "No live hosts found. Skipping technology and vulnerability scans."
            response_data["note"] = note
            results_for_file["note"] = note
        else:
            live_urls = [host["url"] for host in live]

            # ---------- Technology Detection ----------
            if "techdetect" in scans or "all" in scans:
                techs_raw, tech_errors = techdetect.detect(live_urls)

                techs_parsed = {
                    url: TechnologyDetails(
                        status_code=data.get("status_code", 0),
                        response_headers=[f"{k}: {v}" for k, v in data.get("headers", {}).items()],
                        detected_technologies=data.get("detected_technologies", [])
                    )
                    for url, data in techs_raw.items()
                }

                response_data["techdetect_result"] = TechDetectResult(
                    technologies=techs_parsed,
                    errors=wrap_errors(tech_errors) if tech_errors else None
                )
                results_for_file["technologies"] = techs_raw
                results_for_file["techdetect_errors"] = tech_errors

            # ---------- Vulnerability Scan ----------
            if "vulnscan" in scans or "all" in scans:
                https_only = [url for url in live_urls if url.startswith("https://")]
                if https_only:
                    vulns, vuln_errors = vulnscan.scan_with_nuclei(
                        https_only, config_path="config.yaml"
                    )
                    response_data["vulnscan_result"] = VulnScanResult(
                        vulnerabilities=vulns,
                        errors=wrap_errors(vuln_errors) if vuln_errors else None
                    )
                    results_for_file["vulnerabilities"] = vulns
                    results_for_file["vulnscan_errors"] = vuln_errors
                else:
                    note = "No HTTPS targets found to scan."
                    response_data["vulnscan_note"] = note
                    results_for_file["vulnscan_note"] = note

        # ---------- Save Results ----------
        save_results(results_for_file, output_dir=output_dir)

        return ScanResponse(**response_data)

    except Exception as e:
        print(f"[!] Unhandled exception during scan: {e}")
        raise e
