from fastapi import APIRouter
from typing import List
import os

from scanner import subdomain, probe, techdetect, vulnscan
from utils.config import load_config
from utils.output import save_results

from api.models.request_models import ScanRequest
from api.models.response_models import ScanResponse

router = APIRouter()
config = load_config("config.yaml")

@router.post("/scan", response_model=ScanResponse)
def run_scan(request: ScanRequest):
    domain = request.domain
    scans = request.scans or ["all"]

    results = {"domain": domain}
    output_dir = config.get("output_dir", "reports")
    os.makedirs(output_dir, exist_ok=True)

    subs = []
    if "subdomain" in scans or "all" in scans:
        subs, sub_errors = subdomain.discover(domain, config.get("wordlist", "wordlists/subdomains.txt"))
        results["subdomains"] = subs
        if sub_errors:
            results["subdomain_errors"] = sub_errors

    live = []
    if "probe" in scans or "all" in scans:
        live, probe_errors = probe.check_live(subs, config.get("max_threads", 20))
        results["live_hosts"] = live
        if probe_errors:
            results["probe_errors"] = probe_errors

    if not live:
        results["note"] = "No live hosts found. Skipping technology and vulnerability scans."
    else:
        live_urls = [h["url"] for h in live]

        if "techdetect" in scans or "all" in scans:
            techs, tech_errors = techdetect.detect(live_urls)
            results["technologies"] = techs
            if tech_errors:
                results["techdetect_errors"] = tech_errors

        if "vulnscan" in scans or "all" in scans:
            https_only = [url for url in live_urls if url.startswith("https://")]
            if https_only:
                vulns, vuln_errors = vulnscan.scan_with_nuclei(https_only, config_path="config.yaml")
                results["vulnerabilities"] = vulns
                if vuln_errors:
                    results["vulnscan_errors"] = vuln_errors
            else:
                results["vulnscan_note"] = "No HTTPS targets found to scan."

    save_results(results, output_dir=output_dir)
    return results
