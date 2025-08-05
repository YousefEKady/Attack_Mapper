# AttackMapper

AttackMapper is a modular and extensible attack surface discovery and vulnerability scanning tool. It automates the process of enumerating subdomains, probing live hosts, identifying technologies, and scanning for vulnerabilities using [Nuclei](https://github.com/projectdiscovery/nuclei).

---

## Features

- Subdomain discovery
- Live host detection
- Technology fingerprinting
- Vulnerability scanning with Nuclei
- Configurable settings via `config.yaml`
- JSON report generation

---

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/attackmapper.git
cd attackmapper
```

2. **Install the required Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download and configure [Nuclei](https://github.com/projectdiscovery/nuclei):**
	- Download the Nuclei binary for your OS.
	- Set the path in the `config.yaml` file.

---

## Configuration

Edit the `config.yaml` file to match your environment:

```yaml
nuclei_path: "YOUR-PATH"
templates: "YOUR-PATH"
severity: "medium,high,critical"
output_dir: "reports"
wordlist: wordlists/subdomains.txt
max_threads: 2
concurrency: 2
rate_limit: 5
nuclei_http_timeout: 30
subprocess_timeout: 240
```


---

## Usage

Run from the command line:
```bash
python main.py --domain example.com
```

You can specify scan modules:
```bash
python main.py --domain example.com --scan subdomain,probe,techdetect,vulnscan
```

Optional output file:
```bash
python main.py --domain example.com --output reports/example_output.json
```


---

## Output

Results are printed to the console and saved in the `reports/` directory if an output file is specified. The output includes:

- Discovered subdomains
- Live hosts and their response codes
- Detected technologies per host
- Vulnerability scan results from Nuclei (if applicable)

---
