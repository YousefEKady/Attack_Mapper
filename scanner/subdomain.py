import dns.resolver
import concurrent.futures
import re
import os

def load_wordlist(path):
    if not os.path.exists(path):
        print(f"[!] Wordlist file '{path}' not found. Using default list.")
        return ["www", "mail", "test", "admin", "ftp", "dev", "staging", "api"]
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [w.strip() for w in f if w.strip()]

def is_valid_domain(domain):
    pattern = r"^(?!-)(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, domain) is not None

def resolve_subdomain(subdomain, record_types=("A",)):
    found_records = []
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(subdomain, rtype, lifetime=3)
            for answer in answers:
                found_records.append(f"{rtype}: {answer.to_text()}")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer,
                dns.resolver.LifetimeTimeout, dns.resolver.NoNameservers):
            continue
        except Exception as e:
            found_records.append(f"{rtype} ERROR: {e}")
    if found_records:
        return {"subdomain": subdomain, "records": found_records}
    return None

def discover(domain, wordlist_file="wordlists/subdomains.txt", record_types=("A", "AAAA", "CNAME", "MX")):
    if not is_valid_domain(domain):
        print(f"[!] Invalid domain: {domain}")
        return [], []

    words = load_wordlist(wordlist_file)
    subdomains_found = []
    errors = []
    seen = set()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {
                executor.submit(resolve_subdomain, f"{word}.{domain}", record_types): f"{word}.{domain}"
                for word in words
            }

            for future in concurrent.futures.as_completed(futures):
                sub = futures[future]
                try:
                    result = future.result()
                    if result and result["subdomain"] not in seen:
                        seen.add(result["subdomain"])
                        subdomains_found.append(result["subdomain"])
                except Exception as e:
                    errors.append(f"{sub} - Exception: {e}")
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
        return subdomains_found, errors

    return subdomains_found, errors
