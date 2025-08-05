# Attack Surface Discovery Dashboard

A modern, responsive web dashboard for performing attack surface discovery scans. Built with HTML, CSS, Bootstrap 5, and vanilla JavaScript.

## Features

- **Modern Dark Theme**: Clean, professional dark UI with gradient backgrounds
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Real-time Scanning**: Live API integration with loading states
- **Comprehensive Results**: Displays subdomains, live hosts, technologies, and vulnerabilities
- **Error Handling**: Clear display of scan errors and warnings
- **Developer Friendly**: Expandable raw JSON output for debugging
- **Summary Cards**: Quick overview of scan results with counts and error indicators

## Directory Structure

```
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css       # Custom CSS styling
│   └── js/
│       └── script.js       # JavaScript functionality
└── README.md               # This file
```

## Setup Instructions

### 1. Backend API Requirements

Your backend API should have a POST endpoint at `/api/scan` with the following specification:

**Request:**
```json
{
  "domain": "example.com",
  "scans": ["subdomain", "probe", "techdetect", "vulnscan"]
}
```

**Response:**
```json
{
  "domain": "example.com",
  "subdomains": ["sub1.example.com", "sub2.example.com"],
  "subdomain_errors": [],
  "live_hosts": ["192.168.1.1", "10.0.0.1"],
  "probe_errors": [],
  "technologies": ["Apache", "PHP", "MySQL"],
  "techdetect_errors": [],
  "vulnerabilities": ["CVE-2021-1234", "SQL Injection"],
  "vulnscan_errors": []
}
```

### 2. Serving the Dashboard

#### Option A: Flask/Python Backend
```python
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Your API endpoint
@app.route('/api/scan', methods=['POST'])
def scan():
    # Your scan logic here
    pass

if __name__ == '__main__':
    app.run(debug=True)
```

#### Option B: Express.js/Node.js Backend
```javascript
const express = require('express');
const path = require('path');
const app = express();

app.use('/static', express.static('static'));
app.set('view engine', 'html');
app.set('views', 'templates');

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Your API endpoint
app.post('/api/scan', (req, res) => {
    // Your scan logic here
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
```

#### Option C: Simple HTTP Server (Development)
```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server

# Using PHP
php -S localhost:8000
```

### 3. API Configuration

If your API is not at the same domain as the dashboard, you'll need to update the fetch URL in `static/js/script.js`:

```javascript
// Change this line in static/js/script.js
const response = await fetch('/api/scan', {
    // to your actual API endpoint
    const response = await fetch('https://your-api-domain.com/api/scan', {
```

## Usage

1. **Open the Dashboard**: Navigate to your server's root URL
2. **Enter Domain**: Type the target domain (e.g., `example.com`)
3. **Select Scan Types**: Choose from:
   - All Scans (recommended)
   - Subdomain Discovery
   - Host Probing
   - Technology Detection
   - Vulnerability Scan
4. **Start Scan**: Click the "Start Scan" button
5. **View Results**: Results will appear in organized cards with:
   - Summary statistics
   - Detailed findings for each scan type
   - Error messages (if any)
   - Raw JSON output (expandable)

## Customization

### Styling
- Modify `static/css/style.css` to change colors, fonts, and layout
- The dashboard uses CSS custom properties for easy theming
- Bootstrap 5 classes are used for responsive design

### Functionality
- Edit `static/js/script.js` to modify API calls or add new features
- The code is well-commented and modular for easy extension

### Adding New Scan Types
1. Add new options to the select element in `templates/index.html`
2. Update the `generateSummaryCards` function in `static/js/script.js`
3. Create new update functions for the new scan type
4. Add corresponding result containers to the HTML

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Considerations

- Ensure your backend API implements proper authentication
- Consider rate limiting to prevent abuse
- Validate all input on both frontend and backend
- Use HTTPS in production environments

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if your backend server is running
   - Verify the API endpoint URL in `static/js/script.js`
   - Check browser console for CORS errors

2. **Results Not Displaying**
   - Ensure your API returns the expected JSON format
   - Check browser console for JavaScript errors
   - Verify all required fields are present in the API response

3. **Styling Issues**
   - Ensure Bootstrap CSS is loading correctly
   - Check if `static/css/style.css` is accessible
   - Clear browser cache if changes aren't appearing

4. **Static Files Not Loading**
   - Verify your web server is configured to serve static files
   - Check file paths in `templates/index.html`
   - Ensure proper permissions on static directories

### Debug Mode

To enable debug mode, uncomment the last line in `static/js/script.js`:
```javascript
document.addEventListener('DOMContentLoaded', addExampleData);
```

This will pre-fill the form with example data for testing.

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the dashboard.