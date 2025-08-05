import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
import time

# Disable SSL warnings (insecure certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probe_url(url, retries=2, timeout=5):
    """
    Attempts to send a GET request to the URL with retries.
    Returns dict with status or error.
    """
    last_error = "Unknown error"

    for attempt in range(retries):
        try:
            start_time = time.time()
            response = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                verify=False
            )
            elapsed = round((time.time() - start_time) * 1000, 2)

            if response.status_code < 400:
                return {
                    "url": url,
                    "status": response.status_code,
                    "response_time_ms": elapsed
                }
            else:
                last_error = f"HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            last_error = "Timeout"
        except requests.exceptions.SSLError:
            last_error = "SSL Error"
        except requests.exceptions.ConnectionError:
            last_error = "Connection Error"
        except requests.exceptions.RequestException as e:
            last_error = str(e)

        time.sleep(0.5)  # brief delay between retries

    return {"url": url, "error": last_error}

def check_live(subdomains, max_threads=20):
    """
    Probes http and https versions of subdomains in parallel.
    Returns a list of live hosts and list of errors.
    """
    live_hosts = []
    errors = []
    urls_to_probe = []

    for sub in subdomains:
        urls_to_probe.append(f"http://{sub}")
        urls_to_probe.append(f"https://{sub}")

    seen = set()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(probe_url, url): url for url in urls_to_probe}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result and "error" not in result:
                    if result["url"] not in seen:
                        seen.add(result["url"])
                        live_hosts.append(result)
                else:
                    errors.append(f"{url} - {result.get('error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"{url} - Exception: {e}")

    return live_hosts, errors
