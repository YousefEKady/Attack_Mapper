import argparse
import os
from scanner import subdomain, probe, techdetect, vulnscan
from utils.output import save_results, print_results
from utils.config import load_config

def run_scan(domain, scans, config, output_file=None):
    results = {"domain": domain}
    output_dir = config.get("output_dir", "reports")
    os.makedirs(output_dir, exist_ok=True)

    subs = []
    if "subdomain" in scans or "all" in scans:
        print("[*] Discovering subdomains...")
        subs, sub_errors = subdomain.discover(domain, config.get("wordlist", "wordlists/subdomains.txt"))
        results["subdomains"] = subs
        if sub_errors:
            print("\n[!] Subdomain Errors:")
            for err in sub_errors:
                print(f"    {err}")

    live = []
    if "probe" in scans or "all" in scans:
        print("\n[*] Checking live hosts...")
        live, probe_errors = probe.check_live(subs, config.get("max_threads", 20))
        results["live_hosts"] = live
        if probe_errors:
            print("\n[!] Probe Errors:")
            for err in probe_errors:
                print(f"    {err}")

    if not live:
        print("\n[!] No live hosts found. Skipping tech/vuln scans.")
    else:
        live_urls = [h["url"] for h in live]

        if "techdetect" in scans or "all" in scans:
            print("\n[*] Detecting technologies...")
            techs, tech_errors = techdetect.detect(live_urls)
            results["technologies"] = techs
            if tech_errors:
                print("\n[!] TechDetect Errors:")
                for err in tech_errors:
                    print(f"    {err}")

        if "vulnscan" in scans or "all" in scans:
            https_only = [url for url in live_urls if url.startswith("https://")]
            if https_only:
                print("\n[*] Scanning for vulnerabilities with nuclei...")
                vulns, vuln_errors = vulnscan.scan_with_nuclei(https_only, config_path="config.yaml")
                results["vulnerabilities"] = vulns
                if vuln_errors:
                    print("\n[!] Vulnerability Scan Errors:")
                    for err in vuln_errors:
                        print(f"    {err}")
            else:
                print("\n[!] No HTTPS hosts found to scan for vulnerabilities.")

    # Save results
    if output_file:
        save_results(results, output_file)
    else:
        save_results(results, output_dir=output_dir)

    print_results(results)

def main():
    parser = argparse.ArgumentParser(description="AttackMapper - Recon & Vulnerability Scanner")
    parser.add_argument("--domain", help="Target domain to scan")
    parser.add_argument("--scan", default="all",
                        help="Comma-separated scan modules: subdomain,probe,techdetect,vulnscan,all")
    parser.add_argument("--output", help="Optional output JSON file")

    args = parser.parse_args()
    config = load_config("config.yaml")

    if args.domain:
        scans = args.scan.lower().split(",")
        run_scan(args.domain, scans, config, args.output)
    else:
        domain = input("Enter target domain: ")
        run_scan(domain, ["all"], config, args.output)

if __name__ == "__main__":
    main()
