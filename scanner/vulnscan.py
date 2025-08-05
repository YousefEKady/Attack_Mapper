import subprocess
import os
import time
import re
import yaml

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
    raw_output_file = os.path.join(output_dir, f"nuclei_{safe_name}.txt")
    stderr_file = os.path.join(output_dir, f"nuclei_{safe_name}_error.log")
    findings = []
    error_msg = None

    cmd = [
        nuclei_path,
        "-u", url,
        "-silent",
        "-severity", severity,
    ]

    if templates and os.path.exists(templates):
        cmd += ["-t", templates]
    else:
        return url, {"error": f"[!] Templates path invalid: {templates}"}, f"[!] Invalid templates path: {templates}"

    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        with open(raw_output_file, "w", encoding="utf-8") as out_file:
            out_file.write(result.stdout)

        if result.stderr.strip():
            with open(stderr_file, "w", encoding="utf-8") as ef:
                ef.write(result.stderr)
            error_msg = f"[!] STDERR for {url}: {result.stderr.strip().splitlines()[0]} (see log)"

        for line in result.stdout.strip().splitlines():
            if line.strip():
                findings.append({"raw_output": line.strip()})

        elapsed = round(time.time() - start_time, 2)
        return url, {
            "scan_time_seconds": elapsed,
            "findings": findings if findings else [{"info": "No vulnerabilities found"}]
        }, error_msg

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

    if not os.path.isfile(nuclei_path):
        msg = f"[!] Nuclei binary not found: {nuclei_path}"
        return {url: {"error": msg} for url in targets}, [msg]

    if not os.path.exists(templates):
        msg = f"[!] Templates path not found: {templates}"
        return {url: {"error": msg} for url in targets}, [msg]

    os.makedirs(output_dir, exist_ok=True)

    for url in targets:
        url, result, err = scan_single(url, dict(config))  # Copy config per target
        results[url] = result
        if err:
            errors.append(err)

    return results, errors
