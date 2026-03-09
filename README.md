# V-Shuttle Project

Autonomous shuttle decision support system with sensor fusion backend and live dashboard frontend.

## Quick Start (Full Stack)

Once both backend and frontend are merged:

```bash
make dev
```

This starts:
- Backend API on http://localhost:5000
- Frontend on http://localhost:3000

## Backend Setup

Use the root Makefile to create a virtual environment and install backend libraries.

Runtime dependencies only:

make backend-install

Runtime + development dependencies:

make backend-install-dev

Run backend tests:

make backend-test

Clean local virtual environment:

make backend-clean

Notes:
- The virtual environment is created at .venv in the repository root.
- Backend dependencies are read from backend/requirements.txt.
- Development dependencies are read from backend/requirements-dev.txt.

## Frontend <-> Backend Communication

Start the backend API:

make backend-run-api

Default API base URL:

http://localhost:5000

Available endpoints:
- GET /api/health
- GET /api/scenarios

Frontend fetch example:

```js
const API_BASE = "http://localhost:5000";

export async function fetchScenarios() {
	const response = await fetch(`${API_BASE}/api/scenarios`);
	if (!response.ok) {
		throw new Error(`Backend error: ${response.status}`);
	}
	return response.json();
}

export async function pollScenarios(onData, intervalMs = 4000) {
	const tick = async () => {
		try {
			const data = await fetchScenarios();
			onData(data);
		} catch (error) {
			console.error(error);
		}
	};

	await tick();
	return setInterval(tick, intervalMs);
}
```
## Frontend Setup (After Frontend Merge)

Install frontend dependencies:

```bash
make frontend-install
```

Run frontend dev server:

```bash
make frontend-dev
```

### Frontend Environment Configuration

Create `frontend/.env` (or `.env.local`) with:

```env
VITE_API_BASE_URL=http://localhost:5000
# or for React without Vite:
REACT_APP_API_BASE_URL=http://localhost:5000
```

For production deployment, set:

```env
VITE_API_BASE_URL=https://your-backend-domain.com
```

## Full Stack Development Workflow

### Option 1: Single command (recommended)

```bash
make dev
```

### Option 2: Separate terminals

Terminal 1 (Backend):
```bash
make backend-run-api
```

Terminal 2 (Frontend):
```bash
make frontend-dev
```

## API Contract

### GET /api/scenarios

Returns array of scenario decisions:

```json
[
  {
    "id_scenario": 1,
    "action": "GO",
    "confidence": 0.954,
    "reason": "Libero transito - nessun divieto rilevato",
    "fused_text": "GO"
  },
  {
    "id_scenario": 2,
    "action": "STOP",
    "confidence": 0.982,
    "reason": "ZTL attiva - divieto di transito",
    "fused_text": "ZTL"
  },
  {
    "id_scenario": 3,
    "action": "HUMAN_CONFIRM",
    "confidence": 0.410,
    "reason": "Confidenza troppo bassa - richiesta conferma umana",
    "fused_text": "ZTL ORARIO"
  }
]
```

### GET /api/health

Health check endpoint:

```json
{"status": "ok"}
```

## Production Deployment

### Backend

```bash
# Install production dependencies
make backend-install

# Run with production WSGI server (e.g., gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.main:app
```

### Frontend

```bash
# Build for production
make frontend-build

# Serve the build folder (frontend/dist or frontend/build)
# with nginx, Apache, or any static file server
```

## Project Structure

```
.
├── backend/              # Python Flask API
│   ├── main.py          # Entry point with Flask app
│   ├── requirements.txt # Python dependencies
│   ├── data/
│   │   └── input.json   # Sensor scenarios
│   ├── src/             # Core logic modules
│   └── tests/           # Test suite
│
├── frontend/            # (After merge) Web dashboard
│   ├── src/
│   ├── public/
│   └── package.json
│
├── Makefile            # Automation commands
└── README.md           # This file
```

## Development Tips

1. **CORS is enabled** - Frontend can run on different port during development
2. **Hot reload** - Both backend and frontend support live reload
3. **API polling** - Frontend should poll `/api/scenarios` every 4 seconds
4. **Error handling** - Always handle backend connection errors gracefully
5. **Testing** - Run `make backend-test` before committing backend changes