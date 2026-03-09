# Frontend-Backend Integration Guide

## For Frontend Developers

This guide explains how to integrate your frontend with the backend API after both branches are merged into main.

## Running the Full Stack

### Quickest Way

From the repository root:

```bash
make dev
```

This automatically starts both backend (port 5000) and frontend (port 3000).

## Backend API Details

### Base URL

**Development:** `http://localhost:5000`
**Production:** Set via environment variable

### Available Endpoints

#### 1. Get All Scenarios

```http
GET /api/scenarios
```

**Response:** 200 OK

```json
[
  {
    "id_scenario": 1,
    "action": "GO" | "STOP" | "HUMAN_CONFIRM",
    "confidence": 0.954,
    "reason": "Human-readable explanation in Italian",
    "fused_text": "The normalized sensor reading"
  }
]
```

**Action Types:**
- `GO` - Proceed safely (green indicator)
- `STOP` - Must stop, restriction active (red indicator)
- `HUMAN_CONFIRM` - Low confidence, needs Marco's input (yellow indicator)

#### 2. Health Check

```http
GET /api/health
```

**Response:** 200 OK

```json
{"status": "ok"}
```

## Frontend Integration Steps

### 1. Configure API Base URL

Create a `.env` file in your frontend directory:

**For Vite (React/Vue/Svelte):**

```env
VITE_API_BASE_URL=http://localhost:5000
```

**For Create React App:**

```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

**For Next.js:**

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

### 2. Create API Client

Example TypeScript/JavaScript implementation:

```typescript
// src/api/backend.ts or src/services/api.js

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export interface Scenario {
  id_scenario: number;
  action: 'GO' | 'STOP' | 'HUMAN_CONFIRM';
  confidence: number;
  reason: string;
  fused_text: string;
}

export async function fetchScenarios(): Promise<Scenario[]> {
  const response = await fetch(`${API_BASE}/api/scenarios`);
  
  if (!response.ok) {
    throw new Error(`Backend error: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    console.error('Health check failed:', error);
    return false;
  }
}
```

### 3. Implement Polling (Required)

Per specification, the frontend must poll every 4 seconds:

```typescript
// src/hooks/useScenarios.ts or similar

import { useState, useEffect } from 'react';
import { fetchScenarios, type Scenario } from './api/backend';

export function useScenarios(intervalMs: number = 4000) {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;
    
    const poll = async () => {
      try {
        const data = await fetchScenarios();
        if (isMounted) {
          setScenarios(data);
          setError(null);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };

    // Initial fetch
    poll();

    // Set up polling interval
    const intervalId = setInterval(poll, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [intervalMs]);

  return { scenarios, loading, error };
}
```

### 4. Handle Each Action Type

```typescript
function ScenarioCard({ scenario }: { scenario: Scenario }) {
  const getColor = (action: string) => {
    switch (action) {
      case 'GO': return 'green';
      case 'STOP': return 'red';
      case 'HUMAN_CONFIRM': return 'yellow';
      default: return 'gray';
    }
  };

  const getIcon = (action: string) => {
    switch (action) {
      case 'GO': return '✓';
      case 'STOP': return '✕';
      case 'HUMAN_CONFIRM': return '⚠';
      default: return '?';
    }
  };

  return (
    <div 
      className={`scenario-card ${getColor(scenario.action)}`}
      style={{ 
        backgroundColor: getColor(scenario.action),
        padding: '20px',
        borderRadius: '8px'
      }}
    >
      <div className="icon">{getIcon(scenario.action)}</div>
      <h3>Scenario #{scenario.id_scenario}</h3>
      <h2>{scenario.action}</h2>
      <p>{scenario.reason}</p>
      <small>Confidenza: {(scenario.confidence * 100).toFixed(1)}%</small>
    </div>
  );
}
```

### 5. Implement HUMAN_CONFIRM Timer

Per specification, when action is `HUMAN_CONFIRM`, show a 2-second countdown:

```typescript
function HumanConfirmModal({ scenario, onOverride, onConfirm, onTimeout }) {
  const [timeLeft, setTimeLeft] = useState(2);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeout(); // Auto-STOP after 2 seconds
      return;
    }

    const timer = setTimeout(() => {
      setTimeLeft(timeLeft - 0.1);
    }, 100);

    return () => clearTimeout(timer);
  }, [timeLeft, onTimeout]);

  return (
    <div className="modal-overlay">
      <div className="human-confirm-modal">
        <div className="countdown" style={{ 
          fontSize: '72px',
          color: timeLeft < 1 ? 'red' : 'orange'
        }}>
          {timeLeft.toFixed(1)}s
        </div>
        
        <h2>⚠ CONFERMA RICHIESTA</h2>
        <p>{scenario.reason}</p>
        
        <div className="button-group">
          <button 
            className="btn-override"
            onClick={onOverride}
            style={{ fontSize: '24px', padding: '20px 40px' }}
          >
            OVERRIDE - PROCEDI
          </button>
          
          <button 
            className="btn-confirm"
            onClick={onConfirm}
            style={{ fontSize: '24px', padding: '20px 40px' }}
          >
            CONFERMA - FERMATI
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Testing the Integration

### 1. Start Backend

```bash
make backend-run-api
```

Expected output:
```
 * Running on http://0.0.0.0:5000
```

### 2. Test API Manually

```bash
# Health check
curl http://localhost:5000/api/health

# Get scenarios
curl http://localhost:5000/api/scenarios | jq
```

### 3. Start Frontend

```bash
make frontend-dev
```

### 4. Verify in Browser

1. Open http://localhost:3000
2. Open DevTools → Network tab
3. Verify API calls to `http://localhost:5000/api/scenarios` every 4 seconds
4. Check that CORS headers are present in response

## Common Issues & Solutions

### CORS Errors

**Problem:** `Access to fetch at 'http://localhost:5000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:** The backend already has `flask-cors` configured. If you still see errors:

1. Verify backend is running: `curl http://localhost:5000/api/health`
2. Check that `Flask-CORS` is installed: `pip list | grep Flask-CORS`
3. Restart the backend: `make backend-run-api`

### Connection Refused

**Problem:** `Failed to fetch` or `net::ERR_CONNECTION_REFUSED`

**Solution:**
1. Ensure backend is running on port 5000
2. Check if another process is using port 5000: `lsof -i :5000`
3. Verify API_BASE_URL in frontend `.env` file

### Empty Response

**Problem:** API returns `[]` empty array

**Solution:**
1. Check that `backend/data/input.json` exists and contains valid data
2. Verify file path in backend: `ls -la backend/data/input.json`
3. Check backend logs for parsing errors

### Polling Not Working

**Problem:** Frontend only fetches data once

**Solution:**
1. Verify `setInterval` is not being cleared prematurely
2. Check that component using the hook is not unmounting/remounting
3. Add console.log to verify polling is active:
   ```javascript
   console.log('Polling scenarios...', new Date().toISOString());
   ```

## Production Deployment Checklist

- [ ] Set production `API_BASE_URL` environment variable
- [ ] Build frontend: `make frontend-build`
- [ ] Use production WSGI server for backend (gunicorn)
- [ ] Configure reverse proxy (nginx/Apache) for both services
- [ ] Enable HTTPS with SSL certificate
- [ ] Set up monitoring for both services
- [ ] Configure health check endpoints in load balancer
- [ ] Test CORS with production URLs

## Support

If you encounter issues:

1. Check backend logs
2. Check browser DevTools console
3. Verify network requests in DevTools Network tab
4. Test API endpoints with `curl` or Postman
5. Ask team members or tutors during hackathon
