# Quick Start Guide - V-Shuttle Project

## After Both Branches Are Merged to Main

### One Command to Rule Them All

```bash
make dev
```

That's it! This starts:
- ✅ Backend API on http://localhost:5000
- ✅ Frontend on http://localhost:3000

## Individual Services

### Backend Only

```bash
make backend-run-api
```

### Frontend Only

```bash
make frontend-dev
```

## First Time Setup

### Backend Dependencies

```bash
make backend-install
```

### Frontend Dependencies

```bash
make frontend-install
```

## Testing

```bash
make backend-test
```

## API Endpoints

- `GET http://localhost:5000/api/health` - Health check
- `GET http://localhost:5000/api/scenarios` - Get all decisions

## Expected Response Format

```json
{
  "id_scenario": 1,
  "action": "GO" | "STOP" | "HUMAN_CONFIRM",
  "confidence": 0.954,
  "reason": "Human readable explanation",
  "fused_text": "Normalized sensor text"
}
```

## Frontend Environment Setup

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:5000
```

## Key Requirements

1. **Polling:** Frontend must poll `/api/scenarios` every 4 seconds
2. **Colors:** Green (GO), Red (STOP), Yellow (HUMAN_CONFIRM)
3. **Timer:** 2-second countdown for HUMAN_CONFIRM actions
4. **No crashes:** System must handle the secret test file without errors

## Directory Structure

```
.
├── backend/           # Python Flask API
├── frontend/          # Web Dashboard (after merge)
├── Makefile          # All automation commands
├── README.md         # Full documentation
└── INTEGRATION.md    # Detailed integration guide
```

## Need More Details?

- Full documentation: [README.md](README.md)
- Integration guide: [INTEGRATION.md](INTEGRATION.md)
- Backend structure: [backend/documentazione.md](backend/documentazione.md)

## Common Commands Summary

| Command | What it does |
|---------|-------------|
| `make dev` | Start full stack (backend + frontend) |
| `make backend-install` | Install Python dependencies |
| `make backend-run-api` | Start backend API only |
| `make backend-test` | Run 53 backend tests |
| `make frontend-install` | Install npm dependencies |
| `make frontend-dev` | Start frontend dev server |
| `make frontend-build` | Build frontend for production |
| `make backend-clean` | Remove virtual environment |

## Troubleshooting Quick Fixes

**Port already in use?**
```bash
# Kill process on port 5000
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Backend not responding?**
```bash
curl http://localhost:5000/api/health
```

**Frontend can't connect?**
- Check `frontend/.env` has correct `VITE_API_BASE_URL`
- Verify backend is running with `curl` command above
- Check browser console for CORS errors

## During Final Test (10 min before deadline)

When you receive the secret test file:

1. Replace `backend/data/input.json` with the new file
2. Backend will automatically process it (no restart needed)
3. Frontend will pick up new data on next poll (within 4 seconds)
4. System should handle all scenarios without crashing

---

**Good luck! 🚀**
