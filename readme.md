# AttackMapper

**AttackMapper** is a modular and extensible attack surface discovery and vulnerability scanning tool.  
It automates:

- Subdomain enumeration  
- Live host probing  
- Technology fingerprinting  
- Vulnerability scanning via [Nuclei](https://github.com/projectdiscovery/nuclei)  
- Result visualization through a simple web-based UI

---

## Features

- Subdomain discovery  
- Live host detection  
- Technology fingerprinting (status, headers, tech stack)  
- Vulnerability scanning with Nuclei  
- Clean JSON report generation  
- REST API via FastAPI  
- Web UI with dynamic analytics and visual charts  
- Configurable via `config.yaml`

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

Run the backend API
```shell
uvicorn api_main:app --reload
```
This will start the FastAPI backend at: http://localhost:8000

---

## Output

Scan results include:

- Discovered subdomains
- Live hosts (status, response time)
- Technology stack per host
- Vulnerabilities grouped by severity
- Visual charts: bar graphs for vulnerability severity

All results are stored in:
```
reports/<domain>.json
```

---
