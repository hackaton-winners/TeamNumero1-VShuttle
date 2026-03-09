# Hackaton Project

## Automated Backend Setup

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
