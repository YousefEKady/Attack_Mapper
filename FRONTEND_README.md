# Attack Surface Discovery Scanner - Frontend

A modern, responsive web interface for the Attack Surface Discovery Scanner API.

## Features

✨ **Modern UI/UX**
- Clean, professional design with Bootstrap 5
- Responsive layout that works on all devices
- Smooth animations and transitions
- Intuitive user interface

🔍 **Scan Configuration**
- Domain input with validation
- Checkbox selection for scan types:
  - Subdomain Discovery
  - Live Host Detection
  - Technology Detection
  - Vulnerability Scanning

📊 **Real-time Results**
- Live loading indicators
- Animated counters for statistics
- Detailed result cards for each scan type
- Error handling and display

🎨 **Design Highlights**
- Gradient backgrounds and modern styling
- Bootstrap Icons for visual appeal
- Hover effects and smooth transitions
- Mobile-friendly responsive design

## File Structure

```
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── style.css          # Custom CSS styles
│   └── script.js          # JavaScript functionality
└── api_main.py            # FastAPI application (updated)
```

## Setup and Running

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   uvicorn api_main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the Frontend**
   Open your browser and navigate to: `http://localhost:8000`

## API Integration

The frontend communicates with the FastAPI backend at:
- **Endpoint**: `POST /api/scan/scan`
- **Request Format**:
  ```json
  {
    "domain": "example.com",
    "scans": ["subdomain", "probe", "techdetect", "vulnscan"]
  }
  ```

## Usage

1. **Enter Domain**: Type the target domain (e.g., `example.com`)
2. **Select Scans**: Choose which scan types to run
3. **Start Scan**: Click "Start Scan" to begin the process
4. **View Results**: Results will appear dynamically as they're processed

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Keyboard Shortcuts

- `Ctrl + Enter`: Submit scan form
- `Tab`: Navigate between form elements

## Error Handling

The frontend includes comprehensive error handling:
- Form validation
- Network error detection
- API error display
- Auto-hiding error messages

## Customization

### Styling
- Modify `static/style.css` to change colors, fonts, and layout
- CSS variables are defined in `:root` for easy theming

### Functionality
- Edit `static/script.js` to modify behavior
- The `ScanManager` class handles all API interactions

### Layout
- Update `templates/index.html` for structural changes
- Bootstrap classes provide responsive grid system

## Security Notes

- The frontend is designed for internal/authorized use
- No sensitive data is stored in the browser
- All API calls are made directly to the backend
- Input validation is performed on both client and server

## Performance

- Optimized for fast loading
- Minimal external dependencies
- Efficient DOM manipulation
- Responsive design for all screen sizes