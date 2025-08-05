import json
import os
from datetime import datetime

def save_results(data, output_dir="reports"):
    """
    Save results to a JSON file with a timestamped name.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{data.get('domain', 'output')}_{timestamp}.json"
        file_path = os.path.join(output_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"\n[OK] Results saved to {file_path}\n")
    except Exception as e:
        print(f"[-] Failed to save results: {e}")

def load_results(filename, output_dir="reports"):
    """
    Load results from a JSON report.
    """
    file_path = os.path.join(output_dir, filename)

    if not filename.lower().endswith(".json"):
        print("[!] Warning: File does not have a .json extension")

    if not os.path.exists(file_path):
        print(f"[-] Report file not found: {file_path}")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"[-] Failed to load results: {e}")
        return {}

def print_results(data):
    """
    Custom pretty printer for attack surface data.
    """
    print("\n========== ATTACK SURFACE SUMMARY ==========\n")

    # Subdomains
    subdomains = data.get("subdomains", [])
    print(f"[+] Subdomains Found: {len(subdomains)}")
    for sub in subdomains:
        print(f"    - {sub}")

    # Live Hosts
    live_hosts = data.get("live_hosts", [])
    print(f"\n[+] Live Hosts: {len(live_hosts)}")
    for host in live_hosts:
        url = host.get("url")
        status = host.get("status")
        print(f"    - {url} ({status})")

    # Technologies
    technologies = data.get("technologies", {})
    print(f"\n[+] Detected Technologies ({len(technologies)} hosts):")
    for url, info in technologies.items():
        techs = info.get("detected_technologies", [])
        print(f"    - {url}")
        for tech in techs:
            print(f"        • {tech}")

    print("\n============================================\n")