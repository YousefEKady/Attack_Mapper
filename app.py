from flask import Flask, render_template, request, jsonify
import time
import random

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/scan', methods=['POST'])
def scan():
    """Handle scan requests from the frontend"""
    try:
        data = request.get_json()
        domain = data.get('domain')
        scans = data.get('scans', [])
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        # Simulate scan processing time
        time.sleep(2)
        
        # Mock scan results (replace with your actual scan logic)
        results = {
            'domain': domain,
            'subdomains': [
                f'www.{domain}',
                f'api.{domain}',
                f'admin.{domain}',
                f'mail.{domain}',
                f'blog.{domain}'
            ] if 'all' in scans or 'subdomain' in scans else [],
            'subdomain_errors': [],
            'live_hosts': [
                '192.168.1.1',
                '10.0.0.1',
                '172.16.0.1'
            ] if 'all' in scans or 'probe' in scans else [],
            'probe_errors': [],
            'technologies': [
                'Apache/2.4.41',
                'PHP/7.4.3',
                'MySQL/8.0.21',
                'WordPress/5.7.2',
                'jQuery/3.6.0'
            ] if 'all' in scans or 'techdetect' in scans else [],
            'techdetect_errors': [],
            'vulnerabilities': [
                'CVE-2021-1234 - SQL Injection',
                'CVE-2021-5678 - XSS Vulnerability',
                'Weak Password Policy',
                'Missing Security Headers'
            ] if 'all' in scans or 'vulnscan' in scans else [],
            'vulnscan_errors': []
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Attack Surface Discovery Dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    print("API endpoint: http://localhost:5000/api/scan")
    app.run(debug=True, host='0.0.0.0', port=5000)