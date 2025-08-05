import subprocess
import os
import time
import json
import re
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def sanitize_filename(url):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', url)

def scan_single(url, config):
    nuclei_path = config.get("nuclei_path")
    templates = config.get("templates")
    severity = config.get("severity", "low,medium,high,critical")
    output_dir = config.get("output_dir", "reports")

    safe_name = sanitize_filename(url)
    raw_output_file = os.path.join(output_dir, f"nuclei_{safe_name}.json")
    stderr_file = os.path.join(output_dir, f"nuclei_{safe_name}_error.log")
    findings = []
    error_msg = None

    try:
        cmd = [
            nuclei_path, "-u", url,
            "-silent", "-c", "20", "-rate-limit", "100",
            "-severity", severity, "-json"
        ]

        if templates and os.path.exists(templates):
            cmd.extend(["-t", templates])
        else:
            return url, {"error": f"[!] Templates path not found or invalid: {templates}"}, f"[!] Invalid template path: {templates}"

        start_time = time.time()
        with open(raw_output_file, "w", encoding="utf-8") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=120)

        if result.stderr.strip():
            with open(stderr_file, "w", encoding="utf-8") as ef:
                ef.write(result.stderr)
            error_msg = f"[!] STDERR for {url}: {result.stderr.strip().splitlines()[0]} (See: {stderr_file})"

        if os.path.isfile(raw_output_file):
            with open(raw_output_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        findings.append({
                            "template": data.get("template-id"),
                            "name": data.get("info", {}).get("name"),
                            "severity": data.get("info", {}).get("severity"),
                            "matched": data.get("matched-at")
                        })
                    except json.JSONDecodeError:
                        continue

        elapsed = round(time.time() - start_time, 2)
        return url, {
            "scan_time_seconds": elapsed,
            "findings": findings if findings else []
        }, error_msg

    except subprocess.TimeoutExpired:
        msg = f"[!] Timeout during scan of {url}"
        return url, {"error": msg}, msg
    except Exception as e:
        msg = f"[!] Error scanning {url}: {str(e)}"
        return url, {"error": msg}, msg

def scan_with_nuclei(targets, config_path="config.yaml"):
    results = {}
    errors = []

    try:
        config = load_config(config_path)
    except Exception as e:
        msg = f"[!] Failed to load config: {e}"
        return {url: {"error": msg} for url in targets}, [msg]

    nuclei_path = config.get("nuclei_path")
    templates = config.get("templates")
    output_dir = config.get("output_dir", "reports")
    max_threads = config.get("max_threads", 5)

    if not os.path.isfile(nuclei_path):
        msg = f"[!] Nuclei binary not found at path: {nuclei_path}"
        return {url: {"error": msg} for url in targets}, [msg]

    if templates and not os.path.exists(templates):
        msg = f"[!] Templates folder not found: {templates}"
        return {url: {"error": msg} for url in targets}, [msg]

    os.makedirs(output_dir, exist_ok=True)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(scan_single, url, config) for url in targets]
        for future in as_completed(futures):
            try:
                url, res, err = future.result()
                results[url] = res
                if err:
                    errors.append(err)
            except Exception as e:
                errors.append(f"[!] Unexpected exception: {e}")

    return results, errors
