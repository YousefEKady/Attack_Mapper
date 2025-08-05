from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import urllib3
import time
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_response(response):
    headers = response.headers
    detected = []

    # Server Info
    if "Server" in headers:
        detected.append(f"Server: {headers['Server']}")
    if "X-Powered-By" in headers:
        detected.append(f"X-Powered-By: {headers['X-Powered-By']}")

    # Cookie-based Detection
    set_cookie = (headers.get("Set-Cookie") or "").lower()
    if "phpsessid" in set_cookie:
        detected.append("Technology: PHP")
    if "laravel_session" in set_cookie:
        detected.append("Technology: Laravel")
    if "asp.net" in set_cookie:
        detected.append("Technology: ASP.NET")

    # Body Content Detection
    response.encoding = response.apparent_encoding
    body = response.text.lower()
    if "wordpress" in body:
        detected.append("Technology: WordPress")
    if "django" in body:
        detected.append("Technology: Django")

    # JS Library Detection from <script src="">
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        scripts = [s.get("src", "").lower() for s in soup.find_all("script") if s.get("src")]
        if any("jquery" in s for s in scripts):
            detected.append("JS Library: jQuery")
        if any("react" in s for s in scripts):
            detected.append("JS Library: React")
        if any("vue" in s for s in scripts):
            detected.append("JS Library: Vue.js")
    except Exception as e:
        detected.append(f"HTML parse error: {e}")

    return detected if detected else ["Unknown"]

def detect_single(url, retries=2):
    for attempt in range(retries):
        try:
            start = time.time()
            response = requests.get(url, timeout=5, verify=False)
            elapsed = round((time.time() - start) * 1000, 2)

            if response.status_code >= 400:
                return url, {
                    "status_code": response.status_code,
                    "detected_technologies": ["HTTP error"]
                }, f"{url} returned status {response.status_code}"

            if len(response.text) > 2_000_000:
                return url, {
                    "status_code": response.status_code,
                    "detected_technologies": ["Response too large"]
                }, f"{url} response too large"

            detected = analyze_response(response)
            return url, {
                "status_code": response.status_code,
                "response_time_ms": elapsed,
                "headers": dict(response.headers),
                "detected_technologies": detected
            }, None

        except requests.exceptions.SSLError:
            return url, {"detected_technologies": ["SSL Error"]}, f"{url} SSL handshake failed"
        except requests.exceptions.Timeout:
            return url, {"detected_technologies": ["Timeout"]}, f"{url} timed out"
        except requests.exceptions.ConnectionError:
            return url, {"detected_technologies": ["Connection Error"]}, f"{url} connection error"
        except requests.exceptions.RequestException as e:
            if attempt == retries - 1:
                return url, {"detected_technologies": ["Unreachable"]}, f"{url} unreachable: {e}"
            time.sleep(1)
        except Exception as e:
            return url, {"detected_technologies": ["Unexpected Error"]}, f"{url} unexpected error: {e}"

    return url, {"detected_technologies": ["Unreachable"]}, f"{url} unreachable after retries"

def detect(hosts, retries=2, max_threads=15):
    tech_info = {}
    errors = []

    urls = []
    for h in hosts:
        if isinstance(h, dict) and "url" in h:
            urls.append(h["url"])
        elif isinstance(h, str):
            urls.append(h)

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(detect_single, url, retries): url for url in urls}

        for future in as_completed(futures):
            try:
                url, result, error = future.result()
                tech_info[url] = result
                if error:
                    errors.append(f"[!] {error}")
            except Exception as e:
                errors.append(f"[!] Error while detecting: {e}")

    return tech_info, errors
